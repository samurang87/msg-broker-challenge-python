from fastapi import FastAPI

from broker.config import Settings, get_settings
from broker.models import PublishedMessage


def create_app(settings: Settings) -> FastAPI:
    broker_app = FastAPI(
        title=settings.APP_NAME,
    )

    @broker_app.get("/status")
    async def status():
        return {"status": "ok"}

    @broker_app.post("/publish")
    async def publish(message: PublishedMessage):
        print(f"Publishing message to topic {message.topic}: {message.message}")
        return {"status": "ok"}

    return broker_app


app = create_app(get_settings())
