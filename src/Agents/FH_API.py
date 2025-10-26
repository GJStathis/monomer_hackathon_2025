targets = ['Vibrio natriegens']

from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models import (
    RuntimeConfig,
    TaskRequest,
)
from ldp.agent import AgentConfig
import os

client = FutureHouseClient(
    api_key="+sZzOaCmRpAjIhyV8fFmcg.platformv01.eyJqdGkiOiJkNDgyM2JhMy1lZGY1LTQwMDUtYWM5NC05ODdiMDFhM2ViZGQiLCJzdWIiOiJPNnhZbE03TlVrYm1mczFVc09QbDBZTGNxcTAzIiwiaWF0IjoxNzYxNDYwMjIwLCJleHAiOjE3NjQwNTIyMjB9.dlkXYDlLP/Aq0ISqEHwDa5SVwtseoxwBx7l7cip4AHk")

task_requests = [
    TaskRequest(
        name=JobNames.from_string("crow"),
        query=f"Find documentation useful for crafting protocols to grow the highest yield of {organism}"
    )
    for organism in targets
]

responses = client.run_tasks_until_done(task_requests)
task_response = responses[0]

print(f"Job status: {task_response.status}")
print(f"Job answer: \n{task_response.formatted_answer}")