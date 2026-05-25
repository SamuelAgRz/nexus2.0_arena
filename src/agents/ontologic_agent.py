class OntologicAgent:
    """
    Queries the NSR ontology dataset and returns relevant KPI/measure/column
    metadata for a given user query. Used to enrich downstream agents with
    live context after the Intent Clarifier resolves the user's intent.
    """

    def __init__(self, llm_client, ontology_conn):
        self.llm = llm_client
        self.ontology_conn = ontology_conn

    def _fetch_ontology(self, ontology_filter: list) -> str:
        # TODO: When the hierarchy/category column is defined in 'kpi_documentation 1',
        #       replace the query below with a filtered version, e.g.:
        #
        #   values = ", ".join(f'"{v}"' for v in ontology_filter)
        #   dax = f"""
        #   EVALUATE
        #   FILTER(
        #       'kpi_documentation 1',
        #       'kpi_documentation 1'[<hierarchy_col>] IN {{{{{values}}}}}
        #   )
        #   """
        #
        # For now, fetch all rows (no hierarchy filter column available yet):
        dax = "EVALUATE VALUES('kpi_documentation 1')"
        df = self.ontology_conn.ejecutar_query(dax)
        if df is None or df.empty:
            return ""
        return df.to_string(index=False)

    def run(self, ontology_filter: list) -> str:
        return self._fetch_ontology(ontology_filter)
