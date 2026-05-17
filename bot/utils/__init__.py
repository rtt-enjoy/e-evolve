"""Utility helpers for the E‑Evolve bot.

Provides a safe wrapper around ``os.getenv`` that trims whitespace and
returns ``None`` when a variable is missing or empty.  Centralising this
logic reduces duplicated checks across earning modules.
"""
from __future__ import annotations

import os
from typing import Optional


def get_env(name: str) -> Optional[str]:
    """Return the stripped value of an environment variable or ``None``.

    The function treats empty strings as missing and logs a debug message
    (the bot's logger is configured globally).  Modules can import this
    helper and replace repetitive ``os.getenv(...).strip()`` calls.
    """
    value = os.getenv(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None

__all__ = ["get_env"]