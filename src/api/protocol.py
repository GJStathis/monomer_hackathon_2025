"""
Protocol API endpoints for generating scientific protocols.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.schema.protocol import (
    GenerateProtocolResponse, 
    ReagentItem,
    OrganismListResponse,
    ProtocolTrackersResponse,
    ProtocolDetailResponse,
    ProtocolTrackerItem
)
from src.services.blast_service import BlastAPI
from src.agents.future_house_agent import FutureHouseAPI
from src.agents.basic_research_agent import BasicResearchAgent
from src.agents.protocol_agent import ProtocolAgent
from src.repositories.protocol_tracker_repository import ProtocolTrackerRepository
from src.repositories.protocol_repository import ProtocolRepository

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Database setup
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@router.get("/generate_protocol", response_model=GenerateProtocolResponse)
async def generate_protocol(
    organism_name: str = Query(..., description="Name of the organism to generate protocol for"),
    absorbance_csv_path: Optional[str] = Query(None, description="Optional path to absorbance data CSV"),
    research_agent: str = Query("basic", description="Research agent to use: 'basic' (OpenAI o1) or 'futurehouse'")
):
    """
    Generate a scientific protocol for growing the specified organism.
    
    This endpoint orchestrates:
    1. BLAST API to find related organisms
    2. Research Agent (FutureHouse or Basic) to gather scientific literature
    3. Protocol Agent to generate reagent recommendations
    
    Args:
        organism_name: Name of the organism to generate protocol for
        absorbance_csv_path: Optional path to absorbance data CSV file
        research_agent: Research agent to use ('basic' for OpenAI o1-mini, 'futurehouse' for FutureHouse API)
        
    Returns:
        GenerateProtocolResponse with organism info, related organisms, and reagent list
    """
    try:
        logger.info(f"Starting protocol generation for organism: {organism_name}")
        
        # Step 1: Use BlastAPI to find related organisms
        logger.info("Step 1: Finding related organisms via BLAST...")
        blast_api = BlastAPI()
        related_organisms = blast_api.get_top_10_related_organisms(organism_name)
        logger.info(f"Found {len(related_organisms)} related organisms: {related_organisms}")
        
        # Step 2: Use Research Agent to gather literature for related organisms
        logger.info(f"Step 2: Gathering scientific literature via {research_agent} agent...")
        
        # Add the original organism to the list
        all_organisms = [organism_name] + related_organisms
        logger.info(f"Querying literature for {len(all_organisms)} organisms")
        
        # Choose the appropriate research agent
        if research_agent.lower() == "futurehouse":
            agent = FutureHouseAPI()
        else:  # default to basic
            agent = BasicResearchAgent(model="o1-mini")
        
        # Run the task and get the literature content (returns string directly)
        literature_content = agent.run_task(all_organisms)
        
        logger.info(f"Gathered literature content ({len(literature_content)} characters)")
        
        # Step 3: Use ProtocolAgent to generate the protocol
        logger.info("Step 3: Generating protocol using AI agent...")
        protocol_agent = ProtocolAgent(organism_name=organism_name)
        
        # Generate protocol DataFrame
        protocol_df = protocol_agent.generate_protocol(
            literature=literature_content,
            absorbance_csv_path=absorbance_csv_path
        )
        
        logger.info(f"Generated protocol with {len(protocol_df)} reagents")
        
        # Step 4: Convert DataFrame to response schema
        reagents = []
        for _, row in protocol_df.iterrows():
            reagent = ReagentItem(
                name=row['name'],
                concentration=row.get('concentration', None) if pd.notna(row.get('concentration', None)) else None,
                unit=row['unit']
            )
            reagents.append(reagent)
        
        # Create response
        response = GenerateProtocolResponse(
            organism_name=organism_name,
            related_organisms=related_organisms,
            reagents=reagents,
            message=f"Successfully generated protocol for {organism_name} with {len(reagents)} reagents"
        )
        
        logger.info("Protocol generation completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error generating protocol: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate protocol: {str(e)}"
        )


@router.get("/health")
async def protocol_health():
    """Health check for protocol service."""
    return {
        "service": "protocol",
        "status": "healthy"
    }


@router.get("/organisms", response_model=OrganismListResponse)
async def get_organisms():
    """
    Get a distinct list of all organisms that have protocols.
    
    Returns:
        OrganismListResponse with list of organism names
    """
    session = SessionLocal()
    try:
        tracker_repo = ProtocolTrackerRepository(session)
        organisms = tracker_repo.get_distinct_organisms()
        return OrganismListResponse(organisms=organisms)
    except Exception as e:
        logger.error(f"Error retrieving organisms: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve organisms: {str(e)}")
    finally:
        session.close()


@router.get("/protocols/by-organism", response_model=ProtocolTrackersResponse)
async def get_protocols_by_organism(
    organism: str = Query(..., description="Organism name to filter protocols")
):
    """
    Get all protocol trackers for a specific organism.
    
    Args:
        organism: Name of the organism
        
    Returns:
        ProtocolTrackersResponse with list of protocol trackers
    """
    session = SessionLocal()
    try:
        tracker_repo = ProtocolTrackerRepository(session)
        trackers = tracker_repo.get_by_organism(organism)
        
        tracker_items = [
            ProtocolTrackerItem(
                id=tracker.id,
                target_organism=tracker.target_organism,
                created_at=tracker.created_at
            )
            for tracker in trackers
        ]
        
        return ProtocolTrackersResponse(trackers=tracker_items)
    except Exception as e:
        logger.error(f"Error retrieving protocols for organism {organism}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve protocols: {str(e)}")
    finally:
        session.close()


@router.get("/protocols/{tracker_id}", response_model=ProtocolDetailResponse)
async def get_protocol_detail(tracker_id: int):
    """
    Get detailed protocol information including all reagents.
    
    Args:
        tracker_id: Protocol tracker ID
        
    Returns:
        ProtocolDetailResponse with organism info and reagent list
    """
    session = SessionLocal()
    try:
        tracker_repo = ProtocolTrackerRepository(session)
        protocol_repo = ProtocolRepository(session)
        
        # Get the tracker
        tracker = tracker_repo.get_by_id(tracker_id)
        if not tracker:
            raise HTTPException(status_code=404, detail=f"Protocol tracker {tracker_id} not found")
        
        # Get all protocols for this tracker
        protocols = protocol_repo.get_by_tracker_id(tracker_id)
        
        # Convert to reagent items
        reagents = [
            ReagentItem(
                name=protocol.reagent_name,
                concentration=protocol.concentration,
                unit=protocol.unit
            )
            for protocol in protocols
        ]
        
        return ProtocolDetailResponse(
            tracker_id=tracker.id,
            organism_name=tracker.target_organism,
            created_at=tracker.created_at,
            reagents=reagents
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving protocol {tracker_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve protocol: {str(e)}")
    finally:
        session.close()


@router.put("/protocols/{tracker_id}/refine", response_model=ProtocolDetailResponse)
async def refine_protocol(
    tracker_id: int,
    absorbance_csv_path: str = Query(..., description="Path to absorbance data CSV file"),
    research_agent: str = Query("basic", description="Research agent to use: 'basic' (OpenAI o1) or 'futurehouse'")
):
    """
    Refine an existing protocol with absorbance data.
    
    This endpoint:
    1. Retrieves the existing protocol
    2. Uses BLAST API to find related organisms
    3. Uses Research Agent to gather literature
    4. Uses Protocol Agent to generate improved protocol with absorbance data
    5. Updates the existing protocol (replaces reagents)
    
    Args:
        tracker_id: Protocol tracker ID to update
        absorbance_csv_path: Path to absorbance data CSV file
        research_agent: Research agent to use ('basic' or 'futurehouse')
        
    Returns:
        ProtocolDetailResponse with updated reagent list
    """
    try:
        logger.info(f"Starting protocol refinement for tracker ID: {tracker_id}")
        
        # Get existing protocol
        session = SessionLocal()
        try:
            tracker_repo = ProtocolTrackerRepository(session)
            protocol_repo = ProtocolRepository(session)
            
            # Get the tracker
            tracker = tracker_repo.get_by_id(tracker_id)
            if not tracker:
                raise HTTPException(status_code=404, detail=f"Protocol tracker {tracker_id} not found")
            
            organism_name = tracker.target_organism
            logger.info(f"Refining protocol for organism: {organism_name}")
            
        finally:
            session.close()
        
        # Step 1: Use BlastAPI to find related organisms
        logger.info("Step 1: Finding related organisms via BLAST...")
        blast_api = BlastAPI()
        related_organisms = blast_api.get_top_10_related_organisms(organism_name)
        logger.info(f"Found {len(related_organisms)} related organisms: {related_organisms}")
        
        # Step 2: Use Research Agent to gather literature for related organisms
        logger.info(f"Step 2: Gathering scientific literature via {research_agent} agent...")
        
        # Add the original organism to the list
        all_organisms = [organism_name] + related_organisms
        logger.info(f"Querying literature for {len(all_organisms)} organisms")
        
        # Choose the appropriate research agent
        if research_agent.lower() == "futurehouse":
            agent = FutureHouseAPI()
        else:  # default to basic
            agent = BasicResearchAgent(model="o1-mini")
        
        # Run the task and get the literature content (returns string directly)
        literature_content = agent.run_task(all_organisms)
        
        logger.info(f"Gathered literature content ({len(literature_content)} characters)")
        
        # Step 3: Use ProtocolAgent to generate the refined protocol
        logger.info("Step 3: Generating refined protocol with absorbance data...")
        protocol_agent = ProtocolAgent(organism_name=organism_name)
        
        # Generate protocol DataFrame with absorbance data
        protocol_df = protocol_agent.generate_protocol(
            literature=literature_content,
            absorbance_csv_path=absorbance_csv_path
        )
        
        logger.info(f"Generated refined protocol with {len(protocol_df)} reagents")
        
        # Step 4: Update the existing protocol in the database
        session = SessionLocal()
        try:
            protocol_repo = ProtocolRepository(session)
            
            # Prepare reagents data
            reagents = []
            for _, row in protocol_df.iterrows():
                reagent = {
                    'reagent_name': row['name'],
                    'unit': row['unit'],
                    'concentration': row.get('concentration') if pd.notna(row.get('concentration')) else None
                }
                reagents.append(reagent)
            
            # Update protocols for this tracker (replaces existing)
            updated_protocols = protocol_repo.update_all_for_tracker(
                protocol_id=tracker_id,
                reagents=reagents
            )
            logger.info(f"Updated {len(updated_protocols)} reagents for tracker ID: {tracker_id}")
            
        finally:
            session.close()
        
        # Step 5: Return the updated protocol
        return await get_protocol_detail(tracker_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refining protocol: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refine protocol: {str(e)}"
        )

