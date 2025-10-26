from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING
from datetime import datetime
from . import Base

if TYPE_CHECKING:
    from .protocol import Protocol


class ProtocolTracker(Base):
    """Tracker table for protocol generation runs"""
    __tablename__ = "protocol_tracker"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_organism: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    protocols: Mapped[list["Protocol"]] = relationship("Protocol", back_populates="protocol_tracker")

