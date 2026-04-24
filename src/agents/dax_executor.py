
class DaxExecutorAgent:
    def __init__(self, pbi_client):
        self.pbi = pbi_client

    def run(self, dax_query: str) -> dict:
        return self.pbi.execute_dax(dax_query)
