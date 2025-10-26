from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models import (
    RuntimeConfig,
    TaskRequest,
)
from ldp.agent import AgentConfig
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.repositories.future_house_literature_repository import FutureHouseLiteratureRepository


class FutureHouseAPI:
    def __init__(self, fh_model: str = "crow", database_url: str = "sqlite:///./database.db"):
        self.client = FutureHouseClient(
            api_key=os.getenv("FUTUREHOUSE_API_KEY")
        )   
        self.fh_model = fh_model
        self.query_template = "Find documentation useful for crafting protocols to grow the highest yield of {target}"

        self.logger = logging.getLogger(__name__)
        
        # Database setup for caching
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def run_task(self, targets: list[str]) -> str:

        if len(targets) == 0:
            raise ValueError("No targets added")

        # Create a unique key from the sorted list of targets
        organisms_key = ",".join(sorted(targets))
        
        # Check cache first
        session = self.SessionLocal()
        try:
            repository = FutureHouseLiteratureRepository(session)
            cached_entry = repository.get_by_organisms(organisms_key)
            
            if cached_entry:
                self.logger.info(f"Cache hit for organisms: {organisms_key}")
                return cached_entry.literature
            
            self.logger.info(f"Cache miss for organisms: {organisms_key}. Fetching from FutureHouse API...")
            
            # Cache miss - run the actual task
            task_requests = [
                TaskRequest(
                    name=JobNames.from_string(self.fh_model),
                    query=self.query_template.format(target=target)
                )
                for target in targets
            ]
            responses = self.client.run_tasks_until_done(task_requests)
            
            self.logger.info(f"Job completed with status: {responses[0].status}")
            
            # Cache the successful response
            if responses[0].status == "completed" and hasattr(responses[0], 'answer'):
                literature_text = responses[0].answer
                repository.create(organisms_key, literature_text)
                self.logger.info(f"Cached literature for organisms: {organisms_key}")
                return literature_text
            
            # Fallback if no answer attribute
            return str(responses[0])
            
        finally:
            session.close()