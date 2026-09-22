from __future__ import annotations

from typing import Any, Callable

_cache: dict[str, Any] = {}


def cached_json(key: str, *args: Any, fn: Callable[[], Any] | None = None) -> Any:
    """Return the cached JSON result for *key*, computing it on first use.

    The real call signature used throughout the codebase is
    ``cached_json(key, prompt, system, lambda)``.  We ignore the positional
    prompt/system metadata and key purely on *key* so repeated calls with
    the same key share one result.
    """
    if key in _cache:
        return _cache[key]
    if fn is None:
        # Last positional argument is the callable.
        fn = args[-1] if args else lambda: None
    result = fn()
    _cache[key] = result
    return result


def run() -> None:
    """Main entry point for the articles module."""
    pass