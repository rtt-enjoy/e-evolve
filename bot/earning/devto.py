"""
dev.to publishing and the house-style gates shared by everything published there.

``articles`` and ``newsletter`` are two products on one platform under one
byline, so they must not drift apart on fabrication, tone, markdown handling,
or the publish call itself. Those pieces live here, as a public API.

They used to live in ``articles`` and ``newsletter`` reached in for the
underscore-prefixed names -- an import that contradicted what the prefix
promised. Anything both modules rely on belongs here; anything specific to one
product (essay structure, digest structure) stays in that product's module.
"""
from __future__ import annotations

import json
import logging
import re
import time
import random
from typing import Any

import requests
from requests.exceptions import HTTPError

from . import payout

log = logging.getLogger(__name__)

TONE_PATTERNS = [
    (r"\bin today's (world|fast-paced)", "cliche opener \"in today's world\""),
    (r"\b(revolutionary|game.changing|cutting.edge|paradigm shift)\b", "hype language"),
    (r"\b(simply|just) (use|run|add|call|do|install)\b", "condescending \"simply/just\""),
    (r"\bobviously\b", "condescending \"obviously\""),
    (r"\b(utilize|utilise|leverage|commence|endeavour|endeavor)\b", "corporate jargon"),
    (r"\b(delve|dive) (in|into) the (world|realm)\b", "cliche \"dive into the world\""),
    (r"\bit is worth noting that\b", "filler phrase"),
    (r"\b(unleash|supercharge|turbocharge|skyrocket)\b", "marketing verb"),
    (r"!(\s|$)", "exclamation mark"),
]


def tone_problems(body: str) -> list[str]:
    """Flag writing that breaks the clear, friendly, jargon-free house style."""
    prose = strip_code_blocks(body)
    found: list[str] = []
    for pattern, label in TONE_PATTERNS:
        if re.search(pattern, prose, re.IGNORECASE) and label not in found:
            found.append(label)

    sentences = [s for s in re.split(r"[.!?]+\s", prose) if len(s.split()) > 2]
    if sentences:
        avg = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg > 26:
            found.append(f"sentences too long (avg {avg:.0f} words, aim under 22)")
    return found

FABRICATION_PATTERNS = [
    (r"\b\d+\s*[-‐-―~]?\s*\d*\s*ms\b", "invented latency figures (ms)"),
    (r"\$\s?\d+(\.\d+)?\s*(/|per\s)", "invented pricing"),
    (r"\b\d+(\.\d+)?\s*(tokens?/s|tok/s|req/s|requests?/(sec|second))\b", "invented throughput"),
    (r"\b\d+\s*%\s*(faster|slower|cheaper|better|more accurate)\b", "invented benchmark deltas"),
]


def strip_code_blocks(body: str) -> str:
    """Remove fenced code and inline code so only prose claims are checked."""
    body = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", " ", body)


def fabrication_problems(body: str) -> list[str]:
    """Flag unverifiable numeric claims in prose and tables.

    The model cannot know current latency, pricing, or throughput, and stating
    them as fact is the fastest way to lose a technical reader.
    """
    prose = strip_code_blocks(body)
    found: list[str] = []
    for pattern, label in FABRICATION_PATTERNS:
        if re.search(pattern, prose, re.IGNORECASE) and label not in found:
            found.append(label)
    return found


def strip_fabricated_tables(body: str) -> tuple[str, int]:
    """Delete markdown tables containing invented specs. Returns (body, count).

    A spec table is the model's favourite way to fabricate: it reaches for
    latency, parameter counts, and prices to fill cells. Removing the table
    keeps the rest of a good article publishable, and costs no LLM call.
    """
    lines = body.split("\n")
    out: list[str] = []
    removed = 0
    i = 0
    while i < len(lines):
        if "|" in lines[i]:
            start = i
            while i < len(lines) and "|" in lines[i]:
                i += 1
            block = lines[start:i]
            if len(block) >= 2 and fabrication_problems("\n".join(block)):
                removed += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if out and out[-1].strip() and i < len(lines):
                    out.append("")
                continue
            out.extend(block)
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out), removed


