import argparse
import os
import sys
import time

from watchdog.observers import Observer

from watcher.app import FileChangeHandler
from watcher.publisher_clients import FakePublisherClient, HTTPPublisherClient


def main():
    parser = argparse.ArgumentParser(
        description="Watch directory for file changes and publish to Pub/Sub"
    )
    parser.add_argument("directory", help="Directory to watch")
    parser.add_argument(
        "--pubsub-endpoint",
        default="localhost:8000",
        help="Pub/Sub endpoint",
    )
    parser.add_argument("--env", default="development", help="Environment")

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"Directory {args.directory} does not exist")
        return 1

    if args.env == "development":
        publisher_client = FakePublisherClient()
    elif args.env == "production":
        publisher_client = HTTPPublisherClient()
    else:
        print(f"Invalid environment: {args.env}")
        return 1

    event_handler = FileChangeHandler(
        args.pubsub_endpoint, args.directory, publisher_client
    )
    observer = Observer()
    observer.schedule(event_handler, args.directory, recursive=True)
    observer.start()

    print(f"Watching directory: {args.directory}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        sys.exit(0)


if __name__ == "__main__":
    main()
