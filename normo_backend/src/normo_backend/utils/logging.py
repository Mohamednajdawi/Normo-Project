import os
from logging import INFO, Formatter, Logger, StreamHandler, getLogger
from typing import Optional


def get_logger(name: Optional[str] = None) -> Logger:
    logger_name = name or __name__
    logger = getLogger(logger_name)

    if not logger.handlers:
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        log_level = getattr(__import__("logging"), log_level_str, INFO)
        handler = StreamHandler()
        formatter = Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.propagate = False

    return logger
