from sqlalchemy import Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING
from datetime import datetime
from . import Base

if TYPE_CHECKING:
    from .plate_reagent_map import PlateReagentMap

class CellGrowth(Base):
    """Cell growth model for storing cell density measurements"""
    __tablename__ = "cell_growth"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plate_id: Mapped[int] = mapped_column(Integer, ForeignKey("plate_reagent_map.plate_id"), nullable=False)
    well_id: Mapped[int] = mapped_column(Integer, ForeignKey("plate_reagent_map.well_id"), nullable=False)
    cell_density: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationship
    plate_reagent_map: Mapped["PlateReagentMap"] = relationship("PlateReagentMap")

