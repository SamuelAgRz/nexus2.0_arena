class DaxExecutorAgent:
    def __init__(self, nsr_conn):
        self.nsr_conn = nsr_conn

    def run(self, dax_query: str):
        if not dax_query or not dax_query.strip():
            raise ValueError("DAX query is empty. Cannot execute.")

        if dax_query.strip().upper() == "APPROVED":
            raise ValueError("Received validator output instead of DAX query.")

        if dax_query.strip().upper().startswith("NOT APPROVED"):
            raise ValueError("Cannot execute a DAX query that was not approved.")

        result_df = self.nsr_conn.ejecutar_query(dax_query)

        if result_df is None:
            raise RuntimeError("DAX execution failed. Check ADOMD connection or query syntax.")

        return result_df