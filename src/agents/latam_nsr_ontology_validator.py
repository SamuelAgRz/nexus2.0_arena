import json

from src.prompts.latam_nsr_ontology_validator import ONTOLOGY_VALIDATOR_PROMPT


class LatamNsrOntologyValidatorAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def run(self, dax_query: str, ontology_filter: dict) -> str:
        user_prompt = (
            f"Ontology filter requested:\n"
            f"{json.dumps(ontology_filter, ensure_ascii=False, indent=2)}\n\n"
            f"DAX query to validate:\n{dax_query}"
        )
        return self.llm.chat(
            system_prompt=ONTOLOGY_VALIDATOR_PROMPT,
            user_prompt=user_prompt,
        ).strip()
