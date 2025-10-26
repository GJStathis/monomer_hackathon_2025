from sqlalchemy import Integer, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from . import Base

if TYPE_CHECKING:
    from .experiment import Experiment
    from .reagent import Reagent

class ReagentValue(Base):
    """Reagent values for experiments"""
    __tablename__ = "reagent_values"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_id: Mapped[int] = mapped_column(Integer, ForeignKey("experiment.id"), nullable=False)
    reagent_id: Mapped[int] = mapped_column(Integer, ForeignKey("reagent.id"), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    
    # Relationships
    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="reagent_values")
    reagent: Mapped["Reagent"] = relationship("Reagent", back_populates="reagent_values")

