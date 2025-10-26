"""
Protocol Agent for generating scientific reagent recommendations using LangChain.

This agent analyzes scientific literature and optionally absorbance data to recommend
reagents for experiments.
"""

import os
import logging
import pandas as pd
from typing import Optional, List, Dict, Any
from pathlib import Path
from io import StringIO
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import AIMessage
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.repositories.protocol_tracker_repository import ProtocolTrackerRepository
from src.repositories.protocol_repository import ProtocolRepository

load_dotenv()

class ProtocolAgent:
    """
    An AI agent for generating scientific protocols and reagent recommendations.
    
    Uses LangChain and OpenAI to analyze scientific literature and experimental data
    to suggest optimal reagent combinations, concentrations, and protocols.
    """
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.7, organism_name: str = "organism_name", database_url: str = "sqlite:///./database.db"):
        """
        Initialize the Protocol Agent.
        
        Args:
            model: OpenAI model to use (default: gpt-4o)
            temperature: Temperature for generation (0.0-1.0, higher = more creative)
            organism_name: Name of the organism for this protocol
            database_url: Database URL for storing protocols
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        self.logger = logging.getLogger(__name__)
        self.root_dir = Path(__file__).parent.parent.parent 
        self.protocol_dir = self.root_dir / 'protocols'
        self.organism_name = organism_name
        
        # Database setup for saving protocols
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)


    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        return """You are an expert biochemist and protocol designer specializing in media optimization for microbial growth experiments.

Your task is to analyze scientific literature and experimental data to recommend optimal reagent combinations for experiments. You should:

1. Consider standard microbial growth media components (carbon sources, nitrogen sources, minerals, buffers, trace elements)
2. Suggest appropriate concentrations based on established protocols and the literature provided
3. Consider interactions between reagents
4. Account for experimental goals (growth optimization, specific metabolite production, etc.)
5. When absorbance data is provided, analyze growth patterns to inform recommendations

Output your recommendations as a CSV table with columns:
- name: reagent name
- concentration: numerical concentration value (use NULL if not applicable)
- unit: concentration unit (e.g., mg/mL, M, N, or descriptive text for liquids)

For reagents that are already liquids (like glycerol or trace metals solutions), use NULL for concentration and describe the form in the unit column.

Be specific and practical. Use standard laboratory concentrations and follow best practices."""

    def _create_user_prompt_template(self) -> str:
        """Create the user prompt template."""
        return """Please analyze the following scientific literature and generate reagent recommendations:

LITERATURE:
{literature}

{absorbance_section}

Generate a complete CSV table of recommended reagents with appropriate concentrations and units. Include all necessary components for a complete growth medium (carbon sources, nitrogen sources, minerals, buffers, etc.).

