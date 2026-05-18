from __future__ import annotations

import json
import logging
import os
import re
import time
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
    "auto_pursue": True,
    "pursue_score_threshold": 75,
    "requirements": [
        "Prefer work that can be reproduced from public logs, docs, or a clean checkout in under 30 minutes.",
        "Prefer boring maintenance where the failure and expected fix are visible without private context.",
        "Require a deterministic command, log, docs page, or issue thread that an AI agent can use as proof.",
        "Keep the first contribution small enough for the bot to patch, test, and explain automatically.",
        "Do not count discovery or speculative upside as earnings."
    ],
    "github_searches": [
        "is:issue is:open label:\"help wanted\" \"CI\"",
        "is:issue is:open label:\"help wanted\" \"failing tests\"",
        "is:issue is:open label:\"good first issue\" \"dependency update\"",
        "is:issue is:open label:\"good first issue\" \"documentation\" \"example\"",
        "is:issue is:open \"docs\" \"broken\" \"example\"",
        "is:issue is:open \"README\" \"does not work\" \"install\"",
        "is:issue is:open \"quickstart\" \"fails\" language:Python",
        "is:issue is:open \"pyproject\" \"deprecation\"",
        "is:issue is:open \"ruff\" \"mypy\" \"pytest\"",
        "is:issue is:open \"Node 20\" \"migration\"",
        "is:issue is:open \"Node 22\" \"migration\"",
        "is:issue is:open \"GitHub Actions\" \"deprecated\" \"warning\"",
        "is:issue is:open \"import error\" \"Python 3.12\"",
        "is:issue is:open \"Python 3.13\" \"compatibility\"",
        "is:issue is:open \"release notes\" \"breaking change\""
    ],
    "underserved_focus": [
        "failing CI with a small, reproducible fix",
        "dependency migration or deprecation cleanup",
        "documentation examples that no longer run",
        "test flakiness with a clear failure signature",
        "type hints, packaging metadata, and release automation",
        "small compatibility fixes in niche developer tools",
        "abandoned but still-installed packages with open compatibility issues",
        "template repos and starter kits whose quickstarts fail on current runtimes",
        "internal-tool shaped repos where businesses need maintenance more than novelty",
        "release-note gaps after breaking API changes",
        "low-glamour data import/export bugs in small SaaS integrations"
    ],
    "strategy_playbook": [
        "Start from maintenance pain, not idea novelty.",
        "Use proof as the sales asset: failing command, failing log line, short before/after note.",
        "Favor repeatable chores that can become productized services.",
        "Look for AI-automatable chores: stale issues with logs, forks with small fixes, unanswered install failures.",
        "Bundle adjacent fixes only after trust exists.",
        "Treat content as deal flow from solved niche issues."
    ],
    "avoid_patterns": [
        "Large rewrites, vague feature requests, design taste debates, and architecture arguments without a failing proof.",
        "Repos with no maintainer response, no recent users, no releases, and no business signal.",
        "Crowded prize or beginner issues where many contributors compete for low-value visibility.",
        "Unpaid speculative requests that need private context before value can be proven.",
        "Crypto/NFT hype work unless there is a concrete paid maintenance task and bounded risk."
    ]
}

_LOCAL_LEADS = [
    {
        "title": "Package migration cleanup for small Python projects",
        "url": "",
        "source": "local-playbook",
        "body": "Let the AI agent patch pyproject.toml, ruff, mypy, pytest, and GitHub Actions drift from public CI logs.",
        "labels": ["migration", "packaging", "ci"]
    },
    {
        "title": "Broken README examples in niche SDK repos",
        "url": "",
        "source": "local-playbook",
        "body": "Find repos where the documented quickstart fails, then have the AI agent submit a runnable example fix.",
        "labels": ["docs", "examples", "sdk"]
    },
    {
        "title": "Flaky test triage for tiny open-source maintainers",
        "url": "",
        "source": "local-playbook",
        "body": "Target intermittent CI failures with logs, seed control, network timeouts, and time-based assertions the bot can reproduce.",
        "labels": ["tests", "ci", "flaky"]
    },
    {
        "title": "Deprecated GitHub Actions cleanup",
        "url": "",
        "source": "local-playbook",
        "body": "Patch action version warnings, Node runtime deprecations, cache key drift, and failing matrix jobs.",
        "labels": ["github-actions", "deprecation", "ci"]
    },
    {
        "title": "Starter template compatibility repair",
        "url": "",
        "source": "local-playbook",
        "body": "Run a starter template from scratch, fix install/build/test failures, and document the exact working command.",
        "labels": ["template", "quickstart", "compatibility"]
    }
]

