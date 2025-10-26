from sqlalchemy import Integer, Float, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from . import Base

class Plate(Base):
    """Plate model for storing plate measurements"""
    __tablename__ = "plate"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plate_id: Mapped[int] = mapped_column(Integer, nullable=False)
    row_id: Mapped[str] = mapped_column(String, nullable=False)
    column_id: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    seconds_time_sample: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

