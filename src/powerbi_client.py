import requests

class PowerBIClient:
    AUTH_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    SCOPE = "https://analysis.windows.net/powerbi/api/.default"
    API_ROOT = "https://api.powerbi.com/v1.0/myorg"

    def __init__(self, tenant_id, client_id, client_secret, group_id, dataset_id):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.group_id = group_id
        self.dataset_id = dataset_id
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        url = self.AUTH_URL.format(tenant_id=self.tenant_id)
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.SCOPE
        }
        return requests.post(url, data=data).json()["access_token"]

    def execute_dax(self, dax_query):
        url = f"{self.API_ROOT}/groups/{self.group_id}/datasets/{self.dataset_id}/executeQueries"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"queries": [{"query": dax_query}]}
        return requests.post(url, headers=headers, json=payload).json()
