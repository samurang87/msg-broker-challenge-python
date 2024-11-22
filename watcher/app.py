import difflib
import logging
from datetime import datetime
from pathlib import Path

import requests
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from common.models import TimestampedMessage
from watcher.publisher_clients import PublisherClient

logger = logging.getLogger("watcher_app_logger")


class FileChangeHandler(FileSystemEventHandler):
    def __init__(
        self, pubsub_endpoint: str, watch_dir: str, publisher_client: PublisherClient
    ):
        self.pubsub_endpoint = pubsub_endpoint
        self.watch_dir = Path(watch_dir)
        self.cached_content: dict[str, str] = {}
        self._initialize_cache()
        self.publisher_client = publisher_client

    def _initialize_cache(self) -> None:
        logger.info(f"Initializing cache for {self.watch_dir}")
        for filepath in self.watch_dir.rglob("*"):
            logger.info(f"Caching file {filepath}")
            if filepath.is_file():
                content = self._get_file_content(str(filepath))
                if content is not None:
                    self.cached_content[str(filepath)] = content
        logger.info(f"Cache initialized with {len(self.cached_content)} files")

    @staticmethod
    def _get_file_content(filepath: str) -> str | None:
        try:
            with open(filepath) as f:
                return f.read()
        except Exception:
            logger.exception("Error reading file: %s", filepath)
            return None

    @staticmethod
    def _calculate_diff(old_content: str, new_content: str) -> str:
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True), new_content.splitlines(keepends=True)
        )
        return "".join(diff)

    def _publish_message(self, filepath: str, message: str, timestamp: str):
        try:
            payload = TimestampedMessage(
                filepath=filepath, message=message, timestamp=timestamp
            )
            logger.info(f"Publishing message {message} to topic {filepath}")
            self.publisher_client.publish(payload, f"{self.pubsub_endpoint}")
        except requests.exceptions.HTTPError:
            logger.exception("HTTP error occurred")
        except requests.exceptions.RequestException:
            logger.exception("Error publishing message")

    def on_modified(self, event: FileSystemEvent) -> None:
        timestamp = datetime.now().isoformat()

        if event.is_directory:
            return

        filepath = str(event.src_path)
        if filepath not in self.cached_content:
            logger.info("Ignoring modification of not cached file: %s", filepath)
            return

        new_content = self._get_file_content(filepath)
        if new_content is None:
            return

        old_content = self.cached_content[filepath]

        if new_content != old_content:
            logger.info("Detected change in %s", filepath)
            diff = self._calculate_diff(old_content, new_content)
            self._publish_message(filepath, diff, timestamp)
            self.cached_content[filepath] = new_content
