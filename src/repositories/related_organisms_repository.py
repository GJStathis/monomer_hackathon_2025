from sqlalchemy.orm import Session
from typing import Optional

from src.models.related_organisms import RelatedOrganisms


class RelatedOrganismsRepository:
    """Repository for managing RelatedOrganisms cache operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_organism(self, organism: str) -> Optional[RelatedOrganisms]:
        """Get cached related organisms by organism name"""
        return self.session.query(RelatedOrganisms).filter(
            RelatedOrganisms.organism == organism.lower().strip()
        ).first()
    
    def create(self, organism: str, related_organisms: str) -> RelatedOrganisms:
        """Create a new related organisms cache entry"""
        entry = RelatedOrganisms(
            organism=organism.lower().strip(),
            related_organisms=related_organisms
        )
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