# In‑memory request counter for GitHub API throttling
_GITHUB_REQ_COUNT = 0
_GITHUB_WINDOW_START = time.time()
_GITHUB_MAX_PER_MIN = 10

@dataclass
class Opportunity:
    title: str
    url: str
    source: str
    score: int
    estimated_value_usd: float
    reason: str
    next_step: str
    pursued: bool = False
    archived_at: str | None = None

def run(llm: Any, status: dict[str, Any]) -> list[dict]:
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

    # Auto‑pursue high‑value leads
    pursued_count = 0
    if cfg.get("auto_pursue", True):
        threshold = max(50, int(cfg.get("pursue_score_threshold", 75) or 75))
        for opp in opportunities:
            if opp.score >= threshold and not opp.pursued and opp.url:
                if _pursue_lead(opp, cfg):
                    opp.pursued = True
                    pursued_count += 1

    state.update({
        "enabled": True,
        "last_refresh_at": now.isoformat(),
        "daily_target_usd": float(cfg.get("daily_target_usd", 10.0) or 10.0),
        "refresh_hours": refresh_hours,
        "opportunities": [op.__dict__ for op in opportunities],
        "requirements": _clean_list(cfg.get("requirements", [])),
        "focus": _clean_list(cfg.get("underserved_focus", [])),
        "strategy_playbook": _clean_list(cfg.get("strategy_playbook", [])),
        "avoid_patterns": _clean_list(cfg.get("avoid_patterns", []))
    })
    _write_report(state)

    log.info("[code_techs] refreshed %d opportunities, pursued %d", len(opportunities), pursued_count)
    return [{
        "platform": "code_techs",
        "success": True,
        "opportunity_count": len(opportunities),
        "pursued_count": pursued_count,
        "estimated_usd": 0.0,
        "target_usd_per_day": state["daily_target_usd"],
        "title": f"Code-tech queue refreshed ({len(opportunities)} leads, {pursued_count} pursued)",
        "url": str(_REPORT_FILE)
    }]

def _pursue_lead(opportunity: Opportunity, cfg: dict) -> bool:
    token = os.getenv("GH_TOKEN", "").strip() or os.getenv("GITHUB_TOKEN", "").strip()
    if not token or not opportunity.url:
        return False
    try:
        parts = opportunity.url.replace("https://github.com/", "").split("/")
        if len(parts) < 4:
            return False
        owner, repo, _, issue_num = parts[0], parts[1], parts[2], parts[3]
    except Exception as exc:
        log.warning("[code_techs] URL parse failed %s: %s", opportunity.url, exc)
        return False
    comment_body = _build_pursuit_comment(opportunity)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    try:
        resp = requests.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}/comments",
            headers=headers,
            json={"body": comment_body},
            timeout=15
        )
        if resp.status_code == 201:
            log.info("[code_techs] Pursued lead: %s", opportunity.title[:50])
            return True
        elif resp.status_code == 403:
            log.warning("[code_techs] Rate limited or forbidden pursuing %s", opportunity.url)
        else:
            log.debug("[code_techs] Comment failed %s", resp.status_code)
    except Exception as exc:
        log.warning("[code_techs] Pursue error: %s", exc)
    return False