Output only the CSV data with headers: name,concentration,unit"""

    def analyze_absorbance_data(self, absorbance_csv_path: str) -> str:
        """
        Analyze absorbance data and create a summary.
        
        Args:
            absorbance_csv_path: Path to CSV file with absorbance data
            
        Returns:
            String summary of the absorbance data analysis
        """
        try:
            df = pd.read_csv(absorbance_csv_path, index_col=0)
            
            # Basic statistics
            analysis = "ABSORBANCE DATA ANALYSIS:\n"
            analysis += f"- Time points measured: {len(df)} samples\n"
            analysis += f"- Wells measured: {len(df.columns)} wells (96-well plate)\n"
            analysis += f"- Time range: {df.index.min()} to {df.index.max()} seconds ({df.index.max() / 3600:.1f} hours)\n"
            
            # Calculate growth metrics
            initial_values = df.iloc[0]
            final_values = df.iloc[-1]
            growth = final_values - initial_values
            
            # Identify best performing wells
            top_wells = growth.nlargest(5)
            analysis += f"\nTop 5 performing wells (by growth):\n"
            for well, growth_val in top_wells.items():
                analysis += f"  - Well {well}: Initial={initial_values[well]:.3f}, Final={final_values[well]:.3f}, Growth={growth_val:.3f}\n"
            
            # Identify poor performing wells
            bottom_wells = growth.nsmallest(5)
            analysis += f"\nBottom 5 performing wells:\n"
            for well, growth_val in bottom_wells.items():
                analysis += f"  - Well {well}: Initial={initial_values[well]:.3f}, Final={final_values[well]:.3f}, Growth={growth_val:.3f}\n"
            
            # Overall statistics
            analysis += f"\nOverall statistics:\n"
            analysis += f"  - Mean final absorbance: {final_values.mean():.3f} ± {final_values.std():.3f}\n"
            analysis += f"  - Mean growth: {growth.mean():.3f} ± {growth.std():.3f}\n"
            
            return analysis
            
        except Exception as e:
            return f"Error analyzing absorbance data: {str(e)}"

    def generate_protocol(
        self,
        literature: str,
        absorbance_csv_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Generate reagent recommendations based on literature and optional absorbance data.
        
        Args:
            literature: Scientific literature text to analyze
            absorbance_csv_path: Optional path to CSV with absorbance data
            output_csv_path: Optional path to save output CSV
            
        Returns:
            DataFrame with reagent recommendations (name, concentration, unit)
        """
        # Analyze absorbance data if provided
        absorbance_section = ""
        if absorbance_csv_path:
            absorbance_analysis = self.analyze_absorbance_data(absorbance_csv_path)
            absorbance_section = f"\n{absorbance_analysis}\n\nPlease consider the growth patterns shown in the absorbance data when making your recommendations. Focus on conditions that promote robust growth or match the experimental goals described in the literature."
        
        # Create the prompt
        system_prompt = self._create_system_prompt()
        user_prompt_template = self._create_user_prompt_template()
        
        # Format the user prompt
        user_prompt = user_prompt_template.format(
            literature=literature,
            absorbance_section=absorbance_section
        )
        
        # Create chat prompt
        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(user_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        
        # Generate response
        formatted_prompt = chat_prompt.format_messages(
            literature=literature,
            absorbance_section=absorbance_section
        )
        
        response = self.llm.invoke(formatted_prompt)
        
        # Parse CSV from response
        csv_content = response.content.strip()
        
        # Handle markdown code blocks if present
        if "```" in csv_content:
            # Extract content between code blocks
            parts = csv_content.split("```")
            for part in parts:
                if "name,concentration,unit" in part or "name,concentration" in part:
                    csv_content = part.strip()
                    # Remove language identifier if present (e.g., "csv\n")
                    lines = csv_content.split("\n")
                    if lines[0].lower() in ["csv", "text"]:
                        csv_content = "\n".join(lines[1:])
                    break
        
        # Clean up lines with extra commas in reagent names
        lines = csv_content.split("\n")
        fixed_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip language identifiers
            if line.lower() in ["csv", "text"]:
                continue
            
            # If it's the header line, keep it as is
            if "name,concentration,unit" in line.lower() or line.startswith("name,"):
                fixed_lines.append(line)
                continue
            
            # Count commas - we expect exactly 2 commas (3 fields)
            comma_count = line.count(",")
            
            if comma_count > 2:
                # Split and rejoin: merge all parts except last 2 into the name
                parts = line.split(",")
                # Join all parts except the last 2 as the name
                name = ",".join(parts[:-2])
                concentration = parts[-2]
                unit = parts[-1]
                fixed_line = f"{name},{concentration},{unit}"
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        
        csv_content = "\n".join(fixed_lines)
        
        # Parse CSV
        try:
            df = pd.read_csv(StringIO(csv_content))
            
            # Save CSV file if output path exists
            if os.path.exists(self.protocol_dir):
                df.to_csv(os.path.join(self.protocol_dir, f"{self.organism_name}_protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"), index=False)
                self.logger.info(f"Saved reagent recommendations to {os.path.join(self.protocol_dir, f'{self.organism_name}_protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv')}")
            
            # Save to database
            session = self.SessionLocal()
            try:
                # Create protocol tracker entry
                tracker_repo = ProtocolTrackerRepository(session)
                tracker = tracker_repo.create(target_organism=self.organism_name)
                self.logger.info(f"Created protocol tracker with ID: {tracker.id}")
                
                # Prepare reagents data
                reagents = []
                for _, row in df.iterrows():
                    reagent = {
                        'reagent_name': row['name'],
                        'unit': row['unit'],
                        'concentration': row.get('concentration') if pd.notna(row.get('concentration')) else None
                    }
                    reagents.append(reagent)
                
                # Create protocol entries
                protocol_repo = ProtocolRepository(session)
                protocols = protocol_repo.create_many(
                    protocol_id=tracker.id,
                    reagents=reagents
                )
                self.logger.info(f"Saved {len(protocols)} reagents to database for tracker ID: {tracker.id}")
                
            except Exception as db_error:
                self.logger.error(f"Error saving to database: {db_error}", exc_info=True)
                # Don't raise - we still want to return the DataFrame even if DB save fails
            finally:
                session.close()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error parsing CSV response: {e}")
            self.logger.error(f"Raw response:\n{csv_content}")
            raise
    
    def refine_protocol(
        self,
        existing_protocol_df: pd.DataFrame,
        feedback: str,
        literature: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Refine an existing protocol based on feedback.
        
        Args:
            existing_protocol_df: DataFrame with current protocol
            feedback: User feedback or experimental observations
            literature: Optional additional literature to consider
            
        Returns:
            DataFrame with refined reagent recommendations
        """
        # Convert existing protocol to CSV string
        existing_csv = existing_protocol_df.to_csv(index=False)
        
        refinement_prompt = f"""You are refining an existing experimental protocol based on feedback.

CURRENT PROTOCOL (CSV):
{existing_csv}

FEEDBACK/OBSERVATIONS:
{feedback}

{f"ADDITIONAL LITERATURE:\n{literature}\n" if literature else ""}

Please provide an updated CSV with modified reagent recommendations that address the feedback. Maintain the same CSV format (name,concentration,unit).

Output only the refined CSV data:"""

        messages = [
            SystemMessagePromptTemplate.from_template(self._create_system_prompt()),
            HumanMessagePromptTemplate.from_template(refinement_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        
        formatted_prompt = chat_prompt.format_messages()
        response = self.llm.invoke(formatted_prompt)
        
        # Parse CSV from response
        csv_content = response.content.strip()
        
        # Handle markdown code blocks
        if "```" in csv_content:
            parts = csv_content.split("```")
            for part in parts:
                if "name,concentration,unit" in part:
                    csv_content = part.strip()
                    lines = csv_content.split("\n")
                    if lines[0].lower() in ["csv", "text"]:
                        csv_content = "\n".join(lines[1:])
                    break
        
        return pd.read_csv(StringIO(csv_content))
