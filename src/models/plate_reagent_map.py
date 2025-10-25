from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from . import Base

if TYPE_CHECKING:
    from .reagent import Reagent
    from .plate import Plate

class PlateReagentMap(Base):
    """Mapping table connecting plates, wells, and reagents"""
    __tablename__ = "plate_reagent_map"
    
    plate_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    well_id: Mapped[int] = mapped_column(Integer, nullable=False)
    reagent_id: Mapped[int] = mapped_column(Integer, ForeignKey("reagent.id"), nullable=False)
    concentration: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    reagent: Mapped["Reagent"] = relationship("Reagent", back_populates="plate_reagent_maps")
    plates: Mapped[list["Plate"]] = relationship("Plate", back_populates="plate_reagent_map")