def _build_pursuit_comment(opportunity: Opportunity) -> str:
    templates = [
        "Hi! I'm interested in helping with this. Do you have a preferred way to receive patches? I can start with a small reproducer if helpful.",
        "I'd like to work on this. Could you point me to the relevant files or tests?",
        "Happy to help here. What's the best way to submit a fix — PR directly or discuss first?",
        "I can take this on. Should I open a draft PR with the initial fix, or discuss the approach first?"
    ]
    return templates[opportunity.score % len(templates)]

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
    global _GITHUB_REQ_COUNT, _GITHUB_WINDOW_START
    leads: list[dict[str, Any]] = []
    token = os.getenv("GITHUB_TOKEN", "").strip()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "e-evolve-code-techs"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for query in cfg.get("github_searches", []):
        # Simple rate‑limit handling
        now = time.time()
        if now - _GITHUB_WINDOW_START >= 60:
            _GITHUB_WINDOW_START = now
            _GITHUB_REQ_COUNT = 0
        if _GITHUB_REQ_COUNT >= _GITHUB_MAX_PER_MIN:
            sleep_sec = 60 - (now - _GITHUB_WINDOW_START) + 1
            log.info("[code_techs] GitHub rate limit reached, sleeping %ds", int(sleep_sec))
            time.sleep(sleep_sec)
            _GITHUB_WINDOW_START = time.time()
            _GITHUB_REQ_COUNT = 0
        _GITHUB_REQ_COUNT += 1
        try:
            resp = requests.get(
                "https://api.github.com/search/issues",
                params={"q": str(query), "sort": "updated", "order": "desc", "per_page": 8},
                headers=headers,
                timeout=20
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
                    "labels": [label.get("name", "") for label in item.get("labels", [])]
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
    now = datetime.now(timezone.utc)
    for lead in leads:
        # Skip archived leads older than 30 days
        if lead.get("archived_at"):
            try:
                arch_dt = datetime.fromisoformat(lead["archived_at"]).replace(tzinfo=timezone.utc)
                if now - arch_dt > timedelta(days=30):
                    continue
            except Exception:
                pass
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
            pursued=False,
            archived_at=None
        ))
    ranked.sort(key=lambda op: (op.score, op.estimated_value_usd), reverse=True)
    return ranked[:max_items]

def _clean_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]

def _score(text: str, labels: list[str], value: float) -> int:
    score = 30
    if value:
        score += min(35, int(value / 5))
    if _is_ai_automatable(text):
        score += 20
    if any(word in text for word in ("bounty", "reward")):
        score -= 18
    if any(word in text for word in ("paid", "fixed-price", "service", "offer")):
        score += 6
    if _has_any(text, ("ci", "test", "flaky", "failing")):
        score += 14
    if any(word in text for word in ("migration", "deprecation", "upgrade", "compatibility")):
        score += 12
    if _is_announcement_maintenance_lead(text):
        score += 12
    if any(word in text for word in ("python 3.12", "node 20", "pyproject", "deprecated", "warning")):
        score += 10
    if any(word in text for word in ("docs", "readme", "example", "quickstart")):
        score += 10
    if any(word in text for word in ("import error", "install", "setup", "starter", "template")):
        score += 8
    if any(word in text for word in ("release notes", "breaking change", "changelog")):
        score += 6
    if any(word in text for word in ("design", "logo", "marketing", "translation", "rewrite")):
        score -= 12
    if "good first issue" in " ".join(labels):
        score -= 4
    return max(0, min(100, score))

def _extract_value(text: str, cfg: dict) -> float:
    amounts = [float(m.group(1).replace(",", "")) for m in re.finditer(r"\$(\d[\d,]*(?:\.\d+)?)", text)]
    if amounts:
        return round(max(amounts), 2)
    target = float(cfg.get("daily_target_usd", 10.0) or 10.0)
    if any(word in text for word in ("paid", "fixed-price", "service")):
        return target
    return 0.0

