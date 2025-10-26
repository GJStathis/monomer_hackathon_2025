import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.repositories.protocol_repository import ProtocolRepository

class RoboticsIntegrationAgent:

    def __init__(self):
        self.claude_key = os.getenv("CLAUDE_API_KEY")

        self.claude_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.claude_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        self.prompt = "Write a detailed protocol for creating the following media with an Opentron Flex protocol {media_protocol}. Include first the labware needed, solutions required in each labware and instructions on making them. Then secondly write as text the python script that i can run on an Opentron Flex robot. Minimize the number of tokens needed"

        self.engine = create_engine("sqlite:///./database.db")
        self.SessionLocal = sessionmaker(bind=self.engine)

    def generate_protocol_script(self, protocol_id: int) -> str:
        try:
            session = self.SessionLocal()
            protocol_repo = ProtocolRepository(session)
            protocols = protocol_repo.get_by_tracker_id(protocol_id)

            if not protocols:
                raise ValueError(f"No protocols found for tracker ID {protocol_id}")

            media_protocol = ""
            for protocol in protocols:
                media_protocol += f"{protocol.reagent_name}: {protocol.concentration} {protocol.unit}\n\n"

            prompt = self.prompt.format(media_protocol=media_protocol.strip())

            data = {
                "model": "claude-sonnet-4-5",
                "max_tokens": 10000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(self.claude_url, headers=self.headers, json=data)
            if response.status_code == 200:
                reply = response.json()
                return reply["content"][0]["text"]
            else:
                raise ValueError(f"Error: {response.status_code} {response.text}")
        except Exception as e:
            raise ValueError(f"Error: {e}")
        finally:
            session.close()