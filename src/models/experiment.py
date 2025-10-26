from sqlalchemy import Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from . import Base

if TYPE_CHECKING:
    from .reagent_values import ReagentValue
    from .plate_experiment_map import PlateExperimentMap

class Experiment(Base):
    """Experiment model for storing experiment parameters"""
    __tablename__ = "experiment"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cell_concentration: Mapped[float] = mapped_column(Float, nullable=False)
    dilution: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    reagent_values: Mapped[list["ReagentValue"]] = relationship("ReagentValue", back_populates="experiment")
    plate_experiment_maps: Mapped[list["PlateExperimentMap"]] = relationship("PlateExperimentMap", back_populates="experiment")

