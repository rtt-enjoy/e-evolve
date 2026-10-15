"""
Exponential backoff retry utility for resilient external API calls.

Provides a decorator ``retry_with_backoff`` that retries a function with
exponential delay and jitter, reducing transient failures such as quota
exhaustion or network flakiness.
"""

import random
import time
from functools import wraps
from typing import Any, Callable


def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    factor: float = 2.0,
    jitter: float = 0.1,
    **kwargs,
) -> Any:
    """Execute ``func(*args, **kwargs`` with exponential backoff on failure.

    Retries up to ``max_retries`` times. The delay between attempts follows
    ``base_delay * factor ** attempt`` plus a random jitter fraction of the
    delay. All exceptions are caught and re-raised after the final attempt.
    """
    last_exc = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt == max_retries - 1:
                break
            delay = base_delay * (factor ** attempt)
            delay += random.uniform(-jitter * delay, jitter * delay)
            time.sleep(delay)
    raise last_exc