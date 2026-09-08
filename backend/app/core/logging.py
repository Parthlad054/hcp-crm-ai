"""
core/logging.py — Centralised logging configuration.

Call setup_logging() once at application startup (in main.py lifespan or
at module level) to apply consistent formatting across all loggers.
"""
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure the root logger with a structured formatter.

    Format: [LEVEL] YYYY-MM-DD HH:MM:SS — logger_name — message
    Outputs to stdout so container runtimes (Docker, K8s) capture logs
    automatically without extra configuration.
    """
    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(asctime)s — %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid adding duplicate handlers on repeated calls (e.g. during tests)
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers[0] = handler

    # Quieten noisy third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
