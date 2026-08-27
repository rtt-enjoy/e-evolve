"""
Shared primitives for the earning modules.

Every earning module needs the same four things: its slice of
``config/strategy.json``, a cadence check against a stored timestamp, and
tolerant parsers for the feed data it scrapes. Each module used to carry its
own copy, and the copies had drifted -- ``code_techs`` held a ``_parse_dt``
that could not read RFC-822 RSS dates and a ``_strip_html`` that left
``<script>`` bodies intact, while ``trending`` handled both. Consolidating on
the stronger implementation is what this module is for.

No module state and no I/O beyond reading the strategy file, so importing it
is free and it can be exercised directly in tests.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

CONFIG_FILE = Path("config/strategy.json")


def load_config(section: str, defaults: Mapping[str, Any] | None = None) -> dict:
	"""Return one section of the strategy file, with ``defaults`` filled in.

    Read at call time, never at import time. A module-level constant captured
    at import cannot see an owner's config edit without a reimport, and it
    forces tests to monkeypatch globals to change one setting.

    A missing or malformed file yields the defaults: bad config degrades the
    module to its documented behaviour rather than crashing the cycle.
    """
	try:
		raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8")).get(section, {})
	except Exception:
		raw = {}
	cfg = dict(defaults or {})
	if isinstance(raw, dict):
		cfg.update(raw)
	return cfg


def hours_until_due(state: Mapping[str, Any], key: str, interval_hours: int) -> float:
	"""Hours remaining before ``key``'s cadence is due again. 0.0 when due now.

    A missing or unparseable stamp reads as due. A module that has never run
    must be allowed to run, and a corrupt timestamp must not wedge it forever.
    """
	stamp = str(state.get(key) or "").strip()
	if not stamp:
		return 0.0
	last = parse_dt(stamp)
	if last is None:
		return 0.0
	due = last + timedelta(hours=max(1, interval_hours))
	return max(0.0, (due - datetime.now(timezone.utc)).total_seconds() / 3600)


def parse_dt(value: Any) -> Optional[datetime]:
	"""Parse ISO-8601 or RFC-822 (RSS ``pubDate``) into an aware UTC datetime.

    Feeds serve both formats, so both are tried. A naive result is assumed UTC,
    which is what every source here publishes.
    """
	if not value:
		return None
	raw = str(value).strip()
	try:
		dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
		return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
	except Exception:
		pass
	try:
		from email.utils import parsedate_to_datetime
		dt = parsedate_to_datetime(raw)
		return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
	except Exception:
		return None


def strip_html(value: str) -> str:
	"""Flatten feed HTML to plain text.

    ``<script>`` bodies are dropped whole -- tag-stripping alone would leave
    the JavaScript source behind as if it were prose.
    """
	value = re.sub(r"<script.*?</script>", " ", value, flags=re.DOTALL | re.IGNORECASE)
	value = re.sub(r"<[^>]+>", " ", value)
	value = re.sub(r"&[a-z]+;", " ", value)
	return re.sub(r"\s+", " ", value).strip()


def xml_text(parent: ET.Element, tag: str) -> str:
	"""Text of the first ``tag`` child, namespace-agnostic. '' when absent."""
	element = parent.find(f"{{*}}{tag}")
	if element is None or element.text is None:
		return ""
	return element.text.strip()


def bounded_append(entries: list, value: Any, limit: int) -> None:
	"""Append ``value`` if new, then trim ``entries`` to the newest ``limit``.

    Every history list in status.json is bounded this way so the file cannot
    grow without end across an hourly schedule.
    """
	if value and value not in entries:
		entries.append(value)
	del entries[: -max(1, limit)]
