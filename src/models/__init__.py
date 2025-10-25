from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass

# Import all models here so Alembic can detect them
from .reagent import Reagent
from .plate_reagent_map import PlateReagentMap
from .plate import Plate
from .cell_growth import CellGrowth

