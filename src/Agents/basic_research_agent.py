"""
Basic Research Agent using LangChain and OpenAI's reasoning model.

This agent mimics the behavior of the FutureHouse API by generating research
about organisms using OpenAI's o1 reasoning model.
"""

import os
import logging
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv

from src.repositories.future_house_literature_repository import FutureHouseLiteratureRepository

load_dotenv()


class BasicResearchAgent:
    """
    A research agent that uses LangChain and OpenAI to generate scientific literature
    about organism growth protocols.
    """
    
    def __init__(
        self, 
        model: str = "o1-mini",
        database_url: str = "sqlite:///./database.db"
    ):
        """
        Initialize the Basic Research Agent.
        
        Args:
            model: OpenAI model to use (default: o1-mini for reasoning)
                   Options: "o1-mini", "o1-preview", "gpt-4o", "gpt-4-turbo"
            database_url: Database URL for caching results
        """
        # Note: o1 models don't support temperature parameter
        if model.startswith("o1"):
            self.llm = ChatOpenAI(
                model=model,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.7,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        
        self.logger = logging.getLogger(__name__)
        self.model = model
        
        # Database setup for caching
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        self.query_template = """Find and synthesize scientific documentation useful for crafting protocols to grow the highest yield of {target}.

Include information about:
- Optimal growth media composition
- Carbon and nitrogen sources
- Essential minerals and trace elements
- pH and temperature requirements
- Specific growth factors or supplements
- Common antibiotics or selection markers
- Any organism-specific requirements

Focus on peer-reviewed sources and established protocols."""
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the research agent."""
        return """You are an expert microbiologist and scientific literature researcher specializing in microbial growth optimization.

Your task is to provide comprehensive, accurate information about optimal growth conditions for microorganisms. You should:

1. Draw from established scientific literature and protocols
2. Focus on practical, laboratory-applicable information
3. Include specific reagents, concentrations, and conditions
4. Mention key research papers or established protocols when relevant
5. Consider modern best practices in microbiology
6. Be specific about growth media components (carbon sources, nitrogen sources, minerals, buffers, etc.)
7. Include information about related organisms that may inform protocol design

Provide detailed, well-organized information that can directly inform protocol development."""
    
    def run_task(self, targets: List[str]) -> str:
        """
        Generate research literature for the given target organisms.
        
        Args:
            targets: List of organism names to research
            
        Returns:
            String containing synthesized research literature
        """
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
            
            self.logger.info(f"Cache miss for organisms: {organisms_key}. Generating research using {self.model}...")
            
            # Generate queries for each target
            queries = [self.query_template.format(target=target) for target in targets]
            
            # Combine queries into a single comprehensive request
            combined_query = f"""Research the following organisms and provide comprehensive growth protocol information for each:

{chr(10).join(f"{i+1}. {query}" for i, query in enumerate(queries))}

Synthesize the information across all organisms, noting similarities and differences that might inform protocol design."""
            
            # Create the prompt
            system_prompt = self._create_system_prompt()
            
            # For o1 models, we can't use system messages, so we combine into user message
            if self.model.startswith("o1"):
                full_prompt = f"{system_prompt}\n\n{combined_query}"
                response = self.llm.invoke(full_prompt)
            else:
                messages = [
                    SystemMessagePromptTemplate.from_template(system_prompt),
                    HumanMessagePromptTemplate.from_template(combined_query)
                ]
                chat_prompt = ChatPromptTemplate.from_messages(messages)
                formatted_prompt = chat_prompt.format_messages()
                response = self.llm.invoke(formatted_prompt)
            
            # Extract the text content
            literature_text = response.content
            
            self.logger.info(f"Generated {len(literature_text)} characters of research")
            
            # Cache the successful response
            repository.create(organisms_key, literature_text)
            self.logger.info(f"Cached literature for organisms: {organisms_key}")
            
            return literature_text
            
        except Exception as e:
            self.logger.error(f"Error generating research: {str(e)}", exc_info=True)
            raise
        finally:
            session.close()
    
    def research_single_organism(self, organism: str) -> str:
        """
        Convenience method to research a single organism.
        
        Args:
            organism: Name of the organism to research
            
        Returns:
            String containing research literature
        """
        return self.run_task([organism])

