"""
Earning Module — Articles
Generates one developer article per cycle and publishes it.

Activates with: DEV_TO_API_KEY  and/or  MEDIUM_INTEGRATION_TOKEN
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from bot.utils import sanitize_tags

def _load_strategy() -> dict:
    try:
        return json.loads(Path("config/strategy.json").read_text())
    except Exception:
        return {}

_strategy  = _load_strategy().get("articles", {})
_MIN_WORDS = int(_strategy.get("min_words", 600))
_ESTIMATED_USD_PER_PUBLISH = float(_strategy.get("estimated_usd_per_publish", 0.0))
_CTA_LABEL_DEFAULT = str(_strategy.get("cta_label_default", "Support this project")).strip()
_CTA_UTM_CAMPAIGN = str(_strategy.get("cta_utm_campaign", "e_evolve_content_loop")).strip()
_BUYER_INTENT_RATIO = float(_strategy.get("buyer_intent_ratio", 0.35))
_CURRENT_MARKET_SIGNALS = [
    str(item).strip()
    for item in _strategy.get("current_market_signals", [])
    if str(item).strip()
]
_MONETIZATION_ANGLES = [
    str(item).strip()
    for item in _strategy.get("monetization_angles", [])
    if str(item).strip()
]

log = logging.getLogger(__name__)

_SYSTEM = (
    "You are a senior software engineer and AI practitioner writing for an audience of professional developers."
    " Your readers ship production systems daily — they are impatient with fluff,"
    " respect hard-won experience, and will stop reading the moment you waste their time.\n\n"
    "VOICE AND TONE:\n"
    "- Write as a practitioner talking to peers — direct, confident, occasionally dry.\n"
    "- First-person is fine but earn it: share a real decision, a real mistake, a real number.\n"
    "- No motivational language ('unlock the power of...', 'revolutionise your workflow').\n"
    "- No hedging ('you might want to consider...') — state opinions clearly.\n"
    "- Prefer precise nouns over adjectives: 'a 400ms p99 latency' beats 'slow response times'.\n"
    "- Contractions are fine. Jargon is fine when accurate; define it once if rare.\n"
    "- Vary article style: tutorial (step-by-step), opinion/hot-take, post-mortem/failure story,"
    " comparison (A vs B), reference/cheatsheet, or explainer. Match style to topic.\n\n"
    "Respond with ONLY a single JSON object.\n\n"
    "Schema:\n"
    '{\n'
    '  "title": "Specific, outcome-focused title — no clickbait, no vague superlatives",\n'
    '  "tags": ["tag1", "tag2", "tag3"],\n'
    '  "description": "One crisp sentence summarising the concrete takeaway. Under 155 chars.",\n'
    f'  "body_markdown": "Full article in Markdown. At least {_MIN_WORDS} words. Follow structure rules below."\n'
    '}\n\n'
    "body_markdown STRUCTURE RULES (follow exactly):\n"
    "1. Open with a 2-3 sentence hook: a concrete situation, surprising number, or sharp observation."
    " No heading. No 'In this article...'.\n"
    "2. Use ## (H2) for 4-6 major sections. Use ### (H3) for sub-points when the section warrants it.\n"
    "3. Every code example in a fenced block with language tag (```python, ```bash, ```yaml, ```json,"
    " ```typescript, ```sql, ```dockerfile, etc.).\n"
    "4. At least 3 code examples. Each must be >6 lines, production-realistic, copy-pasteable."
    " Add a single-line comment explaining the non-obvious parts — not every line.\n"
    "5. Bullet lists only for true parallel items (3+). Prose flows as paragraphs, not fragmented bullets.\n"
    "6. Bold (**text**) for: critical warnings, key terms on first use, important CLI flags. Sparingly.\n"
    "7. Include at least one concrete result, metric, or failure story — something that happened, with numbers.\n"
    "8. End with ## Key Takeaways: 3-5 tight bullet points, each one actionable or decision-relevant.\n"
    "9. Banned phrases: 'In this article', 'In conclusion', 'As you can see', 'It's worth noting',"
    " 'leverage', 'seamless', 'game-changer', 'cutting-edge', 'deep dive', 'robust solution'.\n"
    "10. Do NOT wrap the entire body in a code fence. Plain markdown only.\n\n"
    "MONETIZATION PRIORITIES:\n"
    "- Prefer topics that connect implementation detail to buyer intent: AI automation tools,"
    " SaaS comparisons, digital product templates, newsletters, productized automation services,"
    " and cost-saving workflows for solo builders or small teams.\n"
    "- Never invent affiliate links, sponsor claims, revenue screenshots, or current market data."
    " If a claim needs fresh proof and none is supplied, phrase it as a practical observation.\n"
    "- Make the article independently useful. The reader should get value even if they never click a CTA.\n\n"
    "Topic domains: Python, JavaScript/TypeScript, systems programming, AI/ML engineering,"
    " DevOps/infrastructure, databases, security, web development, open-source tooling,"
    " software architecture, career/engineering culture. Pick whichever domain fits the topic."
    " Ground every article in real implementation detail — not theory."
)

_TOPICS = [
    # AI / LLM Engineering
    "How I built a self-improving bot that earns money while I sleep",
    "Building autonomous AI agents with free LLM APIs — a practical guide",
    "Multi-provider LLM fallback in Python: never let your bot go dark",
    "Prompt engineering for code generation: what actually works in 2026",
    "Structuring LLM outputs as JSON: parsing strategies that don't break",
    "Claude Sonnet 4.6 vs Haiku 4.5: cost-performance tradeoffs for autonomous agents",
    "Agentic AI in 2026: patterns that survived contact with production",
    "Free LLM APIs in 2026: Groq, Anthropic, Gemini, OpenRouter compared",
    "RAG without a vector database: BM25 + reranking in pure Python",
    "Fine-tuning vs prompting: when each approach actually wins",
    "LLM evals that don't lie: building an honest benchmark for your use case",
    "Context window management for long-running AI agents",
    "A practical AI automation affiliate funnel for developers who hate marketing",
    "How to compare AI SaaS tools without becoming a review farm",
    "Turning an internal AI script into a paid template or checklist",
    "Building a newsletter-first funnel for technical products",
    "Productized automation services: the boring path from script to invoice",
    "How to make short-form automation demos feed durable technical articles",
    # Python
    "Python dataclasses vs dicts vs Pydantic: when each wins in production",
    "Exponential backoff in Python: the right way to retry API calls",
    "Building observable autonomous bots: logging strategies that scale",
    "Why I store my bot's state in a JSON file instead of a database",
    "AST-based code safety checks: letting LLMs edit your repo without breaking it",
    "Python subprocess tricks for running CLI tools from autonomous agents",
    "Self-healing code: how bots can detect and fix their own regressions",
    "Python typing in 2026: what's actually useful vs ceremony",
    "Async Python for I/O-heavy bots: avoiding the footguns",
    "Writing Python packages that are easy to test without mocks",
    # GitHub Actions / DevOps
    "GitHub Actions is a free cloud computer — 8 things you can automate for $0",
    "Cron jobs on GitHub Actions: gotchas and best practices in 2026",
    "How to version a bot that modifies its own source code safely",
    "GitHub Actions secrets management for multi-provider AI pipelines",
    "Docker layer caching that actually works in CI in 2026",
    "Deploying a Python service to a $5 VPS with zero downtime",
    "Monitoring a side project for free: uptime, alerts, logs",
    # Web / TypeScript / JavaScript
    "Building a real-time dashboard with plain WebSockets — no framework needed",
    "TypeScript strict mode in 2026: the settings that matter",
    "Next.js App Router vs Pages Router: a year in production, honest verdict",
    "Server-sent events vs WebSockets: when each is the right call",
    "Writing a REST API in pure Node.js — no Express, no bloat",
    # Databases / Storage
    "SQLite in production: the surprising cases where it's the right call",
    "PostgreSQL indexing mistakes I made and how I fixed them",
    "Redis as a job queue: simple patterns that actually hold up",
    "Choosing between S3, R2, and Backblaze for a side project in 2026",
    # Security
    "Secrets management for solo developers: what actually matters",
    "OWASP Top 10 for Python APIs: the ones that bite you first",
    "JWT vs session cookies: the decision nobody makes consciously enough",
    # Software Architecture / Career
    "The 5-file architecture: keeping side projects alive for years",
    "When to use a monorepo — and when it's just overhead",
    "Writing technical articles with AI assistance: a realistic breakdown",
    "How I use GitHub Actions as a personal cron platform for $0",
    "The economics of running a dev content bot: real numbers after 440 cycles",
]

_BUYER_INTENT_TOPICS = list(_strategy.get("buyer_intent_topics", [
    "How to replace a paid cron service with GitHub Actions for $0",
    "Building an AI content pipeline that publishes without paid infrastructure",
    "Free LLM APIs for solo developers: when to use Groq, Gemini, or OpenRouter",
    "How to build a sponsor-ready open-source dashboard in one afternoon",
    "Turning technical articles into a free lead funnel without spamming readers",
    "The no-budget stack I use for autonomous side projects",
    "How to add a donation or sponsor CTA to developer content without sounding desperate",
    "Building a small automation product before paying for hosting",
]))

_RESEARCH_ANGLES = [
    "Include one implementation tradeoff, one operational metric, and one failure mode.",
    "Compare the boring production choice against the tempting shortcut.",
    "Explain what changes when the same system runs unattended every hour.",
    "Ground the article in GitHub Actions constraints: logs, secrets, retries, and state.",
    "Show how to keep AI-generated code reviewable instead of magical.",
]

_RESEARCH_SYSTEM = (
    "You prepare compact research briefs for a technical writing bot. "
    "Use only the supplied project facts and evergreen engineering knowledge. "
    "Do not invent current events, prices, citations, or benchmark dates. "
    "Respond with ONLY a single JSON object with keys: brief, angle, risks, examples."
)


@dataclass
class Result:
    platform: str
    title: str = ""
    url: str = ""
    success: bool = False
    error: Optional[str] = None
    error_type: Optional[str] = None
    estimated_usd: float = 0.0


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Generate one article and publish to every active platform."""
    devto_key = os.getenv("DEV_TO_API_KEY", "").strip()
    medium_tok = os.getenv("MEDIUM_INTEGRATION_TOKEN", "").strip()

    if not devto_key and not medium_tok:
        return []

    sequence = int(status.get("_article_sequence", 0) or 0)
    status["_article_sequence"] = sequence + 1

    article = _generate(llm, status, sequence)
    if not article:
        return []

    results: list[Result] = []
    if devto_key:
        results.append(_post_devto(_with_free_cta(article, "devto"), devto_key))
    if medium_tok:
        results.append(_post_medium(_with_free_cta(article, "medium"), medium_tok))

    for r in results:
        if r.success:
            log.info("[articles] Published on %s: %s", r.platform, r.url)
        else:
            log.warning("[articles] %s failed: %s", r.platform, r.error)

    return [vars(r) for r in results]


