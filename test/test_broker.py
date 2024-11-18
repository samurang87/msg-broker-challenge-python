from collections import deque

from fastapi import status


def test_status_endpoint(broker_client):
    response = broker_client.get("/status")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_publish_endpoint(broker_client, storage_client, sender_client):
    storage_client.topics["test-topic"] = deque()
    callback_url = "http://localhost:8000/notifications"
    storage_client.subscriptions["test-topic"] = [callback_url]

    message = "This is a test message"
    response = broker_client.post(
        "/publish", json={"topic": "test-topic", "message": message}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "published"}
    assert sender_client.check_message_sent(message, callback_url)
    assert not storage_client.get_messages("test-topic")

    response = broker_client.post(
        "/publish", json={"topic": "test-topic-2", "message": "This is a test message"}
    )
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

    message = "This is a test message"
    response = broker_client.post(
        "/publish", json={"topic": "test-topic", "message": message}
    )
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
