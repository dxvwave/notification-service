import logging
import sys

from core.config import settings


def setup_logging(log_level: str | None = None) -> None:
    if log_level is None:
        log_level = settings.log_level

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
