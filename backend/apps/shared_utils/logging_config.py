import logging
import os


def _get_log_level() -> int:
    level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    return getattr(logging, level_name, logging.INFO)


def setup_logging(force: bool = False, level: int | None = None) -> None:
    """
    Configure root logging for the backend server.

    - Uses LOG_LEVEL environment variable (default: INFO).
    - Skips configuration if handlers already exist unless force=True.
    - Sets a sane format suitable for server logs.
    """
    root_logger = logging.getLogger()

    if level is None:
        level = _get_log_level()

    # Avoid duplicating handlers when tests import the app multiple times
    if root_logger.handlers and not force:
        # Still ensure the level is at least the desired level
        root_logger.setLevel(level)
        return

    log_format = '%(asctime)s %(levelname)s [[SERVER]] [%(name)s] => %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(level=level, format=log_format, datefmt=datefmt)

    # Reduce noisy libraries if desired
    for noisy in ('uvicorn', 'uvicorn.access', 'asyncio', 'httpx'):
        logging.getLogger(noisy).setLevel(os.getenv('NOISY_LOG_LEVEL', 'WARNING').upper())
