from typing import Annotated

from pydantic import BaseModel, Field


class TimestampedMessage(BaseModel):
    filepath: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=1024,
            pattern=r"^[a-zA-Z0-9_.\-/]+$",
            examples=["/some/path.file.txt", "user/name.md"],
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
    timestamp: Annotated[
        str,
        Field(
            ...,
            max_length=64,
            examples=["2021-01-01T12:00:00Z"],
        ),
    ]

    model_config = {"str_strip_whitespace": True}


class TopicSubscription(BaseModel):
    topic: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=1024,
            pattern=r"^[a-zA-Z0-9_.\-/~]+$",
            examples=["/tmp/", "some/file.txt"],
        ),
    ]
    callback_url: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["http://localhost:8000/notifications"],
    )

    model_config = {"str_strip_whitespace": True}
