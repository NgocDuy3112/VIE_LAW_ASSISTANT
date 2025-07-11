import logging
import sys


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL = logging.INFO


# Configure root logger
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    stream=sys.stdout
)

def get_logger(name: str="retriever-service") -> logging.Logger:
    """
    Returns a logger with the specified name, using the global configuration.
    """
    return logging.getLogger(name)