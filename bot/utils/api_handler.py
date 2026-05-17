"""Centralized API error handling with retry logic."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

import requests

log = logging.getLogger(__name__)


def _load_config() -> dict:
    try:
        import json
        from pathlib import Path
        return json.loads(Path("config/strategy.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    jitter: bool = True


def _get_retry_config() -> RetryConfig:
    cfg = _load_config().get("api", {})
    return RetryConfig(
        max_attempts=int(cfg.get("max_attempts", 3)),
        base_delay=float(cfg.get("base_delay", 1.0)),
        max_delay=float(cfg.get("max_delay", 30.0)),
        backoff_factor=float(cfg.get("backoff_factor", 2.0)),
        jitter=cfg.get("jitter", True),
    )


class APIHandler:
    """Centralized HTTP client with retry and error handling."""

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or _get_retry_config()
        self.session = requests.Session()

    def request(
        self,
        method: str,
        url: str,
        *, 
        retry_on: Optional[list[int]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make an HTTP request with automatic retry on specified status codes.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            retry_on: List of status codes to retry on (default: 429, 502, 503, 504)
            **kwargs: Passed to requests.request
            
        Returns:
            requests.Response object
            
        Raises:
            requests.RequestException after all retries exhausted
n        """
        if retry_on is None:
            retry_on = [429, 502, 503, 504]

        last_error = None
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                resp = self.session.request(method, url, **kwargs)
                if resp.status_code not in retry_on:
                    return resp
                last_error = f"Status {resp.status_code} in retry list"
            except requests.RequestException as exc:
                last_error = str(exc)

            if attempt < self.config.max_attempts:
                delay = self._calculate_delay(attempt)
                log.warning(
                    "API request failed (attempt %d/%d): %s — retrying in %.1fs",
                    attempt, self.config.max_attempts, last_error, delay
                )
                time.sleep(delay)

        raise requests.RequestException(
            f"API request failed after {self.config.max_attempts} attempts: {last_error}"
        )

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        delay = min(
            self.config.base_delay * (self.config.backoff_factor ** (attempt - 1)),
            self.config.max_delay,
        )
        if self.config.jitter:
            import random
            delay = delay * 0.5 + random.random() * delay * 0.5
        return delay

    def get(self, url: str, **kwargs) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        return self.request("POST", url, **kwargs)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "APIHandler":
        return self

    def __exit__(self, *args) -> None:
        self.close()