"""Rate-limit monitoring for API providers."""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

log = logging.getLogger(__name__)


def _load_config() -> dict:
    try:
        import json
        from pathlib import Path
        return json.loads(Path("config/strategy.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


@dataclass
class ProviderLimits:
    """Rate limits for a single provider."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    _requests: list[float] = field(default_factory=list)


@dataclass
class RateLimitStatus:
    """Current rate limit status for a provider."""
    provider: str
    requests_this_minute: int = 0
    requests_this_hour: int = 0
    remaining_minute: int = 0
    remaining_hour: int = 0
    is_limited: bool = False
    warning_threshold: float = 0.8


class RateLimiter:
    """Track and warn on API rate limit usage."""

    _instance: Optional["RateLimiter"] = None
    _limits: dict[str, ProviderLimits] = field(default_factory=dict, init=False)
    _request_times: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list), init=False)

    def __new__(cls) -> "RateLimiter":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_limits()
        return cls._instance

    def _init_limits(self) -> None:
        cfg = _load_config().get("rate_limits", {})
        self._limits = {}
        for provider, limits in cfg.items():
            self._limits[provider] = ProviderLimits(
                requests_per_minute=int(limits.get("per_minute", 60)),
                requests_per_hour=int(limits.get("per_hour", 1000)),
            )

    def record_request(self, provider: str) -> RateLimitStatus:
        """Record a request and return current status."""
        now = time.time()
        limits = self._limits.get(provider)
        if not limits:
            limits = ProviderLimits()
            self._limits[provider] = limits

        # Clean old requests (older than 1 hour)
        cutoff = now - 3600
        self._request_times[provider] = [
            t for t in self._request_times[provider] if t > cutoff
        ]

        # Add current request
        self._request_times[provider].append(now)

        # Count in current windows
        minute_cutoff = now - 60
        hour_cutoff = now - 3600

        req_min = sum(1 for t in self._request_times[provider] if t > minute_cutoff)
        req_hour = sum(1 for t in self._request_times[provider] if t > hour_cutoff)

        # Calculate remaining
        remaining_min = max(0, limits.requests_per_minute - req_min)
        remaining_hour = max(0, limits.requests_per_hour - req_hour)

        # Check if limited
        is_limited = req_min >= limits.requests_per_minute or req_hour >= limits.requests_per_hour

        status = RateLimitStatus(
            provider=provider,
            requests_this_minute=req_min,
            requests_this_hour=req_hour,
            remaining_minute=remaining_min,
            remaining_hour=remaining_hour,
            is_limited=is_limited,
        )

        if status.remaining_minute <= limits.requests_per_minute * 0.1:
            log.warning(
                "Rate limit warning for %s: %d/%d requests this minute", 
                provider, req_min, limits.requests_per_minute
            )

        return status

    def check_before_request(self, provider: str) -> bool:
        """Check if request is allowed before making it."""
        status = self.record_request(provider)
        if status.is_limited:
            log.error("Rate limit exceeded for %s", provider)
            return False
        return True

    def get_status(self, provider: str) -> Optional[RateLimitStatus]:
        """Get current status for a provider."""
        if provider not in self._limits:
            return None
        return self.record_request(provider)  # Record to get fresh count

    def reset(self, provider: Optional[str] = None) -> None:
        """Reset request counts for a provider or all providers."""
        if provider:
            self._request_times[provider] = []
        else:
            for p in self._request_times:
                self._request_times[p] = []


# Convenience function for quick checks
_limiter: Optional[RateLimiter] = None


def get_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter


def check_rate(provider: str) -> bool:
    """Quick check if request is allowed for provider."""
    return get_limiter().check_before_request(provider)