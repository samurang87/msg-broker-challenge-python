from fastapi import FastAPI

from broker.config import Settings, get_settings


def create_app(settings: Settings) -> FastAPI:
    broker_app = FastAPI(
        title=settings.APP_NAME,
    )

    @broker_app.get("/status")
    async def status():
        return {"status": "ok"}

    return broker_app


app = create_app(get_settings())
