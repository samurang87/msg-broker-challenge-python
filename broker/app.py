from fastapi import FastAPI

from broker.config import Settings, get_settings
from broker.models import PublishedMessage, TopicSubscription
from broker.sender_clients import SenderClient, TestSenderClient
from broker.storage import InMemoryMessageStorage, MessageStorage, StorageClient


def get_sender(settings: Settings) -> SenderClient:
    if settings.ENVIRONMENT == "development":
        return TestSenderClient()
    else:
        raise NotImplementedError("Only 'development' environment is supported")


def get_storage() -> StorageClient:
    return InMemoryMessageStorage()


def create_app(
    settings: Settings, storage_client: StorageClient, sender_client: SenderClient
) -> FastAPI:
    broker_app = FastAPI(
        title=settings.APP_NAME,
    )

    message_storage = MessageStorage(storage_client)

    @broker_app.get("/status")
    async def status():
        return {"status": "ok"}

    @broker_app.post("/publish")
    async def publish(message: PublishedMessage):
        if matching_topics := message_storage.get_matching_topics(message.topic):
            for matching_topic in matching_topics:
                message_storage.publish(matching_topic, message.message)
                for msg, callback_url in message_storage.consume(matching_topic):
                    sender_client.send(msg.message, callback_url)
        else:
            return {"status": "topic_not_found"}

        return {"status": "published"}

    @broker_app.post("/subscribe")
    async def subscribe(subscription: TopicSubscription):
        message_storage.subscribe(subscription)
        return {"status": "subscribed"}

    return broker_app


settings = get_settings()
storage_client = get_storage()


sender_client = get_sender(settings)
app = create_app(settings, storage_client, sender_client)