def _with_free_cta(article: dict, platform: str = "article") -> dict:
    """Append an optional tracked, no-cost monetization CTA to article content."""
    url = os.getenv("EARN_CTA_URL", "").strip()
    if not url:
        return article
    if not url.startswith(("https://", "http://")):
        log.warning("[articles] Ignoring EARN_CTA_URL because it is not http(s)")
        return article

    label = os.getenv("EARN_CTA_LABEL", "").strip() or _CTA_LABEL_DEFAULT
    label = label.replace("[", "").replace("]", "").strip()[:80] or _CTA_LABEL_DEFAULT
    tracked_url = _tracked_cta_url(url, platform, "article")
    footer = (
        "\n\n---\n\n"
        f"If this was useful, [{label}]({tracked_url}). "
        "This keeps the project running without paid infrastructure."
    )
    updated = dict(article)
    body = str(updated.get("body_markdown", "")).rstrip()
    if url not in body and tracked_url not in body:
        updated["body_markdown"] = body + footer
    return updated


def _tracked_cta_url(url: str, source: str, medium: str) -> str:
    """Add stable UTM tags so the owner can see which channel converts."""
    if not url.startswith(("https://", "http://")):
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.setdefault("utm_source", source)
    query.setdefault("utm_medium", medium)
    query.setdefault("utm_campaign", _CTA_UTM_CAMPAIGN or "e_evolve_content_loop")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _estimated_usd() -> float:
    """Assign conservative configured value for a successfully published article."""
    return max(0.0, round(_ESTIMATED_USD_PER_PUBLISH, 6))


