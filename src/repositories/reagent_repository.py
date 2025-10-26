from sqlalchemy.orm import Session
from typing import List, Optional

from src.models.reagent import Reagent


class ReagentRepository:
    """Repository for managing Reagent data operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_name(self, name: str) -> Optional[Reagent]:
        """Get a reagent by name"""
        return self.session.query(Reagent).filter(Reagent.name == name).first()
    
    def get_by_id(self, reagent_id: int) -> Optional[Reagent]:
        """Get a reagent by ID"""
        return self.session.query(Reagent).filter(Reagent.id == reagent_id).first()
    
    def get_all(self) -> List[Reagent]:
        """Get all reagents"""
        return self.session.query(Reagent).all()