def normalize(data: dict) -> dict:
    """Clean up markdown artifacts that hurt rendering on dev.to."""
    body = str(data.get("body_markdown", ""))
    if body.lstrip().startswith("```markdown"):
        body = re.sub(r"^\s*```markdown\s*\n", "", body)
        body = re.sub(r"\n```\s*$", "", body)
    body = re.sub(r"^# (?!#)", "## ", body, flags=re.MULTILINE)
    body = re.sub(r"^(#{2,3} )\d+[.)]\s+", r"\1", body, flags=re.MULTILINE)
    body = re.sub(r"\n{4,}", "\n\n\n", body)
    body = re.sub(r"(?<!\n)\n(#{2,3} )", r"\n\n\1", body)
    body = re.sub(r"^(#{2,3} .*\n)(?!\n)(?=\S)", r"\1\n\n", body, flags=re.MULTILINE)
    data["body_markdown"] = body.strip()

    tags = [
        re.sub(r"[^a-z0-9]", "", str(t).lower())
        for t in (data.get("tags") or ["python", "automation"])
    ]
    data["tags"] = [t for t in tags if t][:4] or ["python", "automation"]
    return data


def own_post_urls(status: dict) -> list[str]:
    """This account's own dev.to post URLs, for excluding them as sources.

    The bot publishes into the same dev.to programming tag it reads as a
    trending feed, so without this its own posts come back as other people's
    news. Derived from the articles the key already owns -- no new secret and no
    hardcoded handle, so it keeps working if the account is renamed.
    """
    hist = (status or {}).get("article_history") or {}
    return [str(u) for u in hist.get("own_urls", []) if u]


def _request_with_retry(method: str, url: str, headers=None, json=None, timeout=30, max_retries=3, base_delay=1, max_delay=30):
    """Execute an HTTP request with exponential backoff for HTTP 429 errors."""
    for attempt in range(max_retries + 1):
        try:
            resp = requests.request(method, url, headers=headers, json=json, timeout=timeout)
            resp.raise_for_status()
            return resp
        except HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries:
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, base_delay), max_delay)
                time.sleep(delay)
                continue
            raise
        except Exception:
            if attempt < max_retries:
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, base_delay), max_delay)
                time.sleep(delay)
                continue
            raise


def publish(article: dict, api_key: str) -> dict:
    """Publish article to dev.to and return action result.

    The support footer is attached here rather than in either product, for two
    reasons. It is one call site for both, so a future third product cannot
    ship without it. And it lands *after* every quality gate has run: the
    footer adds a heading and an untagged fence, which would otherwise trip
    ``articles._format_problems`` and pad the word count enough to carry a
    too-thin draft past its minimum. Gates judge what the model wrote; the
    footer is appended to what they approved.
    """
    article = payout.add_footer(dict(article))
    url = "https://dev.to/api/articles"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "article": {
            "title": article.get("title", "Untitled")[:80],
            "body_markdown": article.get("body_markdown", ""),
            "description": article.get("description", "")[:150] or article.get("title", "")[:150],
            "published": True,
            "tags": article.get("tags", ["python", "automation"])[:4],
        }
    }

    try:
        resp = _request_with_retry('POST', url, headers=headers, json=payload, timeout=30)
        data = resp.json()
        article_url = data.get("url", "")
        log.info("[devto] published: %s", article_url)
        return {
            "platform": "dev.to",
            "success": True,
            "title": article.get("title", "Untitled"),
            "url": article_url,
            "estimated_usd": 0.0,
        }
    except Exception as exc:
        log.error("[devto] publish failed: %s", exc)
        return {
            "platform": "dev.to",
            "success": False,
            "error": str(exc)[:200],
            "estimated_usd": 0.0,
        }

_FRONT_MATTER_RE = re.compile(r"\A\s*---\s*$", re.MULTILINE)


def has_front_matter(body: str) -> bool:
    """True when a body opens with a YAML front-matter block."""
    return bool(_FRONT_MATTER_RE.match(body or ""))


def update_body(article_id: int, body_markdown: str, api_key: str) -> dict:
    """Replace the body of one already-published article.

    ``PUT /api/articles/{id}``, authenticated with the same ``DEV_TO_API_KEY``
    the publish and stats calls already use -- no new secret. Forem scopes the
    lookup to the key's own articles, so this can only ever touch this
    account's posts.

    Only ``body_markdown`` is sent. Absent keys are left alone by the update,
    so the title, tags and description of a post that already earns its traffic
    are not re-asserted from data this bot may have re-derived. The caller is
    responsible for having checked ``has_front_matter`` first.

    Editing does not change ``published_at``, so a post keeps its original feed
    position -- this adds an ask to what people already read, it does not
    re-promote anything.
    """
    url = f"https://dev.to/api/articles/{int(article_id)}"
    try:
        resp = _request_with_retry('PUT', url, headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/vnd.forem.api-v1+json",
        }, json={"article": {"body_markdown": body_markdown}}, timeout=30)
        data = resp.json() if resp.content else {}
        return {"success": True, "url": str(data.get("url") or "")}
    except Exception as exc:
        log.warning("[devto] update %s failed: %s", article_id, exc)
        return {"success": False, "error": str(exc)[:200]}