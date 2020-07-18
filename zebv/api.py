import requests


class ApiClient:
    def __init__(self, base_url, api_key):
        self.session = requests.Session()
        self.base_url = base_url
        self.api_key = api_key

    def _post(self, endpoint: str, data) -> str:
        response: requests.Response = self.session.post(
            self.base_url + endpoint, data=data, params={"apiKey": self.api_key}
        )
        response.raise_for_status()
        return response.text

    def aliens_send(self, data: str) -> str:
        return self._post("aliens/send", data)
