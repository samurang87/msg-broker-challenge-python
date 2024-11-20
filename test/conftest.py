import logging

import pytest
from fastapi.testclient import TestClient

from broker.app import create_app as create_broker_app
from broker.config import get_settings
from broker.sender_clients import TestSenderClient
from broker.storage import InMemoryMessageStorage
from reviewer.app import create_app as create_reviewer_app
from watcher.app import FileChangeHandler
from watcher.publisher_clients import FakePublisherClient


# Broker application fixtures
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


# Watcher application fixtures
@pytest.fixture
def publisher_client():
    return FakePublisherClient()


@pytest.fixture(scope="function", autouse=True)
def temp_file(tmp_path):
    # Create the directory if it doesn't exist
    temp_dir = tmp_path / "path" / "to"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Create a temporary file at the specified path
    temp_file_path = temp_dir / "file1.txt"
    temp_file_path.write_text("Content of file1")

    yield str(temp_file_path)


@pytest.fixture
def cached_content(temp_file):
    return {
        temp_file: "Content of file1",
        "/path/to/file2.txt": "Content of file2",
    }


@pytest.fixture
def file_change_handler(publisher_client, cached_content):
    handler = FileChangeHandler("localhost:8000", ".", publisher_client)
    handler.cached_content = cached_content

    yield handler


@pytest.fixture
def reviewer_client(caplog):
    caplog.set_level(logging.INFO)
    logger = logging.getLogger("test_reviewer")
    logger.handlers = []
    app = create_reviewer_app(logger, logger)
    return TestClient(app)
