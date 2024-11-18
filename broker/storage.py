from abc import ABC, abstractmethod
from collections import defaultdict, deque
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime

from broker.models import TopicSubscription


@dataclass
class TimestampedMessage:
    message: str
    timestamp: str


class MessageStorage:
    def __init__(self, storage: "StorageClient"):
        self.storage = storage

    def consume(self, topic: str) -> Iterator[tuple[TimestampedMessage, str]]:
        return self.storage.consume(topic)

    def publish(self, topic: str, message: str):
        self.storage.publish(topic, message)

    def get_matching_topics(self, topic: str) -> list[str]:
        return self.storage.get_matching_topics(topic)

    def get_topics(self) -> list[str]:
        return self.storage.get_topics()

    def subscribe(self, subscription: TopicSubscription):
        return self.storage.subscribe(subscription)


class StorageClient(ABC):
    @abstractmethod
    def consume(self, topic: str):
        pass

    @abstractmethod
    def get_matching_topics(self, topic: str) -> list[str]:
        pass

    @abstractmethod
    def publish(self, topic: str, message: str):
        pass

    @abstractmethod
    def get_topics(self) -> list[str]:
        pass

    @abstractmethod
    def subscribe(self, subscription: TopicSubscription):
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
        self.subscriptions = defaultdict(list[str])

    def consume(self, topic: str) -> Iterator[tuple[TimestampedMessage, str]]:
        while self.topics[topic]:
            message = self.topics[topic].popleft()
            for callback_url in self.subscriptions[topic]:
                yield message, callback_url

    def get_matching_topics(self, topic: str) -> list[str]:
        matching_topics = []
        for available_topic in self.get_topics():
            if available_topic == topic:
                matching_topics.append(available_topic)
            if "~" in available_topic and topic.startswith(available_topic[:-1]):
                matching_topics.append(available_topic)
        return matching_topics

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

    def subscribe(self, subscription: TopicSubscription):
        self.subscriptions[subscription.topic].append(subscription.callback_url)
        self.topics[subscription.topic] = deque()
