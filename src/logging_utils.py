import logging

logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    _logger = logging.getLogger(name)
    if not _logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        _logger.addHandler(handler)
        _logger.setLevel(logging.INFO)
    return _logger
