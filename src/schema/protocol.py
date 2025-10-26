"""
Pydantic schemas for protocol API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReagentItem(BaseModel):
    """Schema for a single reagent item in the protocol."""
    name: str = Field(..., description="Name of the reagent")
    concentration: Optional[float] = Field(None, description="Concentration value (null for liquids)")
    unit: str = Field(..., description="Unit of concentration or description for liquids")


class GenerateProtocolRequest(BaseModel):
    """Request schema for generating a protocol."""
    organism_name: str = Field(..., description="Name of the organism to generate protocol for")
    absorbance_csv_path: Optional[str] = Field(None, description="Optional path to absorbance data CSV")


class GenerateProtocolResponse(BaseModel):
    """Response schema for generated protocol."""
    organism_name: str = Field(..., description="Name of the organism")
    related_organisms: List[str] = Field(..., description="List of related organisms found via BLAST")
    reagents: List[ReagentItem] = Field(..., description="List of recommended reagents")
    message: str = Field(..., description="Status message")


class ProtocolTrackerItem(BaseModel):
    """Schema for a protocol tracker item."""
    id: int = Field(..., description="Tracker ID")
    target_organism: str = Field(..., description="Target organism name")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class OrganismListResponse(BaseModel):
    """Response schema for list of organisms."""
    organisms: List[str] = Field(..., description="List of distinct organism names")


class ProtocolTrackersResponse(BaseModel):
    """Response schema for protocol trackers."""
    trackers: List[ProtocolTrackerItem] = Field(..., description="List of protocol trackers")


class ProtocolDetailResponse(BaseModel):
    """Response schema for detailed protocol."""
    tracker_id: int = Field(..., description="Protocol tracker ID")
    organism_name: str = Field(..., description="Target organism")
    created_at: datetime = Field(..., description="Creation timestamp")
    reagents: List[ReagentItem] = Field(..., description="List of reagents in the protocol")

