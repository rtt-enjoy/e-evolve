"""Utility helpers for the E‑Evolve bot.

Provides a safe wrapper around ``os.getenv`` that trims whitespace and
returns ``None`` when a variable is missing or empty.  Centralising this
logic reduces duplicated checks across earning modules.
"""
from __future__ import annotations

import logging
import os
from typing import Optional


_log = logging.getLogger(__name__)


def get_env(name: str) -> Optional[str]:
	"""Return the stripped value of an environment variable or ``None``.

    The function treats empty strings as missing and logs a debug message
    so silent configuration drift shows up in the bot's logs. Modules can
    import this helper and replace repetitive ``os.getenv(...).strip()``
    calls with a single, well-behaved call.
    """
	value = os.getenv(name)
	if value is None:
		return None
	stripped = value.strip()
	if not stripped:
		# A missing-or-empty key is a configuration signal, not a hard error;
		# debug level keeps the noise out of normal runs while still surfacing
		# when the owner inspects logs to find a missing secret.
		_log.debug("get_env: %s is missing or empty", name)
		return None
	return stripped

__all__ = ["get_env"]