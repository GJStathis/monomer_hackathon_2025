from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass

# Import all models here so Alembic can detect them
from .reagent import Reagent
from .experiment import Experiment
from .reagent_values import ReagentValue
from .plate import Plate
from .plate_experiment_map import PlateExperimentMap
from .future_house_literature import FutureHouseLiterature
from .related_organisms import RelatedOrganisms
from .protocol_tracker import ProtocolTracker
from .protocol import Protocol
