from pathlib import Path

from src.config.settings import Settings
from src.llm_client import AzureAIFoundry
from src.powerbi_client import PowerBIClient
from orchestrator import NexusNotebookOrchestrator


def load_semantic_context(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def build_orchestrator(
    semantic_context_path: str,
    general_syn: str = "",
    dav: str = "",
) -> NexusNotebookOrchestrator:
    settings = Settings()
    settings.validate()

    semantic_context = load_semantic_context(semantic_context_path)

    llm_client = AzureAIFoundry(
        endpoint=settings.foundry_endpoint,
        api_key=settings.foundry_api_key,
        deployment=settings.foundry_model,
        api_version=settings.foundry_api_version,
    )

    pbi_client = PowerBIClient(
        tenant_id=settings.pbi_tenant_id,
        client_id=settings.pbi_client_id,
        client_secret=settings.pbi_client_secret,
        group_id=settings.pbi_group_id,
        dataset_id=settings.pbi_dataset_id,
    )

    return NexusNotebookOrchestrator(
        llm_client=llm_client,
        pbi_client=pbi_client,
        semantic_context=semantic_context,
        general_syn=general_syn,
        dav=dav,
        log_level=settings.app_log_level,
    )