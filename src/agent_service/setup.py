import os

from azure.ai.agents.models import BingGroundingTool
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from rich import print

load_dotenv()

project_endpoint = os.environ["PROJECT_ENDPOINT"]
bing_connection_id = os.environ["BING_CONNECTION_ID"]
deployment_model_name = os.environ["DEPLOYMENT_NAME"]

print(deployment_model_name)

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=project_endpoint,
)

bing = BingGroundingTool(connection_id=bing_connection_id)

agent = project.agents.create_agent(
    model=deployment_model_name,  # TODO: This is not setting the model correctly.
    name="Chat with Wiki Agent - SDK",
    instructions="""
You are a chatbot having a conversation with a human.
ALWAYS retrieve information from wikipedia, NEVER answer based simply on your knowledge.
Then given the response, create a final answer with references ("SOURCES").
If you don't know the answer, just say that you don't know. Don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.
""",
    description="A chatbot that retrieves information from Wikipedia and provides answers with sources.",
    tools=bing.definitions,
)

print(f"Created agent: '{agent.name}' with ID: {agent.id}")
