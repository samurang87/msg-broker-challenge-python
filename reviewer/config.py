import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BROKER_URL: str = "http://localhost:8000"
    CALLBACK_URL: str = "http://localhost:8001/callback"
    LOG_FORMATTER: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


class LoggerConfig:
    @staticmethod
    def get_file_logger(name: str) -> logging.Logger:
        file_logger = logging.getLogger(f"{name}_file")
        file_logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler("reviewer_app.log")
        file_handler.setLevel(logging.DEBUG)
        formatter = Settings().LOG_FORMATTER
        file_handler.setFormatter(formatter)

        file_logger.addHandler(file_handler)
        return file_logger

    @staticmethod
    def get_stdout_logger(name: str) -> logging.Logger:
        stdout_logger = logging.getLogger(f"{name}_stdout")
        stdout_logger.setLevel(logging.DEBUG)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.INFO)
        formatter = Settings().LOG_FORMATTER
        stdout_handler.setFormatter(formatter)

        stdout_logger.addHandler(stdout_handler)
        return stdout_logger
