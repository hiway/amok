import logging as _logging
from typing import Optional as _Optional


def get_logger(name: str, level: int = _logging.INFO) -> _logging.Logger:
    logger = _logging.getLogger(name)
    logger.setLevel(level)
    handler = _logging.StreamHandler()
    handler.setLevel(level)
    formatter = _logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
