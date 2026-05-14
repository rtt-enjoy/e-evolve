"""
Independent earning module: code-tech opportunity scanner.

This module does not publish, trade, mint, or claim revenue. It periodically
builds a queue of code-only opportunities that can plausibly lead to small
daily income: paid OSS issues, maintainer chores, migration work, CI fixes, and
micro-service ideas. Confirmed revenue remains tracked elsewhere.
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger(__name__)

_STRATEGY_FILE = Path("config/strategy.json")
_REPORT_FILE = Path("docs/code-tech-opportunities.md")

_DEFAULT_CONFIG = {
    "enabled": True,
    "refresh_hours": 24,
    "daily_target_usd": 10.0,
    "max_items": 8,
    "min_score": 55,
    "github_searches": [
        "is:issue is:open bounty label:bounty",
        "is:issue is:open bounty language:Python",
        "is:issue is:open bounty language:TypeScript",
        "is:issue is:open label:\"help wanted\" \"CI\"",
        "is:issue is:open label:\"good first issue\" \"migration\"",
        "is:issue is:open \"docs\" \"broken\" \"example\"",
    ],
    "underserved_focus": [
        "failing CI with a small, reproducible fix",
        "dependency migration or deprecation cleanup",
        "documentation examples that no longer run",
        "test flakiness with a clear failure signature",
        "type hints, packaging metadata, and release automation",
        "small compatibility fixes in niche developer tools",
    ],
}

_LOCAL_LEADS = [
    {
        "title": "Package migration cleanup for small Python projects",
        "url": "",
        "source": "local-playbook",
        "body": "Offer a fixed-price patch for pyproject.toml, ruff, mypy, pytest, and GitHub Actions drift.",
        "labels": ["migration", "packaging", "ci"],
    },
    {
        "title": "Broken README examples in niche SDK repos",
        "url": "",
        "source": "local-playbook",
        "body": "Find repos where the documented quickstart fails, then submit a runnable example and offer maintenance.",
        "labels": ["docs", "examples", "sdk"],
    },
    {
        "title": "Flaky test triage for tiny open-source maintainers",
        "url": "",
        "source": "local-playbook",
        "body": "Target intermittent CI failures with logs, seed control, network timeouts, and time-based assertions.",
        "labels": ["tests", "ci", "flaky"],
    },
]


@dataclass
class Opportunity:
    title: str
    url: str
    source: str
    score: int
    estimated_value_usd: float
    reason: str
    next_step: str


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Refresh the code-tech opportunity queue when the cadence is due."""
    cfg = _config()
    state = status.setdefault("code_tech_earning", {})
    if not _enabled(cfg):
        state["enabled"] = False
        return []

    now = datetime.now(timezone.utc)
    refresh_hours = max(1, int(cfg.get("refresh_hours", 24) or 24))
    last_run = _parse_dt(state.get("last_refresh_at"))
    if last_run and now - last_run < timedelta(hours=refresh_hours):
        log.info("[code_techs] queue is fresh; next refresh after %sh", refresh_hours)
        return []

    max_items = max(1, int(cfg.get("max_items", 8) or 8))
    min_score = max(0, int(cfg.get("min_score", 55) or 55))
    raw = _fetch_github_leads(cfg) or list(_LOCAL_LEADS)
    opportunities = _rank(raw, cfg, max_items=max_items, min_score=min_score)

    state.update({
        "enabled": True,
        "last_refresh_at": now.isoformat(),
        "daily_target_usd": float(cfg.get("daily_target_usd", 10.0) or 10.0),
        "refresh_hours": refresh_hours,
        "opportunities": [op.__dict__ for op in opportunities],
        "focus": list(cfg.get("underserved_focus", [])),
    })
    _write_report(state)

    log.info("[code_techs] refreshed %d code-tech opportunities", len(opportunities))
    return [{
        "platform": "code_techs",
        "success": True,
        "opportunity_count": len(opportunities),
        "estimated_usd": 0.0,
        "target_usd_per_day": state["daily_target_usd"],
        "title": f"Code-tech opportunity queue refreshed ({len(opportunities)} leads)",
        "url": str(_REPORT_FILE),
    }]


def _config() -> dict[str, Any]:
    try:
        strategy = json.loads(_STRATEGY_FILE.read_text(encoding="utf-8"))
    except Exception:
        strategy = {}
    cfg = dict(_DEFAULT_CONFIG)
    cfg.update(strategy.get("code_techs", {}) or {})
    return cfg


def _enabled(cfg: dict[str, Any]) -> bool:
    raw = os.getenv("CODE_TECH_EARN_ENABLED", "").strip().lower()
    if raw in {"0", "false", "no", "off"}:
        return False
    if raw in {"1", "true", "yes", "on"}:
        return True
    return bool(cfg.get("enabled", True))


