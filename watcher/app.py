import difflib
from pathlib import Path

import requests
from watchdog.events import FileSystemEventHandler


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, pubsub_endpoint: str, watch_dir: str):
        self.pubsub_endpoint = pubsub_endpoint
        self.watch_dir = Path(watch_dir)
        self.cached_content: dict[str, str] = {}
        self._initialize_cache()

    def _initialize_cache(self):
        """Initialize cache with all existing files content"""
        print("Initializing cache...")
        for filepath in self.watch_dir.rglob("*"):
            if filepath.is_file():
                content = self._get_file_content(str(filepath))
                if content is not None:
                    self.cached_content[str(filepath)] = content
        print(f"Cache initialized with {len(self.cached_content)} files")

    def _get_file_content(self, filepath: str) -> str | None:
        try:
            with open(filepath) as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None

    def _calculate_diff(self, old_content: str, new_content: str) -> str:
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True), new_content.splitlines(keepends=True)
        )
        return "".join(diff)

    def _publish_message(self, topic: str, message: str):
        try:
            payload = {"messages": [{"data": message.encode("utf-8").hex()}]}
            response = requests.post(
                f"{self.pubsub_endpoint}/topics/{topic}:publish", json=payload
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error publishing message: {e}")

    def on_modified(self, event):
        if event.is_directory:
            return

        filepath = str(event.src_path)
        if filepath not in self.cached_content:
            print(f"Ignoring modification of uncached file: {filepath}")
            return

        new_content = self._get_file_content(filepath)
        if new_content is None:
            return

        old_content = self.cached_content[filepath]
        if new_content != old_content:
            diff = self._calculate_diff(old_content, new_content)
            topic = filepath.replace("/", "_").lstrip("_")
            self._publish_message(topic, diff)
            self.cached_content[filepath] = new_content
