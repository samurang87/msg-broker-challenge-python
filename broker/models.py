from typing import Annotated

from pydantic import BaseModel, Field


class TopicSubscription(BaseModel):
    topic: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=100,
            pattern=r"^[a-zA-Z0-9_.-]+$",
            examples=["my-topic", "user.notifications"],
        ),
    ]
    callback_url: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["http://localhost:8000/notifications"],
    )

    model_config = {"str_strip_whitespace": True}


class PublishedMessage(BaseModel):
    topic: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=100,
            pattern=r"^[a-zA-Z0-9_.-]+$",
            examples=["my-topic", "user.notifications"],
        ),
    ]
    message: Annotated[
        str,
        Field(
            ...,
            max_length=1024 * 1024,  # 1MB limit
            examples=["This is a test message"],
        ),
    ]

    model_config = {"str_strip_whitespace": True}
