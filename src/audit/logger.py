import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from src.config import get_settings


def get_audit_logger() -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger("audit")
    if logger.handlers:
        return logger

    logger.setLevel(settings.LOG_LEVEL)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    if settings.AUDIT_LOG_PATH:
        file_handler = logging.FileHandler(settings.AUDIT_LOG_PATH)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(file_handler)

    return logger


def audit_event(event_type: str, payload: Dict[str, Any]) -> None:
    logger = get_audit_logger()
    body = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **payload,
    }
    logger.info(json.dumps(body, default=str))
