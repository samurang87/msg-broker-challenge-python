from abc import ABC, abstractmethod

import requests

from common.models import TimestampedMessage


class SenderClient(ABC):
    @abstractmethod
    def send(self, message: TimestampedMessage, callback_url: str) -> str:
        pass


class TestSenderClient(SenderClient):
    def __init__(self):
        self.sent_messages: list[tuple[TimestampedMessage, str]] = []

    def send(self, message: TimestampedMessage, callback_url: str) -> str:
        self.sent_messages.append((message, callback_url))
        return "ack"

    def check_message_sent(
        self, message: TimestampedMessage, callback_url: str
    ) -> bool:
        return (message, callback_url) in self.sent_messages


class HTTPSenderClient(SenderClient):
    def send(self, message: TimestampedMessage, callback_url: str) -> str:
        response = requests.post(callback_url, json=message.model_dump())
        if response.ok:
            return "ack"
        else:
            print(f"Error sending message: {response.text}")
