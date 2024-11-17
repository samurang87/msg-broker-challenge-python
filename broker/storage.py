from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class TimestampedMessage:
    message: str
    timestamp: str


class MessageStorage:
    def __init__(self, storage: "StorageClient"):
        self.storage = storage

    def publish(self, topic: str, message: str):
        self.storage.publish(topic, message)

    def get_messages(self, topic: str) -> list[str]:
        return self.storage.get_messages(topic)

    def get_topics(self) -> list[str]:
        return self.storage.get_topics()


class StorageClient(ABC):
    @abstractmethod
    def publish(self, topic: str, message: str):
        pass

    @abstractmethod
    def get_messages(self, topic: str) -> list[str]:
        pass

    @abstractmethod
    def get_topics(self) -> list[str]:
        pass


class InMemoryMessageStorage(StorageClient):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        self.topics = dict[str, deque[TimestampedMessage]]()

    def publish(self, topic: str, message: str):
        timestamped_message = TimestampedMessage(
            message=message,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self.topics[topic].append(timestamped_message)

    def get_messages(self, topic: str) -> list[TimestampedMessage]:
        # This is only used for testing, at this point
        return list(self.topics[topic])

    def get_topics(self) -> list[str]:
        return list(self.topics.keys())
