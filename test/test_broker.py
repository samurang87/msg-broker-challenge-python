from fastapi import status


def test_status_endpoint(broker_client):
    response = broker_client.get("/status")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_publish_endpoint(broker_client, storage_client):
    storage_client.topics["test-topic"] = []

    response = broker_client.post(
        "/publish", json={"topic": "test-topic", "message": "This is a test message"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "published"}

    response = broker_client.post(
        "/publish", json={"topic": "test-topic-2", "message": "This is a test message"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "topic_not_found"}