# ── Generation ────────────────────────────────────────────────────────────────

def _classify_gen_error(exc: Exception) -> str:
    s = str(exc).lower()
    if "timeout" in s or "timed out" in s:
        return "llm_timeout"
    if "json" in s or "parse" in s or "decode" in s or "assertionerror" in type(exc).__name__.lower():
        return "llm_json"
    if "quota" in s or "rate" in s or "429" in s or "limit" in s:
        return "llm_quota"
    return "unknown"


def _generate(llm: Any, status: dict, sequence: int = 0) -> Optional[dict]:
    n     = int(status.get("total_runs", 1) or 1)
    topic_seed = (n * 10) + sequence
    topic, conversion_mode = _select_topic(topic_seed)
    angle = _RESEARCH_ANGLES[topic_seed % len(_RESEARCH_ANGLES)]
    context = _research_context(llm, status, topic, angle, conversion_mode)
    try:
        prompt = (
            f'Write a developer article about: "{topic}"\n'
            f"{context}\n"
            "JSON only."
        )
        if hasattr(llm, "complete_json_for_role"):
            art = llm.complete_json_for_role("post", prompt, system=_SYSTEM, max_tokens=4000)
        else:
            art = llm.complete_json(prompt, system=_SYSTEM, max_tokens=4000)
        assert art.get("title") and art.get("body_markdown"), "missing title or body"
        log.info("[articles] Generated: %s", art["title"][:70])
        return art
    except Exception as exc:
        error_type = _classify_gen_error(exc)
        log.error("[articles] Generation failed [%s]: %s", error_type, exc)
        return None


