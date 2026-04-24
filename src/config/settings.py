import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    foundry_endpoint: str = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT", "")
    foundry_api_key: str = os.getenv("AZURE_AI_FOUNDRY_API_KEY", "")
    foundry_model: str = os.getenv("AZURE_AI_FOUNDRY_DEPLOYMENT", "gpt-5-mini")
    foundry_api_version: str = os.getenv("AZURE_AI_FOUNDRY_API_VERSION", "2024-12-01-preview")

    pbi_tenant_id: str = os.getenv("PBI_TENANT_ID", "")
    pbi_client_id: str = os.getenv("PBI_CLIENT_ID", "")
    pbi_client_secret: str = os.getenv("PBI_CLIENT_SECRET", "")
    pbi_group_id: str = os.getenv("PBI_GROUP_ID", "")
    pbi_dataset_id: str = os.getenv("PBI_DATASET_ID", "")

    app_log_level: str = os.getenv("APP_LOG_LEVEL", "INFO")

    def validate(self) -> None:
        required = {
            "AZURE_AI_FOUNDRY_ENDPOINT": self.foundry_endpoint,
            "AZURE_AI_FOUNDRY_API_KEY": self.foundry_api_key,
            "AZURE_AI_FOUNDRY_DEPLOYMENT": self.foundry_model,
            "PBI_TENANT_ID": self.pbi_tenant_id,
            "PBI_CLIENT_ID": self.pbi_client_id,
            "PBI_CLIENT_SECRET": self.pbi_client_secret,
            "PBI_GROUP_ID": self.pbi_group_id,
            "PBI_DATASET_ID": self.pbi_dataset_id,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")