from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from . import Base


class FutureHouseLiterature(Base):
    """Cache table for FutureHouse API literature responses"""
    __tablename__ = "future_house_literature"
    
    organisms: Mapped[str] = mapped_column(String, primary_key=True)
    literature: Mapped[str] = mapped_column(Text, nullable=False)

