from typing import Annotated

from pydantic import BaseModel, Field


class PublishedMessage(BaseModel):
    topic: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=1024,
            pattern=r"^[a-zA-Z0-9_.\-/]+$",
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
