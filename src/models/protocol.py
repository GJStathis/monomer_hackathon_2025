from sqlalchemy import String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING
from datetime import datetime
from . import Base

if TYPE_CHECKING:
    from .protocol_tracker import ProtocolTracker


class Protocol(Base):
    """Protocol table storing reagent recommendations"""
    __tablename__ = "protocol"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    protocol_id: Mapped[int] = mapped_column(Integer, ForeignKey("protocol_tracker.id"), nullable=False)
    reagent_name: Mapped[str] = mapped_column(String, nullable=False)
    concentration: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    protocol_tracker: Mapped["ProtocolTracker"] = relationship("ProtocolTracker", back_populates="protocols")

