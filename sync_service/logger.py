import logging
import logging.handlers
from sync_service.config import LOG_LEVEL, LOG_FILE

logger = logging.getLogger("sync_service")
logger.setLevel(getattr(logging, LOG_LEVEL))

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=10_000_000, backupCount=5
)
handler.setFormatter(formatter)
logger.addHandler(handler)
