from abc import ABC, abstractmethod

import requests

from common.models import TimestampedMessage


class PublisherClient(ABC):
    @abstractmethod
    def publish(self, message: TimestampedMessage, url: str) -> None:
        pass


class FakePublisherClient(PublisherClient):
    def __init__(self):
        self.published_messages: list[tuple[TimestampedMessage, str]] = []

    def publish(self, message: TimestampedMessage, url: str) -> None:
        self.published_messages.append((message, url))

    def one_message_published(self) -> bool:
        return len(self.published_messages) == 1

    def no_message_published(self) -> bool:
        return len(self.published_messages) == 0


class HTTPPublisherClient(PublisherClient):
    def publish(self, message: TimestampedMessage, url: str) -> None:
        response = requests.post(
            url,
            json=message.model_dump(),
        )
        response.raise_for_status()
