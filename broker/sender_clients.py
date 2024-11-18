from abc import ABC, abstractmethod

import requests


class SenderClient(ABC):
    @abstractmethod
    def send(self, message: str, callback_url: str):
        pass


class TestSenderClient(SenderClient):
    def __init__(self):
        self.sent_messages: list[tuple[str, str]] = []

    def send(self, message: str, callback_url: str) -> str:
        self.sent_messages.append((message, callback_url))
        return "ack"

    def check_message_sent(self, message: str, callback_url: str):
        return (message, callback_url) in self.sent_messages


class HTTPSenderClient(SenderClient):
    def send(self, message: str, callback_url: str):
        response = requests.post(callback_url, json={"message": message})
        if response.ok:
            return "ack"
        else:
            print(f"Error sending message: {response.text}")
