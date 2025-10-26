from sqlalchemy.orm import Session
from typing import List, Optional

from src.models.reagent_values import ReagentValue


class ReagentValueRepository:
    """Repository for managing ReagentValue data operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self, 
        experiment_id: int, 
        reagent_id: int, 
        value: float,
        unit: str
    ) -> ReagentValue:
        """Create a new reagent value record"""
        reagent_value = ReagentValue(
            experiment_id=experiment_id,
            reagent_id=reagent_id,
            value=value,
            unit=unit
        )
        self.session.add(reagent_value)
        self.session.commit()
        self.session.refresh(reagent_value)
        return reagent_value
    
    def bulk_create(self, reagent_values_data: List[dict]) -> int:
        """
        Bulk create reagent value records
        
        Returns:
            Number of records inserted
        """
        reagent_values = [
            ReagentValue(
                experiment_id=data['experiment_id'],
                reagent_id=data['reagent_id'],
                value=data['value'],
                unit=data['unit']
            )
            for data in reagent_values_data
        ]
        self.session.bulk_save_objects(reagent_values)
        self.session.commit()
        return len(reagent_values)
    
    def get_by_experiment_id(self, experiment_id: int) -> List[ReagentValue]:
        """Get all reagent values for an experiment"""
        return self.session.query(ReagentValue).filter(
            ReagentValue.experiment_id == experiment_id
        ).all()
    
    def get_by_reagent_id(self, reagent_id: int) -> List[ReagentValue]:
        """Get all reagent values for a specific reagent"""
        return self.session.query(ReagentValue).filter(
            ReagentValue.reagent_id == reagent_id
        ).all()
    
    def delete_by_experiment_id(self, experiment_id: int) -> int:
        """Delete all reagent values for an experiment"""
        count = self.session.query(ReagentValue).filter(
            ReagentValue.experiment_id == experiment_id
        ).delete()
        self.session.commit()
        return count

