import logging

from fastapi import FastAPI

from broker.config import Settings, get_settings
from broker.sender_clients import HTTPSenderClient, SenderClient, TestSenderClient
from broker.storage import InMemoryMessageStorage, MessageStorage, StorageClient
from common.models import TimestampedMessage, TopicSubscription


def get_sender(settings: Settings) -> SenderClient:
    if settings.ENVIRONMENT == "development":
        return TestSenderClient()
    else:
        return HTTPSenderClient()


def get_storage() -> StorageClient:
    return InMemoryMessageStorage()


def create_app(
    settings: Settings, storage_client: StorageClient, sender_client: SenderClient
) -> FastAPI:
    broker_app = FastAPI(
        title=settings.APP_NAME,
    )

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("broker_app_logger")

    message_storage = MessageStorage(storage_client)

    @broker_app.get("/status")
    async def status() -> dict[str, str]:
        return {"status": "ok"}

    @broker_app.post("/publish")
    async def publish(message: TimestampedMessage) -> dict[str, str]:
        logger.debug(
            "Received message: %s in topic %s", message.message, message.filepath
        )
        if matching_topics := message_storage.get_matching_topics(message.filepath):
            for matching_topic in matching_topics:
                message_storage.publish(topic=matching_topic, message=message)
                for msg, callback_url in message_storage.consume(matching_topic):
                    logger.debug("Sending message %s to %s", msg.message, callback_url)
                    sender_client.send(msg, callback_url)
        else:
            return {"status": "topic_not_found"}

        return {"status": "published"}

    @broker_app.post("/subscribe")
    async def subscribe(subscription: TopicSubscription) -> dict[str, str]:
        logger.debug(
            "%s subscribed to %s", subscription.callback_url, subscription.topic
        )
        message_storage.subscribe(subscription)
        return {"status": "subscribed"}

    return broker_app


settings = get_settings()
storage_client = get_storage()


sender_client = get_sender(settings)
app = create_app(settings, storage_client, sender_client)
