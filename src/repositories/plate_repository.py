from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.models.plate import Plate


class PlateRepository:
    """Repository for managing Plate data operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self, 
        plate_id: int, 
        row_id: str, 
        column_id: int, 
        value: float,
        seconds_time_sample: int
    ) -> Plate:
        """Create a new plate record"""
        plate = Plate(
            plate_id=plate_id,
            row_id=row_id,
            column_id=column_id,
            value=value,
            seconds_time_sample=seconds_time_sample
        )
        self.session.add(plate)
        self.session.commit()
        self.session.refresh(plate)
        return plate
    
    def bulk_create(self, plates_data: List[dict]) -> int:
        """
        Bulk create plate records
        
        Returns:
            Number of records inserted
        """
        plates = [
            Plate(
                plate_id=data['plate_id'],
                row_id=data['row_id'],
                column_id=data['column_id'],
                value=data['value'],
                seconds_time_sample=data['seconds_time_sample']
            )
            for data in plates_data
        ]
        self.session.bulk_save_objects(plates)
        self.session.commit()
        return len(plates)
    
    def get_by_plate_id(self, plate_id: int) -> List[Plate]:
        """Get all records for a specific plate"""
        return self.session.query(Plate).filter(Plate.plate_id == plate_id).all()
    
    def get_by_plate_and_time(self, plate_id: int, seconds_time_sample: int) -> List[Plate]:
        """Get all records for a specific plate at a specific time"""
        return self.session.query(Plate).filter(
            Plate.plate_id == plate_id,
            Plate.seconds_time_sample == seconds_time_sample
        ).all()
    
    def get_by_well(self, plate_id: int, row_id: str, column_id: int) -> List[Plate]:
        """Get all time series records for a specific well"""
        return self.session.query(Plate).filter(
            Plate.plate_id == plate_id,
            Plate.row_id == row_id,
            Plate.column_id == column_id
        ).order_by(Plate.seconds_time_sample).all()
    
    def delete_by_plate_id(self, plate_id: int) -> int:
        """Delete all records for a specific plate"""
        count = self.session.query(Plate).filter(Plate.plate_id == plate_id).delete()
        self.session.commit()
        return count

