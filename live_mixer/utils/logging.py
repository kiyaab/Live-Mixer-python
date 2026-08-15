"""Application logging — never call from the real-time audio callback."""

from __future__ import annotations

import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """Configure root logger for the application."""
    logger = logging.getLogger("live_mixer")
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
