import pytest
from fastapi.testclient import TestClient

from broker.app import create_app as create_broker_app
from broker.config import get_settings
from broker.sender_clients import TestSenderClient
from broker.storage import InMemoryMessageStorage


@pytest.fixture
def storage_client():
    return InMemoryMessageStorage()


@pytest.fixture
def sender_client():
    return TestSenderClient()


@pytest.fixture
def broker_client(storage_client, sender_client):
    settings = get_settings()
    app = create_broker_app(settings, storage_client, sender_client)
    return TestClient(app)
