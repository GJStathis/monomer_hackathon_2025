from sqlalchemy.orm import Session
from typing import Optional, List

from src.models.protocol_tracker import ProtocolTracker


class ProtocolTrackerRepository:
    """Repository for managing ProtocolTracker operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, tracker_id: int) -> Optional[ProtocolTracker]:
        """Get a protocol tracker by ID"""
        return self.session.query(ProtocolTracker).filter(
            ProtocolTracker.id == tracker_id
        ).first()
    
    def get_all(self) -> List[ProtocolTracker]:
        """Get all protocol trackers"""
        return self.session.query(ProtocolTracker).all()
    
    def get_by_organism(self, target_organism: str) -> List[ProtocolTracker]:
        """Get all protocol trackers for a specific organism"""
        return self.session.query(ProtocolTracker).filter(
            ProtocolTracker.target_organism == target_organism
        ).all()
    
    def create(self, target_organism: str) -> ProtocolTracker:
        """Create a new protocol tracker entry"""
        tracker = ProtocolTracker(target_organism=target_organism)
        self.session.add(tracker)
        self.session.commit()
        self.session.refresh(tracker)
        return tracker
    
    def get_distinct_organisms(self) -> List[str]:
        """Get a distinct list of all organisms in the tracker"""
        result = self.session.query(ProtocolTracker.target_organism).distinct().all()
        return [row[0] for row in result]

