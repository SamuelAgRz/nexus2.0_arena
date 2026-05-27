import json

from src.prompts.latam_nsr_ontology_developer import ONTOLOGY_DEVELOPER_PROMPT


class LatamNsrOntologyDeveloperAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def _build_user_prompt(self, ontology_filter: dict) -> str:
        return (
            "Build the DAX query for the following ontology filter:\n\n"
            + json.dumps(ontology_filter, ensure_ascii=False, indent=2)
        )

    def _build_revision_prompt(
        self, previous_dax: str, validator_feedback: str, ontology_filter: dict
    ) -> str:
        return (
            "The following DAX query was rejected by the validator.\n\n"
            f"Ontology filter:\n{json.dumps(ontology_filter, ensure_ascii=False, indent=2)}\n\n"
            f"Previous DAX:\n{previous_dax}\n\n"
            f"Validator feedback:\n{validator_feedback}\n\n"
            "Fix the issues and return ONLY the corrected DAX query starting with EVALUATE."
        )

    def run(self, ontology_filter: dict) -> str:
        user_prompt = self._build_user_prompt(ontology_filter)
        return self.llm.chat(
            system_prompt=ONTOLOGY_DEVELOPER_PROMPT,
            user_prompt=user_prompt,
        ).strip()

    def revise(
        self, previous_dax: str, validator_feedback: str, ontology_filter: dict
    ) -> str:
        user_prompt = self._build_revision_prompt(previous_dax, validator_feedback, ontology_filter)
        return self.llm.chat(
            system_prompt=ONTOLOGY_DEVELOPER_PROMPT,
            user_prompt=user_prompt,
        ).strip()
