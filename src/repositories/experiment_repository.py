from sqlalchemy.orm import Session
from typing import List, Optional

from src.models.experiment import Experiment


class ExperimentRepository:
    """Repository for managing Experiment data operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, cell_concentration: float, dilution: float) -> Experiment:
        """Create a new experiment record"""
        experiment = Experiment(
            cell_concentration=cell_concentration,
            dilution=dilution
        )
        self.session.add(experiment)
        self.session.commit()
        self.session.refresh(experiment)
        return experiment
    
    def get_by_id(self, experiment_id: int) -> Optional[Experiment]:
        """Get an experiment by ID"""
        return self.session.query(Experiment).filter(Experiment.id == experiment_id).first()
    
    def get_all(self) -> List[Experiment]:
        """Get all experiments"""
        return self.session.query(Experiment).all()
    
    def delete(self, experiment_id: int) -> bool:
        """Delete an experiment"""
        experiment = self.get_by_id(experiment_id)
        if experiment:
            self.session.delete(experiment)
            self.session.commit()
            return True
        return False

