import pytest
from fastapi.testclient import TestClient

from broker.app import app as broker_app


@pytest.fixture
def broker_client() -> TestClient:
    return TestClient(broker_app)
