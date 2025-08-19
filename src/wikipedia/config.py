from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv

azure_token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

dotenv_path = find_dotenv()


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=dotenv_path, env_file_encoding="utf-8", extra="allow"
    )

    APPLICATIONINSIGHTS_CONNECTIONSTRING: str = Field(
        ..., alias="APPLICATIONINSIGHTS_CONNECTIONSTRING"
    )

    AZURE_OPENAI_API_VERSION: str = Field(
        default="2024-12-01-preview", alias="AZURE_OPENAI_API_VERSION"
    )
    AZURE_OPENAI_ENDPOINT: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(
        default="gpt-4.1-mini", alias="AZURE_OPENAI_DEPLOYMENT_NAME"
    )
    AZURE_AI_PROJECT_ENDPOINT: str = Field(
        default="https://{your-custom-endpoint}.openai.azure.com/",
        alias="AZURE_AI_PROJECT_ENDPOINT",
    )


config = Config()  # type: ignore
