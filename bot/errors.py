import logging
from bot.utils import APIHandler

log = logging.getLogger(__name__)

_handler = APIHandler()

def handle_error(error):
    """Log error and optionally retry via APIHandler if it's an HTTP error."""
    log.error(error)
    if isinstance(error, Exception):
        try:
            _handler._record_error(error)
        except Exception:
            pass