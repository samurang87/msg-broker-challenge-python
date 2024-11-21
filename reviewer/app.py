import logging

import requests
from fastapi import FastAPI

from common.models import TimestampedMessage, TopicSubscription
from reviewer.config import Settings


def create_app(file_logger: logging.Logger, stdout_logger: logging.Logger) -> FastAPI:
    reviewer_app = FastAPI()

    @reviewer_app.get("/status")
    async def status() -> dict[str, str]:
        return {"status": "ok"}

    @reviewer_app.post("/callback")
    async def callback(message: TimestampedMessage) -> dict[str, str]:
        file_logger.info("%s %s", message.timestamp, message.filepath)
        if "important" in message.filepath:
            stdout_logger.info(
                "%s %s %s", message.timestamp, message.filepath, message.message
            )
        return {}

    return reviewer_app


def subscribe_to_broker(settings: Settings, topic: str) -> dict[str, str]:
    subscription_data = TopicSubscription(
        topic=topic, callback_url=settings.CALLBACK_URL
    ).model_dump()
    response = requests.post(f"{settings.BROKER_URL}/subscribe", json=subscription_data)
    return response.json()