def _select_topic(run_number: int) -> tuple[str, bool]:
    """Choose evergreen topics, occasionally favoring conversion intent when a CTA exists."""
    import hashlib

    has_cta = bool(os.getenv("EARN_CTA_URL", "").strip())
    buyer_topics = [str(t).strip() for t in _BUYER_INTENT_TOPICS if str(t).strip()]
    ratio = min(1.0, max(0.0, _BUYER_INTENT_RATIO))
    bucket = int(hashlib.md5(f"buyer:{run_number}".encode()).hexdigest(), 16) % 100
    use_buyer_topic = has_cta and buyer_topics and bucket < int(ratio * 100)
    pool = buyer_topics if use_buyer_topic else _TOPICS
    idx = int(hashlib.md5(str(run_number).encode()).hexdigest(), 16) % len(pool)
    return pool[idx], use_buyer_topic


def _research_context(llm: Any, status: dict, topic: str, angle: str, conversion_mode: bool = False) -> str:
    """Build a compact research brief from local bot state for article generation."""
    earn = status.get("earnings", {})
    evo = status.get("last_evolution", {})
    active = status.get("active_features", [])
    inactive = status.get("inactive_features", [])
    conversion_note = (
        "- Monetization context: a free article CTA is configured. Write for readers with a real implementation problem, "
        "make the article useful without clicking anything, and let the footer CTA do the selling.\n"
        if conversion_mode else
        "- Monetization context: prioritize trust and usefulness over promotion.\n"
    )
    signal_note = _market_signal_note(topic)
    local_brief = (
        f"Research brief:\n"
        f"- Topic: {topic}\n"
        f"- Required angle: {angle}\n"
        f"{signal_note}"
        f"{conversion_note}"
        f"- Bot cycle: #{status.get('total_runs', 1)}\n"
        f"- Active modules: {active}\n"
        f"- Inactive modules: {inactive[:6]}\n"
        f"- Earnings: total=${float(earn.get('total_usd', 0) or 0):.2f}, "
        f"week=${float(earn.get('this_week_usd', 0) or 0):.2f}, "
        f"last_cycle=${float(earn.get('last_cycle_usd', 0) or 0):.4f}\n"
        f"- Last evolution: {str(evo.get('summary', 'none'))[:180]}\n"
        "Use these facts as constraints. Do not invent outside citations, prices, or benchmark dates."
    )
    if not hasattr(llm, "complete_json_for_role"):
        return local_brief
    try:
        prompt = (
            f"{local_brief}\n\n"
            "Turn this into a concise writing brief. Include one strong thesis, "
            "three concrete example ideas, and two accuracy risks to avoid."
        )
        brief = llm.complete_json_for_role("research", prompt, system=_RESEARCH_SYSTEM, max_tokens=900)
        return (
            f"{local_brief}\n\n"
            f"Research model brief: {brief.get('brief', '')}\n"
            f"Suggested angle: {brief.get('angle', '')}\n"
            f"Example ideas: {brief.get('examples', [])}\n"
            f"Accuracy risks: {brief.get('risks', [])}"
        )
    except Exception as exc:
        log.warning("[articles] Research role unavailable; using local brief: %s", exc)
        return local_brief


