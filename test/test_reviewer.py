import logging

from common.models import TimestampedMessage


def test_callback_with_important(reviewer_client, caplog):
    message = TimestampedMessage(
        filepath="important/file.txt",
        message="Test message",
        timestamp="2023-10-10T10:00:00Z",
    )
    with caplog.at_level(logging.DEBUG, logger="reviewer_app"):
        response = reviewer_client.post("/callback", json=message.model_dump())
        assert response.status_code == 200
        assert "important/file.txt" in caplog.text
        assert "Test message" in caplog.text


def test_callback_without_important(reviewer_client, caplog):
    message = TimestampedMessage(
        filepath="regular/file.txt",
        message="Test message",
        timestamp="2023-10-10T10:00:00Z",
    )
    with caplog.at_level(logging.DEBUG, logger="reviewer_app"):
        response = reviewer_client.post("/callback", json=message.model_dump())
        assert response.status_code == 200
        assert "regular/file.txt" in caplog.text
        assert "Test message" not in caplog.text
