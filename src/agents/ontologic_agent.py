from src.prompts.ontologic_agent import ONTOLOGIC_AGENT_PROMPT


class OntologicAgent:
    """
    Queries the NSR ontology dataset and returns relevant KPI/measure/column
    metadata for a given user query. Used to enrich the Intent Clarifier with
    live context before each pass.
    """

    _DAX_QUERY = "EVALUATE VALUES('kpi_documentation 1')"

    def __init__(self, llm_client, ontology_conn):
        self.llm = llm_client
        self.ontology_conn = ontology_conn

    def _fetch_ontology(self) -> str:
        df = self.ontology_conn.ejecutar_query(self._DAX_QUERY)
        if df is None or df.empty:
            return ""
        return df.to_string(index=False)

    def _extract_relevant_context(self, ontology_raw: str, user_query: str) -> str:
        user_prompt = (
            f"User query:\n{user_query}\n\n"
            f"Ontology data:\n{ontology_raw}"
        )
        return self.llm.chat(
            system_prompt=ONTOLOGIC_AGENT_PROMPT,
            user_prompt=user_prompt,
        ).strip()

    def run(self, user_query: str) -> str:
        ontology_raw = self._fetch_ontology()
        if not ontology_raw:
            return ""
        return self._extract_relevant_context(ontology_raw, user_query)
