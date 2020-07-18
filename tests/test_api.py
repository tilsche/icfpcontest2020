import os
from logging import DEBUG, getLogger

import pytest
from zebv.api import ApiClient
from zebv.interact import Interaction

logger = getLogger(__name__)


@pytest.fixture
def api_client():
    yield ApiClient("https://icfpc2020-api.testkontur.ru/", os.environ["PLAYER_KEY"])


def test_interact(caplog, api_client, statefuldraw):
    with caplog.at_level(DEBUG):
        logger.debug(f"Connected to {api_client.base_url}")
        i = Interaction(
            statefuldraw, "statefuldraw", send_function=api_client.aliens_send
        )
        i(4, 8)
        i(7, 7)
        i(12, 14)
