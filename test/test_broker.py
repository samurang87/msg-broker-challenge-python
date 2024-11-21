import logging
from collections import deque

import pytest
from fastapi import status

from common.models import TimestampedMessage


@pytest.fixture(autouse=True)
def suppress_logs(caplog):
    caplog.set_level(logging.CRITICAL)


def test_status_endpoint(broker_client):
    response = broker_client.get("/status")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_publish_endpoint(broker_client, storage_client, sender_client):
    storage_client.topics["test-topic"] = deque()
    callback_url = "http://localhost:8000/notifications"
    storage_client.subscriptions["test-topic"] = [callback_url]

    message = TimestampedMessage(
        filepath="test-topic",
        message="This is a test message",
        timestamp="2021-01-01T00:00:00",
    )
    response = broker_client.post(
        "/publish",
        json=message.model_dump(),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "published"}
    assert sender_client.check_message_sent(message, callback_url)
    assert not storage_client.get_messages("test-topic")

    message.filepath = "test-topic-2"
    response = broker_client.post("/publish", json=message.model_dump())
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "topic_not_found"}
    assert not storage_client.get_messages("test-topic")


def test_publish_endpoint__matches_wildcard_subscriptions(
    broker_client, storage_client, sender_client
):
    storage_client.topics["test-to~"] = deque()
    callback_url = "http://localhost:8000/notifications"
    storage_client.topics["test-topic"] = deque()
    callback_url2 = "http://localhost:8000/notifications2"
    storage_client.subscriptions["test-to~"] = [callback_url]
    storage_client.subscriptions["test-topic"] = [callback_url2]

    message = TimestampedMessage(
        filepath="test-topic",
        message="This is a test message",
        timestamp="2021-01-01T00:00:00",
    )
    response = broker_client.post("/publish", json=message.model_dump())
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "published"}
    assert sender_client.check_message_sent(message, callback_url)
    assert sender_client.check_message_sent(message, callback_url2)


def test_subscribe_endpoint(broker_client, storage_client):
    response = broker_client.post(
        "/subscribe",
        json={
            "topic": "test-topic",
            "callback_url": "http://localhost:8000/notifications",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "subscribed"}

    assert storage_client.subscriptions["test-topic"] == [
        "http://localhost:8000/notifications"
    ]
    assert "test-topic" in storage_client.get_topics()
