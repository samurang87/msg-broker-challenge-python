import argparse

import uvicorn

from reviewer.app import create_app, subscribe_to_broker
from reviewer.config import LoggerConfig, Settings


def main():
    stdout_logger = LoggerConfig.get_stdout_logger("reviewer_app")
    parser = argparse.ArgumentParser(description="Start the reviewer application")
    parser.add_argument("topics", nargs="+", help="List of topics to subscribe to")
    args = parser.parse_args()

    settings = Settings()
    stdout_logger.info("Starting reviewer application...")
    stdout_logger.info("Subscribing to topics: %s", args.topics)

    for topic in args.topics:
        result = subscribe_to_broker(settings, topic)
        stdout_logger.info("Subscription result for topic %s: %s", topic, result)

    app = create_app(
        file_logger=LoggerConfig.get_file_logger("reviewer_app"),
        stdout_logger=stdout_logger,
    )
    port = settings.CALLBACK_URL.split(":")[-1].split("/")[0]
    uvicorn.run(app, host="0.0.0.0", port=int(port))


if __name__ == "__main__":
    main()
