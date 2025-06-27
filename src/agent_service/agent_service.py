import os

from azure.ai.agents.models import ListSortOrder
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from rich import print

load_dotenv()

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
)
agent = project.agents.get_agent(agent_id="asst_ct6ObrQmVzExQLgrf43oihyi")
thread = project.agents.threads.create()

questions = [
    "Tell me about Leonardo da Vinci.",
    "Tell me about his most famous piece of art.",
    "Who will win the next Super Bowl?",
]

color_mapping = {
    "user": "blue",
    "assistant": "green",
    "system": "yellow",
}


def print_thread_messages(thread_id):
    """Fetches and prints messages from a thread."""
    messages = project.agents.messages.list(thread_id, order=ListSortOrder.ASCENDING)
    for message in messages:
        if message.text_messages:
            color = color_mapping.get(message.role, "white")
            print(f"[{color}]{message.role}[/]: {message.text_messages[-1].text.value}")


for question in questions:
    project.agents.messages.create(thread_id=thread.id, role="user", content=question)
    project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

print_thread_messages(thread.id)

print("=== End of Demo ===\n")
