from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from . import Base

if TYPE_CHECKING:
    from .plate_reagent_map import PlateReagentMap

class Reagent(Base):
    """Reagent model for storing chemical reagent information"""
    __tablename__ = "reagent"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    concentration: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    
    # Relationship to plate_reagent_map
    plate_reagent_maps: Mapped[list["PlateReagentMap"]] = relationship(
        "PlateReagentMap", back_populates="reagent"
    )

