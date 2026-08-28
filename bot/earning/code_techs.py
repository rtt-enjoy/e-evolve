from __future__ import annotations

import json
import logging
import os
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import requests

from . import json_repair
from ._shared import load_config, parse_dt, strip_html, xml_text

log = logging.getLogger(__name__)


def _cell(text: str) -> str:
    """Normalize text for use as a single cell in a delimited record."""
    return (text or "").replace("\t", " ").replace("\n", " ").replace("\r", " ").strip()


def _clean_list(value: Any) -> list[str]:
    """Return a list of non-empty strings from ``value``."""
    if not value:
        return []
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        items = re.split(r"[\n,;]", value)
    else:
        return []
    out: list[str] = []
    for item in items:
        if not isinstance(item, str):
            item = str(item)
        cleaned = item.strip()
        if cleaned:
            out.append(cleaned)
    return out


def _dicts(value: Any) -> list[dict[str, Any]]:
    """Return only the mapping items from ``value``."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def run(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run the code_techs earning strategy cycle.

    Returns a dict summarizing actions taken. Kept as a stable entry point
    so ``bot.earning.__init__`` can import it as ``code_techs_run``.
    """
    cfg = load_config()
    strategy_cfg = cfg.get("code_techs", {}) if isinstance(cfg, dict) else {}
    if not strategy_cfg.get("enabled", True):
        log.info("code_techs strategy is disabled; skipping run")
        return {"ok": True, "skipped": True, "reason": "disabled"}

    log.info("code_techs: starting run")
    return {"ok": True, "skipped": False, "strategy": "code_techs"}