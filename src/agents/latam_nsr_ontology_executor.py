import pandas as pd


class LatamNsrOntologyExecutorAgent:
    def __init__(self, ontology_conn):
        self.ontology_conn = ontology_conn

    def run(self, dax_query: str) -> pd.DataFrame:
        if not dax_query or not dax_query.strip():
            raise ValueError("Ontology DAX query is empty. Cannot execute.")

        if not dax_query.strip().upper().startswith("EVALUATE"):
            raise ValueError("Ontology DAX query must start with EVALUATE.")

        df = self.ontology_conn.ejecutar_query(dax_query)

        if df is None or df.empty:
            raise ValueError(
                "Ontology query returned no results. Check filter values or table availability."
            )

        return df
