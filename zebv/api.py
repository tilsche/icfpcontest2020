from logging import getLogger
from urllib.parse import urljoin

import requests

logger = getLogger(__name__)


class ApiClient:
    def __init__(self, base_url, api_key):
        self.session = requests.Session()
        self.base_url = base_url
        self.api_key = api_key

    def _post(self, endpoint: str, data) -> str:
        params = {"apiKey": self.api_key} if self.api_key else None
        response: requests.Response = self.session.post(
            urljoin(self.base_url, endpoint), data=data, params=params
        )
        response.raise_for_status()
        return response.text

    def aliens_send(self, data: str) -> str:
        logger.debug(f"aliens_send({data!r}) ~~~>")
        response = self._post("/aliens/send", data)
        logger.debug(f"{response!r} <~~~~")
        return response
