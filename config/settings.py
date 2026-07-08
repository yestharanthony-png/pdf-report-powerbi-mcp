"""Centralized, typed application settings loaded from .env."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Azure OpenAI
    azure_openai_api_key: str = Field(..., alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str = Field(..., alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment: str = Field("gpt-4o-mini", alias="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = Field("2024-08-01-preview", alias="AZURE_OPENAI_API_VERSION")

    # Power BI
    powerbi_client_id: str = Field(..., alias="POWERBI_CLIENT_ID")
    powerbi_client_secret: str = Field(..., alias="POWERBI_CLIENT_SECRET")
    powerbi_tenant_id: str = Field(..., alias="POWERBI_TENANT_ID")
    powerbi_workspace_id: str = Field(..., alias="POWERBI_WORKSPACE_ID")

    log_level: str = Field("INFO", alias="LOG_LEVEL")
    generated_dir_name: str = Field("generated", alias="GENERATED_DIR")

    class Config:
        populate_by_name = True
        extra = "ignore"

    @property
    def generated_dir(self) -> Path:
        return BASE_DIR / self.generated_dir_name

    @property
    def charts_dir(self) -> Path:
        d = self.generated_dir / "charts"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def reports_dir(self) -> Path:
        d = self.generated_dir / "reports"
        d.mkdir(parents=True, exist_ok=True)
        return d


settings = Settings()
