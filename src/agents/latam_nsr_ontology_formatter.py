import pandas as pd

from src.prompts.latam_nsr_ontology_formatter import ONTOLOGY_FORMATTER_PROMPT


class LatamNsrOntologyFormatterAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def run(self, business_question: str, df_result: pd.DataFrame) -> str:
        table_str = df_result.to_string(index=False)
        user_prompt = (
            f"User's business question:\n{business_question}\n\n"
            f"Ontology KPI rows:\n{table_str}"
        )
        return self.llm.chat(
            system_prompt=ONTOLOGY_FORMATTER_PROMPT,
            user_prompt=user_prompt,
        ).strip()
