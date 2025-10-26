from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from . import Base


class RelatedOrganisms(Base):
    """Cache table for BLAST API related organisms results"""
    __tablename__ = "related_organisms"
    
    organism: Mapped[str] = mapped_column(String, primary_key=True)
    related_organisms: Mapped[str] = mapped_column(Text, nullable=False)