def _reason(text: str, labels: list[str], value: float) -> str:
    parts: list[str] = []
    if value:
        parts.append(f"visible or inferred value around ${value:.2f}")
    if _is_starter_template_lead(text):
        parts.append("clean-checkout install/build proof fits automated AI patching")
        parts.append("template compatibility fixes are easy for maintainers to review")
    if _is_ai_automatable(text):
        parts.append("public proof makes this suitable for automated AI patching")
    if _is_announcement_maintenance_lead(text):
        parts.append("scoped admin feature with RBAC, expiry, env config, docs, and demo proof")
    if _has_any(text, ("ci", "test", "flaky", "failing")):
        parts.append("CI/test work is concrete and easy for maintainers to accept")
    if any(word in text for word in ("migration", "deprecation", "upgrade", "compatibility")):
        parts.append("migration chores are neglected but urgent")
    if any(word in text for word in ("python 3.12", "node 20", "pyproject", "deprecated", "warning")):
        parts.append("runtime and toolchain drift creates urgent maintenance demand")
    if any(word in text for word in ("docs", "readme", "example", "quickstart")):
        parts.append("working docs convert into trust quickly")
    if any(word in text for word in ("import error", "install", "setup", "starter", "template")):
        parts.append("setup failures are high‑friction and easy to prove")
    if not parts:
        parts.append("small code maintenance lead with low competition")
    return "; ".join(parts[:2])

def _next_step(text: str) -> str:
    if _is_announcement_maintenance_lead(text):
        return "Inspect existing admin/RBAC/env docs, then patch the announcement and maintenance-mode paths with demo proof."
    if _is_starter_template_lead(text):
        return "Pick one starter repo with a failing quickstart, capture the install/build error, patch the dependency or command, and offer the cleanup at a fixed price."
    if "bounty" in text:
        return "Skip unless the issue also has public reproduction steps the AI agent can patch and verify automatically."
    if any(word in text for word in ("migration", "deprecation", "upgrade", "compatibility")):
        return "Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup."
    if any(word in text for word in ("python 3.12", "node 20", "pyproject", "deprecated", "warning")):
        return "Reproduce on the current runtime, patch the compatibility issue, and note the exact version boundary."
    if any(word in text for word in ("ci", "test", "flaky", "failing")):
        return "Open the latest failed job, capture the failure signature, and patch only the failing path."
    if any(word in text for word in ("docs", "readme", "example", "quickstart")):
        return "Run the documented example from a clean checkout and submit the corrected command or snippet."
    return "Reproduce locally, write a short maintainer note, and keep the first patch under one focused change."

def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms)

def _is_announcement_maintenance_lead(text: str) -> bool:
    return "notification" in text and "announcements" in text and "maintenance mode" in text

def _is_starter_template_lead(text: str) -> bool:
    return "starter" in text and "template" in text and _has_any(text, ("quickstart", "install", "build"))

def _is_ai_automatable(text: str) -> bool:
    proof_terms = (
        "ci",
        "test",
        "failing",
        "error",
        "log",
        "quickstart",
        "readme",
        "docs",
        "example",
        "install",
        "build",
        "deprecation",
        "migration",
        "compatibility",
        "warning",
    )
    private_context_terms = ("private", "credentials", "account", "manual review", "design", "brand")
    return any(term in text for term in proof_terms) and not any(term in text for term in private_context_terms)

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
    lines = ["# Code-Tech Earning Queue", "", f"Refreshed: {state.get('last_refresh_at')}", f"Daily target: ${float(state.get('daily_target_usd', 10.0) or 10.0):.2f}", "", "## Requirements", ""]
    for item in state.get("requirements", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Underserved Focus", ""]) 
    for item in state.get("focus", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Strategy Playbook", ""]) 
    for item in state.get("strategy_playbook", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Avoid", ""]) 
    for item in state.get("avoid_patterns", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Ranked Leads", ""]) 
    for index, op in enumerate(state.get("opportunities", []), start=1):
        title = op.get("title", "untitled")
        url = op.get("url", "")
        pursued_tag = " [PURSUED]" if op.get("pursued") else ""
        heading = f"{index}. [{title}]({url}){pursued_tag}" if url else f"{index}. {title}{pursued_tag}"
        lines.extend([
            heading,
            f"   - Score: {op.get('score', 0)}/100",
            f"   - Value signal: ${float(op.get('estimated_value_usd', 0) or 0):.2f}",
            f"   - Why: {op.get('reason', '')}",
            f"   - Next: {op.get('next_step', '')}",
        ])
    _REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
