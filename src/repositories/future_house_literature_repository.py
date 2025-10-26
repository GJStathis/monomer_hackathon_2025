from sqlalchemy.orm import Session
from typing import Optional

from src.models.future_house_literature import FutureHouseLiterature


class FutureHouseLiteratureRepository:
    """Repository for managing FutureHouseLiterature cache operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_organisms(self, organisms_key: str) -> Optional[FutureHouseLiterature]:
        """Get cached literature by organisms key"""
        return self.session.query(FutureHouseLiterature).filter(
            FutureHouseLiterature.organisms == organisms_key
        ).first()
    
    def create(self, organisms_key: str, literature: str) -> FutureHouseLiterature:
        """Create a new literature cache entry"""
        entry = FutureHouseLiterature(
            organisms=organisms_key,
            literature=literature
        )
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