def _fetch_github_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    leads: list[dict[str, Any]] = []
    token = os.getenv("GITHUB_TOKEN", "").strip()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "e-evolve-code-techs",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for query in cfg.get("github_searches", []):
        try:
            resp = requests.get(
                "https://api.github.com/search/issues",
                params={"q": str(query), "sort": "updated", "order": "desc", "per_page": 8},
                headers=headers,
                timeout=20,
            )
            if resp.status_code in (403, 422):
                log.warning("[code_techs] GitHub search skipped (%s): %s", resp.status_code, query)
                continue
            resp.raise_for_status()
            for item in resp.json().get("items", []):
                leads.append({
                    "title": item.get("title", ""),
                    "url": item.get("html_url", ""),
                    "source": "github",
                    "body": item.get("body", "") or "",
                    "labels": [label.get("name", "") for label in item.get("labels", [])],
                })
        except Exception as exc:
            log.warning("[code_techs] GitHub search failed for %r: %s", query, exc)
    return _dedupe(leads)


def _dedupe(leads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for lead in leads:
        key = str(lead.get("url") or lead.get("title", "")).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(lead)
    return out


def _rank(leads: list[dict[str, Any]], cfg: dict[str, Any], max_items: int, min_score: int) -> list[Opportunity]:
    ranked: list[Opportunity] = []
    for lead in leads:
        title = str(lead.get("title", "")).strip()
        body = str(lead.get("body", "")).strip()
        labels = [str(x).lower() for x in lead.get("labels", [])]
        text = " ".join([title, body, " ".join(labels)]).lower()
        value = _extract_value(text, cfg)
        score = _score(text, labels, value)
        if score < min_score and lead.get("source") != "local-playbook":
            continue
        ranked.append(Opportunity(
            title=title[:140] or "untitled code-tech lead",
            url=str(lead.get("url", "")),
            source=str(lead.get("source", "unknown")),
            score=score,
            estimated_value_usd=value,
            reason=_reason(text, labels, value),
            next_step=_next_step(text),
        ))
    ranked.sort(key=lambda op: (op.score, op.estimated_value_usd), reverse=True)
    return ranked[:max_items]


def _score(text: str, labels: list[str], value: float) -> int:
    score = 30
    if value:
        score += min(35, int(value / 5))
    if any(word in text for word in ("bounty", "paid", "reward", "fixed-price", "service", "offer")):
        score += 18
    if any(word in text for word in ("ci", "test", "flaky", "failing")):
        score += 14
    if any(word in text for word in ("migration", "deprecation", "upgrade", "compatibility")):
        score += 12
    if any(word in text for word in ("docs", "readme", "example", "quickstart")):
        score += 10
    if any(word in text for word in ("design", "logo", "marketing", "translation")):
        score -= 12
    if "good first issue" in " ".join(labels):
        score -= 4
    return max(0, min(100, score))


def _extract_value(text: str, cfg: dict[str, Any]) -> float:
    amounts = [float(m.group(1).replace(",", "")) for m in re.finditer(r"\$(\d[\d,]*(?:\.\d+)?)", text)]
    if amounts:
        return round(max(amounts), 2)
    target = float(cfg.get("daily_target_usd", 10.0) or 10.0)
    if any(word in text for word in ("bounty", "paid", "reward", "fixed-price")):
        return target
    return 0.0


def _reason(text: str, labels: list[str], value: float) -> str:
    parts: list[str] = []
    if value:
        parts.append(f"visible or inferred value around ${value:.2f}")
    if any(word in text for word in ("ci", "test", "flaky", "failing")):
        parts.append("CI/test work is concrete and easy for maintainers to accept")
    if any(word in text for word in ("migration", "deprecation", "upgrade", "compatibility")):
        parts.append("migration chores are neglected but urgent")
    if any(word in text for word in ("docs", "readme", "example", "quickstart")):
        parts.append("working docs convert into trust quickly")
    if not parts:
        parts.append("small code maintenance lead with low competition")
    return "; ".join(parts[:2])


def _next_step(text: str) -> str:
    if "bounty" in text:
        return "Verify bounty rules, reproduce the issue, then prepare the smallest passing patch."
    if any(word in text for word in ("migration", "deprecation", "upgrade", "compatibility")):
        return "Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup."
    if any(word in text for word in ("ci", "test", "flaky", "failing")):
        return "Open the latest failed job, capture the failure signature, and patch only the failing path."
    if any(word in text for word in ("docs", "readme", "example", "quickstart")):
        return "Run the documented example from a clean checkout and submit the corrected command or snippet."
    return "Reproduce locally, write a short maintainer note, and keep the first patch under one focused change."


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _write_report(state: dict[str, Any]) -> None:
    _REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Code-Tech Earning Queue",
        "",
        f"Refreshed: {state.get('last_refresh_at')}",
        f"Daily target: ${float(state.get('daily_target_usd', 10.0) or 10.0):.2f}",
        "",
        "## Underserved Focus",
        "",
    ]
    for item in state.get("focus", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Ranked Leads", ""])
    for index, op in enumerate(state.get("opportunities", []), start=1):
        title = op.get("title", "untitled")
        url = op.get("url", "")
        heading = f"{index}. [{title}]({url})" if url else f"{index}. {title}"
        lines.extend([
            heading,
            f"   - Score: {op.get('score', 0)}/100",
            f"   - Value signal: ${float(op.get('estimated_value_usd', 0) or 0):.2f}",
            f"   - Why: {op.get('reason', '')}",
            f"   - Next: {op.get('next_step', '')}",
        ])
    _REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
