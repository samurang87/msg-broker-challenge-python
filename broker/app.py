from fastapi import FastAPI

from broker.config import Settings, get_settings
from broker.models import PublishedMessage, TopicSubscription
from broker.storage import InMemoryMessageStorage, MessageStorage, StorageClient


def get_storage(settings: Settings) -> StorageClient:
    if settings.ENVIRONMENT == "development":
        return InMemoryMessageStorage()
    else:
        raise NotImplementedError("Only 'development' environment is supported")


def create_app(settings: Settings, storage_client: StorageClient) -> FastAPI:
    broker_app = FastAPI(
        title=settings.APP_NAME,
    )

    message_storage = MessageStorage(storage_client)

    @broker_app.get("/status")
    async def status():
        return {"status": "ok"}

    @broker_app.post("/publish")
    async def publish(message: PublishedMessage):
        if message.topic in message_storage.get_topics():
            message_storage.publish(message.topic, message.message)
            return {"status": "published"}
        else:
            return {"status": "topic_not_found"}

    @broker_app.post("/subscribe")
    async def subscribe(subscription: TopicSubscription):
        message_storage.subscribe(subscription)
        return {"status": "subscribed"}

    return broker_app


settings = get_settings()
storage_client = get_storage(settings)
app = create_app(settings, storage_client)
