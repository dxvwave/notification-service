from shared.logging import setup_logging as _setup_logging

from core.config import settings


def setup_logging(log_level: str | None = None) -> None:
    if log_level is None:
        log_level = settings.log_level
    _setup_logging(log_level=log_level)
