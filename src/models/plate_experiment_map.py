from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from . import Base

if TYPE_CHECKING:
    from .experiment import Experiment

class PlateExperimentMap(Base):
    """Mapping table connecting plate columns to experiments"""
    __tablename__ = "plate_experiment_map"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    column_id: Mapped[int] = mapped_column(Integer, nullable=False)
    experiment_id: Mapped[int] = mapped_column(Integer, ForeignKey("experiment.id"), nullable=False)
    
    # Relationship
    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="plate_experiment_maps")