def _market_signal_note(topic: str) -> str:
    """Select configured market signals that should steer conversion-focused writing."""
    import hashlib

    lines: list[str] = []
    if _CURRENT_MARKET_SIGNALS:
        start = int(hashlib.md5(topic.encode()).hexdigest(), 16) % len(_CURRENT_MARKET_SIGNALS)
        picked = [
            _CURRENT_MARKET_SIGNALS[(start + offset) % len(_CURRENT_MARKET_SIGNALS)]
            for offset in range(min(2, len(_CURRENT_MARKET_SIGNALS)))
        ]
        lines.append("- Current market signals: " + " | ".join(picked))
    if _MONETIZATION_ANGLES:
        idx = int(hashlib.md5(f"angle:{topic}".encode()).hexdigest(), 16) % len(_MONETIZATION_ANGLES)
        lines.append(f"- Monetization angle: {_MONETIZATION_ANGLES[idx]}")
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


# ── dev.to ────────────────────────────────────────────────────────────────────

def _post_devto(article: dict, api_key: str) -> Result:
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://dev.to/api/articles",
                headers={"api-key": api_key, "Content-Type": "application/json"},
                json={"article": {
                    "title":         article["title"],
                    "body_markdown": article["body_markdown"],
                    "published":     True,
                    "tags":          sanitize_tags(article.get("tags", []), max_tags=4),
                    "description":   article.get("description", ""),
                }},
                timeout=30,
            )
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 60))
                log.warning("[articles] dev.to rate limited — sleeping %ds", retry_after)
                time.sleep(retry_after)
                continue
            if resp.status_code in (400, 401, 403, 422):
                return Result(platform="dev.to",
                              error=f"HTTP {resp.status_code}: {resp.text[:150]}")
            resp.raise_for_status()
            url = resp.json().get("url", "https://dev.to")
            return Result(platform="dev.to", title=article["title"],
                          url=url, success=True, estimated_usd=_estimated_usd())
        except requests.HTTPError as exc:
            return Result(platform="dev.to",
                          error=f"HTTP {exc.response.status_code}: {exc.response.text[:100]}")
        except Exception as exc:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                return Result(platform="dev.to", error=str(exc)[:200])
    return Result(platform="dev.to", error="max retries exceeded")


# ── Medium ────────────────────────────────────────────────────────────────────

def _post_medium(article: dict, token: str) -> Result:
    auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    last_exc: Optional[Exception] = None
    for attempt in range(3):
        try:
            me  = requests.get("https://api.medium.com/v1/me", headers=auth, timeout=15)
            me.raise_for_status()
            uid = me.json()["data"]["id"]

            resp = requests.post(
                f"https://api.medium.com/v1/users/{uid}/posts",
                headers=auth,
                json={
                    "title":         article["title"],
                    "contentFormat": "markdown",
                    "content":       f"# {article['title']}\n\n{article['body_markdown']}",
                    "publishStatus": "public",
                    "tags":          sanitize_tags(article.get("tags", []), max_tags=5),
                },
                timeout=30,
            )
            if resp.status_code in (400, 401, 403):
                return Result(platform="medium",
                              error=f"HTTP {resp.status_code}: {resp.text[:150]}")
            resp.raise_for_status()
            url = resp.json()["data"].get("url", "https://medium.com")
            return Result(platform="medium", title=article["title"],
                          url=url, success=True, estimated_usd=_estimated_usd())
        except Exception as exc:
            last_exc = exc
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
    return Result(platform="medium", error=str(last_exc)[:200] if last_exc else "max retries exceeded")
