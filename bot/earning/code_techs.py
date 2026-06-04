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

log = logging.getLogger(__name__)

_STRATEGY_FILE = Path("config/strategy.json")
_REPORT_FILE = Path("docs/code-tech-opportunities.md")

_DEFAULT_CONFIG = {
    "enabled": True,
    "refresh_hours": 24,
    "daily_target_usd": 10.0,
    "max_items": 8,
    "min_score": 55,
    "auto_pursue": False,
    "pursue_score_threshold": 75,
    "requirements": [
        "Default to online research and the configured free/low-cost research LLM before local fallback.",
        "Prefer leveraged remote-service work: productized services, retainers, async delivery, and AI-assisted systems.",
        "Prefer work that can be reproduced from public logs, docs, or a clean checkout in under 30 minutes.",
        "Prefer boring maintenance where the failure and expected fix are visible without private context.",
        "Require a deterministic command, log, docs page, or issue thread that an AI agent can use as proof.",
        "Keep the first contribution small enough for the bot to patch, test, and explain automatically.",
        "Do not count discovery or speculative upside as earnings."
    ],
    "reference_sources": [
        {
            "title": "15 High-Paying Remote Jobs With a 4-Hour Work Week",
            "url": "https://freedium-mirror.cfd/https://medium.com/@startup_Ideas/15-high-paying-remote-jobs-with-a-4-hour-work-week-and-how-people-actually-get-them-7e8d3562ff99",
            "takeaway": "The viable path is not easy money; it is rare skill, specialization, automation, retainers, async work, and results-based delivery."
        }
    ],
    "remote_service_niches": [
        "AI prompt and workflow consulting",
        "No-code or low-code automation setup",
        "AI customer-support knowledge base cleanup",
        "analytics dashboard and reporting automation",
        "SEO/content operations systems",
        "CRM, spreadsheet, and data import/export automation",
        "developer productivity and CI maintenance retainers",
        "async technical documentation fixes",
        "productized audit/checklist services",
        "micro-SaaS setup, migration, and operations help"
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
    "community_searches": [
        "\"AI prompt consultant\" \"looking for\"",
        "\"automation consultant\" \"need help\"",
        "\"no-code automation\" \"looking for\"",
        "\"AI workflow\" \"need help\"",
        "\"customer support\" \"knowledge base\" \"cleanup\"",
        "\"dashboard\" \"automate\" \"small business\"",
        "\"CRM\" \"automate\" \"export\"",
        "\"SEO\" \"content system\" \"automation\"",
        "looking for a simple tool to",
        "anyone know a tool that can",
        "need a script to automate",
        "is there a free tool for",
        "does anyone have a checklist",
        "looking for a template for",
        "small app that can export",
        "need help fixing install error",
        "quickstart fails",
        "github actions deprecated warning"
    ],
    "reddit_subreddits": [
        "smallbusiness",
        "Entrepreneur",
        "SaaS",
        "learnpython",
        "webdev",
        "automation",
        "excel",
        "Notion"
    ],
    "reddit_searches": [
        "AI prompt consultant",
        "automation consultant need help",
        "no-code automation looking for",
        "AI workflow need help",
        "knowledge base cleanup",
        "dashboard automate small business",
        "looking for a tool",
        "need a script",
        "automate this",
        "does anyone have a template",
        "is there a free tool",
        "quickstart fails"
    ],
    "max_reddit_requests": 24,
    "underserved_focus": [
        "AI prompt/workflow consulting where public before-after examples prove value",
        "productized automations that reduce repeated admin work for a small niche",
        "retainer-friendly reporting, CRM, and support-ops cleanup",
        "async deliverables that can be reviewed without meetings",
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
        "Use online sources first, then ask the research LLM to turn fresh demand signals into ranked owner actions.",
        "Borrow the article's leverage principle: sell outcomes, systems, and repeatable assets instead of hours.",
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
    ],
    "outreach": {
        "enabled": True,
        "default_price_usd": 10.0,
        "payment_label": "crypto",
        "crypto_address_env": "USDT_WALLET_ADDRESS",
        "fallback_payment_note": "Payment address is configured privately; add it manually before sending."
    }
}

_LOCAL_LEADS = [
    {
        "title": "AI workflow audit for overloaded solo founders",
        "url": "",
        "source": "local-playbook",
        "body": "Package a short audit that finds one repetitive inbox, CRM, or reporting workflow and returns a runnable automation plan plus prompt library.",
        "labels": ["ai-workflow", "automation", "productized-service"]
    },
    {
        "title": "Support knowledge base cleanup sprint",
        "url": "",
        "source": "local-playbook",
        "body": "Use public help docs or exported FAQs to identify stale support answers, missing setup paths, and AI-ready snippets for a fixed-price cleanup.",
        "labels": ["support-ops", "knowledge-base", "async"]
    },
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
    codex_prompt: str
    outreach_draft: str
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
    raw = _fetch_online_leads(cfg) or list(_LOCAL_LEADS)
    opportunities = _rank(raw, cfg, max_items=max_items, min_score=min_score)

    pursued_count = 0
    if cfg.get("auto_pursue"):
        log.warning("[code_techs] auto_pursue ignored: research-only policy forbids posting comments")

    state.update({
        "enabled": True,
        "last_refresh_at": now.isoformat(),
        "daily_target_usd": float(cfg.get("daily_target_usd", 10.0) or 10.0),
        "refresh_hours": refresh_hours,
        "opportunities": [op.__dict__ for op in opportunities],
        "requirements": _clean_list(cfg.get("requirements", [])),
        "reference_sources": _reference_sources(cfg),
        "remote_service_niches": _clean_list(cfg.get("remote_service_niches", [])),
        "online_ai_brief": _online_ai_brief(llm, raw, cfg),
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
    log.warning("[code_techs] pursue request ignored: research-only policy forbids posting comments")
    return False


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

def _fetch_online_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Fetch public, read-only leads from free sources."""
    leads = []
    leads.extend(_fetch_github_leads(cfg))
    leads.extend(_fetch_hn_leads(cfg))
    leads.extend(_fetch_reddit_leads(cfg))
    return _dedupe(leads)

def _fetch_hn_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    leads: list[dict[str, Any]] = []
    headers = {"User-Agent": "e-evolve-code-techs"}
    for query in cfg.get("community_searches", []):
        try:
            resp = requests.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": str(query),
                    "tags": "story,comment",
                    "hitsPerPage": 6,
                },
                headers=headers,
                timeout=20,
            )
            if resp.status_code in (403, 429):
                log.warning("[code_techs] HN search skipped (%s): %s", resp.status_code, query)
                continue
            resp.raise_for_status()
            for item in resp.json().get("hits", []):
                title = item.get("title") or item.get("story_title") or "Hacker News request"
                body = item.get("comment_text") or item.get("story_text") or ""
                object_id = item.get("objectID") or item.get("story_id")
                story_id = item.get("story_id") or object_id
                url = item.get("url") or (
                    f"https://news.ycombinator.com/item?id={story_id}" if story_id else ""
                )
                leads.append({
                    "title": title,
                    "url": url,
                    "source": "hacker-news",
                    "body": _strip_html(str(body)),
                    "labels": ["community-request", "free-api"],
                })
        except Exception as exc:
            log.warning("[code_techs] HN search failed for %r: %s", query, exc)
    return leads

def _fetch_reddit_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    leads: list[dict[str, Any]] = []
    subreddits = _clean_list(cfg.get("reddit_subreddits", []))
    queries = _clean_list(cfg.get("reddit_searches", [])) or _clean_list(cfg.get("community_searches", []))
    max_requests = max(0, int(cfg.get("max_reddit_requests", 24) or 0))
    if not subreddits or not queries or max_requests <= 0:
        return leads

    headers = {
        "Accept": "application/atom+xml, application/rss+xml, text/xml;q=0.9",
        "User-Agent": "e-evolve-code-techs/1.0 read-only lead research",
    }
    request_count = 0
    for subreddit in subreddits:
        for query in queries:
            if request_count >= max_requests:
                return leads
            request_count += 1
            url = (
                f"https://www.reddit.com/r/{quote_plus(subreddit)}/search.rss"
                f"?q={quote_plus(query)}&restrict_sr=1&sort=new"
            )
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code in (403, 429):
                    log.warning("[code_techs] Reddit search skipped (%s): r/%s %s", resp.status_code, subreddit, query)
                    continue
                resp.raise_for_status()
                leads.extend(_parse_reddit_rss(resp.text, subreddit))
            except Exception as exc:
                log.warning("[code_techs] Reddit search failed for r/%s %r: %s", subreddit, query, exc)
    return leads

def _parse_reddit_rss(feed_text: str, subreddit: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(feed_text)
    except ET.ParseError:
        return []

    leads: list[dict[str, Any]] = []
    for entry in root.findall(".//{*}entry"):
        title = _xml_text(entry, "title")
        body = _xml_text(entry, "content") or _xml_text(entry, "summary")
        url = ""
        for link in entry.findall("{*}link"):
            href = str(link.attrib.get("href", "")).strip()
            if href:
                url = href
                break
        if not title:
            continue
        leads.append({
            "title": title,
            "url": url,
            "source": f"reddit:r/{subreddit}",
            "body": _strip_html(body),
            "labels": ["reddit", "community-request", "free-rss"],
        })
    return leads

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
        title_for_prompt = title[:140] or "untitled code-tech lead"
        reason = _reason(text, labels, value)
        next_step = _next_step(text)
        ranked.append(Opportunity(
            title=title_for_prompt,
            url=str(lead.get("url", "")),
            source=str(lead.get("source", "unknown")),
            score=score,
            estimated_value_usd=value,
            reason=reason,
            next_step=next_step,
            codex_prompt=_codex_prompt(title_for_prompt, lead, reason, next_step),
            outreach_draft=_outreach_draft(title_for_prompt, lead, value, cfg),
            pursued=False,
            archived_at=None
        ))
    ranked.sort(key=lambda op: (op.score, op.estimated_value_usd), reverse=True)
    return ranked[:max_items]

def _clean_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]

def _reference_sources(cfg: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in cfg.get("reference_sources", []):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        out.append({
            "title": title,
            "url": str(item.get("url", "")).strip(),
            "takeaway": str(item.get("takeaway", "")).strip(),
        })
    return out

def _online_ai_brief(llm: Any, leads: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    """Use the configured research LLM to synthesize online lead signals."""
    if llm is None:
        return {
            "summary": "No LLM client was available; queue used online searches plus local fallback heuristics.",
            "owner_actions": [
                "Review the ranked leads manually before doing local implementation work.",
                "Add or refresh a free research LLM key to improve lead synthesis.",
            ],
        }

    samples = []
    for lead in leads[:12]:
        samples.append({
            "title": str(lead.get("title", ""))[:180],
            "source": str(lead.get("source", ""))[:80],
            "url": str(lead.get("url", ""))[:220],
            "excerpt": str(lead.get("body", ""))[:500],
            "labels": lead.get("labels", [])[:6] if isinstance(lead.get("labels"), list) else [],
        })

    prompt = {
        "task": "Synthesize online demand signals into remote-service earning suggestions.",
        "policy": "Research and draft suggestions only. Do not post, publish, trade, mint, request payment, or contact anyone.",
        "reference_takeaways": _reference_sources(cfg),
        "remote_service_niches": _clean_list(cfg.get("remote_service_niches", [])),
        "lead_samples": samples,
        "required_json_shape": {
            "summary": "one concise paragraph",
            "owner_actions": ["3-5 concrete next actions for the owner"],
        },
    }
    try:
        if hasattr(llm, "complete_json_for_role"):
            data = llm.complete_json_for_role("research", json.dumps(prompt), max_tokens=900)
        else:
            data = llm.complete_json(json.dumps(prompt), max_tokens=900)
    except Exception as exc:
        log.warning("[code_techs] online AI brief failed: %s", exc)
        return {
            "summary": f"Online AI brief failed; used online search and local scoring only. Error: {str(exc)[:160]}",
            "owner_actions": [
                "Use the top ranked lead with the clearest public proof.",
                "Keep local Codex implementation to one small deliverable.",
            ],
        }

    return {
        "summary": str(data.get("summary", "")).strip()[:900],
        "owner_actions": _clean_list(data.get("owner_actions", []))[:5],
    }

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
    if any(word in text for word in ("checklist", "template", "script", "automate", "export", "convert")):
        score += 10
    if any(word in text for word in ("prompt consultant", "ai workflow", "automation consultant", "no-code automation")):
        score += 16
    if any(word in text for word in ("retainer", "productized", "async", "fixed price", "workflow audit")):
        score += 12
    if any(word in text for word in ("customer support", "knowledge base", "crm", "dashboard", "reporting")):
        score += 10
    if "community-request" in labels:
        score += 8
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
    if any(word in text for word in ("retainer", "consultant", "consulting", "audit", "productized")):
        return max(target, float(cfg.get("outreach", {}).get("default_price_usd", target) or target))
    if any(word in text for word in ("paid", "fixed-price", "service")):
        return target
    if any(word in text for word in ("need", "looking for", "does anyone have", "anyone know")):
        return float(cfg.get("outreach", {}).get("default_price_usd", target) or target)
    return 0.0

def _reason(text: str, labels: list[str], value: float) -> str:
    parts: list[str] = []
    if value:
        parts.append(f"visible or inferred value around ${value:.2f}")
    if any(word in text for word in ("prompt consultant", "ai workflow", "automation consultant", "no-code automation")):
        parts.append("matches leverage-style remote service demand from AI-assisted workflows")
    if any(word in text for word in ("retainer", "productized", "async", "workflow audit")):
        parts.append("can become a repeatable async offer instead of hourly labor")
    if any(word in text for word in ("customer support", "knowledge base", "crm", "dashboard", "reporting")):
        parts.append("ops cleanup has clear business value and bounded deliverables")
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
    if any(word in text for word in ("prompt consultant", "ai workflow", "automation consultant", "no-code automation")):
        return "Find the public workflow, draft a one-page automation audit, and use the research LLM to propose a fixed-scope deliverable before any local build."
    if any(word in text for word in ("customer support", "knowledge base", "crm", "dashboard", "reporting")):
        return "Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof."
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
        "checklist",
        "template",
        "script",
        "automate",
        "export",
        "convert",
        "prompt consultant",
        "ai workflow",
        "automation consultant",
        "no-code automation",
        "knowledge base",
        "crm",
        "dashboard",
        "reporting",
    )
    private_context_terms = ("private", "credentials", "account", "manual review", "design", "brand")
    return any(term in text for term in proof_terms) and not any(term in text for term in private_context_terms)

def _codex_prompt(title: str, lead: dict[str, Any], reason: str, next_step: str) -> str:
    url = str(lead.get("url", "")).strip()
    body = str(lead.get("body", "")).strip()
    excerpt = body[:900].replace("\n", " ")
    return (
        "Implement a small, verifiable solution for this public request.\n\n"
        f"Lead: {title}\n"
        f"Source: {lead.get('source', 'unknown')}\n"
        f"URL: {url or 'no public URL'}\n"
        f"Why this is suitable: {reason}\n"
        f"First step: {next_step}\n\n"
        "Constraints:\n"
        "- Keep the first change narrowly scoped.\n"
        "- Use free APIs or offline code paths when possible.\n"
        "- Add or update a specific file that demonstrates the result.\n"
        "- Include exact verification commands and output notes.\n"
        "- Do not post externally or request payment automatically.\n\n"
        f"Request excerpt: {excerpt or 'No excerpt available.'}"
    )

def _outreach_draft(title: str, lead: dict[str, Any], value: float, cfg: dict[str, Any]) -> str:
    outreach_cfg = cfg.get("outreach", {}) or {}
    if not outreach_cfg.get("enabled", True):
        return ""
    price = value or float(outreach_cfg.get("default_price_usd", 10.0) or 10.0)
    payment_label = str(outreach_cfg.get("payment_label", "crypto")).strip() or "crypto"
    payment_note = _payment_note(outreach_cfg)
    url = str(lead.get("url", "")).strip()
    return (
        f"Hi, I found your request about \"{title}\" and can make a small working version.\n\n"
        "I will keep it simple: one focused file/change, a short usage note, and proof that it runs. "
        "If the result solves the request, the fixed price is "
        f"${price:.2f} via {payment_label}.\n\n"
        f"{payment_note}\n\n"
        f"Reference: {url or 'add the original thread URL before sending'}"
    )

def _payment_note(outreach_cfg: dict[str, Any]) -> str:
    env_name = str(outreach_cfg.get("crypto_address_env", "USDT_WALLET_ADDRESS")).strip()
    address = os.getenv(env_name, "").strip() if env_name else ""
    if address:
        return f"Payment address ({env_name}): {address}"
    return str(
        outreach_cfg.get(
            "fallback_payment_note",
            "Payment address is configured privately; add it manually before sending.",
        )
    )

def _strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def _xml_text(parent: ET.Element, tag: str) -> str:
    element = parent.find(f"{{*}}{tag}")
    if element is None or element.text is None:
        return ""
    return element.text.strip()

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
    lines.extend(["", "## Reference Sources", ""])
    for item in state.get("reference_sources", []):
        title = item.get("title", "untitled")
        url = item.get("url", "")
        takeaway = item.get("takeaway", "")
        prefix = f"- [{title}]({url})" if url else f"- {title}"
        lines.append(f"{prefix}: {takeaway}" if takeaway else prefix)
    lines.extend(["", "## Remote Service Niches", ""])
    for item in state.get("remote_service_niches", []):
        lines.append(f"- {item}")
    brief = state.get("online_ai_brief") or {}
    if brief:
        lines.extend(["", "## Online AI Brief", ""])
        summary = str(brief.get("summary", "")).strip()
        if summary:
            lines.append(summary)
            lines.append("")
        for action in brief.get("owner_actions", []):
            lines.append(f"- {action}")
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
            "   - Codex request:",
            _indent_block(str(op.get("codex_prompt", "")), "     "),
            "   - Owner-reviewed outreach draft:",
            _indent_block(str(op.get("outreach_draft", "")), "     "),
        ])
    _REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

def _indent_block(text: str, prefix: str) -> str:
    cleaned = text.strip() or "(none)"
    return "\n".join(f"{prefix}{line}" for line in cleaned.splitlines())
