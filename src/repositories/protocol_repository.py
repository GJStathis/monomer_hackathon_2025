from sqlalchemy.orm import Session
from typing import Optional, List

from src.models.protocol import Protocol


class ProtocolRepository:
    """Repository for managing Protocol operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, protocol_id: int) -> Optional[Protocol]:
        """Get a protocol entry by ID"""
        return self.session.query(Protocol).filter(
            Protocol.id == protocol_id
        ).first()
    
    def get_by_tracker_id(self, tracker_id: int) -> List[Protocol]:
        """Get all protocol entries for a specific tracker"""
        return self.session.query(Protocol).filter(
            Protocol.protocol_id == tracker_id
        ).all()
    
    def create(
        self,
        protocol_id: int,
        reagent_name: str,
        unit: str,
        concentration: Optional[str] = None
    ) -> Protocol:
        """Create a new protocol entry"""
        protocol = Protocol(
            protocol_id=protocol_id,
            reagent_name=reagent_name,
            concentration=concentration,
            unit=unit
        )
        self.session.add(protocol)
        self.session.commit()
        self.session.refresh(protocol)
        return protocol
    
    def create_many(
        self,
        protocol_id: int,
        reagents: List[dict]
    ) -> List[Protocol]:
        """
        Create multiple protocol entries at once.
        
        Args:
            protocol_id: The tracker ID
            reagents: List of dicts with keys: reagent_name, unit, concentration (optional)
        """
        protocols = []
        for reagent in reagents:
            protocol = Protocol(
                protocol_id=protocol_id,
                reagent_name=reagent['reagent_name'],
                concentration=reagent.get('concentration'),
                unit=reagent['unit']
            )
            protocols.append(protocol)
        
        self.session.add_all(protocols)
        self.session.commit()
        
        for protocol in protocols:
            self.session.refresh(protocol)
        
        return protocols
    
    def delete_by_tracker_id(self, protocol_id: int) -> int:
        """
        Delete all protocol entries for a specific tracker.
        
        Args:
            tracker_id: The tracker ID
            
        Returns:
            Number of deleted entries
        """
        deleted_count = self.session.query(Protocol).filter(
            Protocol.protocol_id == protocol_id
        ).delete()
        self.session.commit()
        return deleted_count
    
    def update_all_for_tracker(
        self,
        protocol_id: int,
        reagents: List[dict]
    ) -> List[Protocol]:
        """
        Replace all protocols for a tracker with new ones.
        
        Args:
            protocol_id: The tracker ID
            reagents: List of dicts with keys: reagent_name, unit, concentration (optional)
            
        Returns:
            List of new protocol entries
        """
        # Delete existing protocols
        self.delete_by_tracker_id(protocol_id)
        
        # Create new protocols
        return self.create_many(protocol_id, reagents)

