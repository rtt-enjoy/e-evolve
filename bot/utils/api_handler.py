from __future__ import annotations

import logging
import time
from typing import Any, Callable

log = logging.getLogger(__name__)

class APIHandler:
    """Simple helper for retrying HTTP‑like operations.

    The original bot referenced this class in `bot/errors.py` but the file was missing,
    causing an import error that prevented the error‑handling subsystem from loading.
    This lightweight implementation provides exponential back‑off and optional
    callback hooks without pulling in external dependencies.
    """

    def __init__(self, retries: int = 3, backoff: float = 1.5) -> None:
        self.retries = retries
        self.backoff = backoff

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute *func* with retry logic.

        Parameters
        ----------
        func: Callable
            The function performing the external request.
        *args, **kwargs: Any
            Arguments passed to *func*.
        """
        attempt = 0
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                attempt += 1
                if attempt > self.retries:
                    log.error("API call failed after %d attempts: %s", attempt - 1, exc)
                    raise
                wait = self.backoff ** attempt
                log.warning("API call error (attempt %d/%d): %s – retrying in %.1fs", attempt, self.retries, exc, wait)
                time.sleep(wait)

    def _record_error(self, error: Exception) -> None:
        """Placeholder for future error‑recording integrations.

        Currently logs the error; can be extended to send metrics or alerts.
        """
        log.error("Recorded error: %s", error)