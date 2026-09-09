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

from ._shared import load_config, parse_dt, strip_html, xml_text

log = logging.getLogger(__name__)

_REPORT_FILE = Path("docs/code-tech-opportunities.md")

_DEFAULT_CONFIG = {
    "enabled": True,
    "refresh_hours": 6,
    "daily_target_usd": 10.0,
    "max_items": 40,
    "status_max_items": 16,
    "prompt_top_n": 6,
    "min_score": 40,
    "min_channel_share": 0.5,
    "supply_max_age_days": 120,
    "reddit_backoff_seconds": 5,
    "auto_pursue": False,
    "pursue_score_threshold": 75,
    "requirements": [
        "Every lead must move a digital product toward earning without the owner in the loop.",
        "Rank by how little owner action each unit of income needs, not by headline upside.",
        "Name where the money lands, and prefer stablecoin to the address this project already publishes.",
        "State every cost and every manual setup step out loud; zero budget is the constraint.",
        "Never suggest selling the owner's hours: a rate per hour is a job, not passive income.",
        "Stay inside policy: no social posting, no trading, no minting, no cold outreach.",
        "Do not count discovery, pipeline, or speculative upside as earnings. On-chain or nothing."
    ],
    "free_ai_focus": [
        "free-tier LLM APIs with no credit card requirement",
        "free speech-to-text, TTS, and transcription APIs",
        "free image generation and background-removal APIs",
        "free OCR, document parsing, and PDF extraction APIs",
        "free embedding and vector-search tiers",
        "free translation and summarization APIs",
        "free AI hosting, inference, and scheduled-compute tiers",
        "open-weight models that run on free CPU/GPU allowances"
    ],
    "monetization_patterns": [
        "Ship the tool free and sell the upgrade: the free tier buys discovery the owner cannot.",
        "One-time licence for a digital download, delivered by the storefront with no owner action.",
        "Put the published receive address on the product page and in the README, so a user can pay with no platform at all.",
        "Sell a template, preset, or asset pack built once and downloaded many times.",
        "Charge for the paid tier of a tool whose free tier costs nothing per user to run.",
        "List the same product on every zero-cost channel, since the artifact is already built."
    ],
    "reference_sources": [
        {
            "title": "15 High-Paying Remote Jobs With a 4-Hour Work Week",
            "url": "https://freedium-mirror.cfd/https://medium.com/@startup_Ideas/15-high-paying-remote-jobs-with-a-4-hour-work-week-and-how-people-actually-get-them-7e8d3562ff99",
            "takeaway": "The viable path is not easy money; it is rare skill, specialization, automation, retainers, async work, and results-based delivery."
        },
        {
            "title": "OpenRouter free model list",
            "url": "https://openrouter.ai/models?max_price=0",
            "takeaway": "Free (:free) models are capped at 20 req/min and only 50 req/day unless the account has ever purchased $10 in credits (then 1,000/day) -- verify current limit before relying on volume."
        },
        {
            "title": "Google AI Studio (Gemini API)",
            "url": "https://aistudio.google.com/app/apikey",
            "takeaway": "No credit card required. Gemini 2.5 Flash free tier is roughly 1,500 requests/day; much higher daily ceiling than OpenRouter's free chain -- verify current limit."
        },
        {
            "title": "Cerebras Cloud free tier",
            "url": "https://cloud.cerebras.ai/",
            "takeaway": "No credit card required. Roughly 1M tokens/day and 14,400 requests/day per model -- verify current limit."
        }
    ],
    "product_shapes": [
        "browser extension solving one specific annoyance",
        "single-purpose desktop or CLI utility",
        "static web tool that runs entirely client-side",
        "template, preset, or asset pack for a tool people already use",
        "developer library or plugin for an existing ecosystem",
        "self-hostable script the buyer runs on their own machine",
        "data set or reference compiled once and sold as a download"
    ],
    "github_searches": [
        "awesome browser extensions in:name,readme stars:>200",
        "chrome extension boilerplate manifest v3 in:name,readme stars:>200",
        "indie hackers open source saas alternatives in:readme stars:>200",
        "awesome self-hosted single file tool in:name,readme stars:>150",
        "crypto payment button static site in:readme stars:>100",
        "awesome digital products templates in:readme stars:>100",
        "license key generator offline validation in:readme stars:>100"
    ],
    "community_searches": [
        "selling a chrome extension revenue",
        "how much my browser extension makes",
        "indie developer selling digital products revenue",
        "accept crypto payments digital product",
        "USDT payment for software licence",
        "sold my side project first sale",
        "open source project sponsorship income",
        "pay what you want pricing results",
        "freemium conversion rate indie",
        "where to sell a small utility app"
    ],
    "reddit_subreddits": [
        "SideProject",
        "sideproject",
        "indiehackers",
        "microsaas",
        "Entrepreneur",
        "chrome_extensions",
        "SaaS",
        "opensource"
    ],
    "reddit_searches": [
        "sold my digital product",
        "chrome extension revenue",
        "accept crypto payment product",
        "USDT payout platform",
        "launched my tool first sale",
        "pay what you want pricing",
        "where to list my digital product",
        "free tier paid upgrade conversion"
    ],
    "max_reddit_requests": 3,
    "underserved_focus": [
        "storefronts that settle stablecoin straight to the seller's own wallet, no custodian",
        "one-task tools that solve a single annoyance well enough to be worth paying for",
        "products with zero marginal cost per user, so the free tier can stay free forever",
        "channels that are free to list on and have no approval queue to fail",
        "paying users who never open a storefront and would rather send stablecoin directly",
        "distribution with real organic discovery, so reach does not need ad spend",
        "products whose buyers are developers, since that is the audience already reached"
    ],
    "strategy_playbook": [
        "Build the product once, then spend every later cycle on distribution rather than on more product.",
        "Keep marginal cost per user at zero: client-side code, free hosting, free scheduler. Every dollar in is margin.",
        "Put the receive path on the artifact itself -- product page, README, article footer -- not only on a storefront.",
        "List on the free channels first; pay a listing fee only where discovery is worth it, and say what it cost.",
        "Let the articles this bot already publishes do the marketing: the problem is the post, the product is the fix.",
        "Price once and leave it. A price that needs renegotiating per buyer is a service in disguise.",
        "Measure only what arrives on-chain. Listings, views and pipeline are not revenue."
    ],
    "avoid_patterns": [
        "Selling the owner's hours: freelance postings, contract work, retainers, consulting. Income per unit of work is a job.",
        "Anything requiring paid infrastructure, a monthly fee, or a credit-card-gated tier.",
        "Custodial payment processors that hold the money before the owner does, and anything demanding KYC to receive.",
        "Platforms that are dead, seized, or unverifiable. Sellix was seized in 2024 and is still widely recommended.",
        "Trading, minting, yield farming, staking and airdrops: refused in code, and not a product business.",
        "Offers needing a large audience, ad spend, or a following the owner does not have.",
        "Anything promising passive income without a product that delivers something."
    ]
}

_CHANNEL = "channel"
_ASSET = "asset"
_DEMAND = _CHANNEL
_SUPPLY = _ASSET

_PRODUCT_CHANNELS = [
    {
        "title": "Getly — sell a digital product, settle USDT on Tron to your own wallet",
        "url": "https://www.getly.store/sell/crypto",
        "source": "channel-table",
        "kind": _CHANNEL,
        "body": (
            "Digital-goods storefront with native stablecoin payouts. Buyers pay by card "
            "(Stripe) or crypto; the seller is paid out in USDT/USDC. Payouts go directly "
            "to your own wallet address -- no KYC for crypto settlement, no monthly fee. "
            "Tron (TRC-20) USDT is supported, which is the same network and asset this "
            "project already publishes a receive address for, so a sale lands in the "
            "wallet the dashboard already reads. Minimum payout is $15 on Tron ($5 on BNB "
            "Smart Chain) and the network fee (~$0.50-1 on Tron) comes out of the payout. "
            "Settlement is twice a month, not per sale."
        ),
        "labels": ["storefront", "usdt", "tron", "no-kyc", "own-wallet", "digital-product"],
        "cost_usd": 0.0,
        "manual_setup": "Owner signs up, adds the Tron receive address, and uploads the product once.",
        "verified_note": "Fees, networks, no-KYC and own-wallet payout confirmed on getly.store 2026-09-08.",
    },
    {
        "title": "itch.io — free to publish, you set the platform cut (0-100%)",
        "url": "https://itch.io/docs/creators/faq",
        "source": "channel-table",
        "kind": _CHANNEL,
        "body": (
            "Free to upload, no approval queue and no upfront fee, and it lists tools and "
            "assets rather than only games. Open revenue sharing lets the seller choose the "
            "platform's cut, default around 10%. Pay-what-you-want pricing is supported and "
            "is reported as the highest-earning model there. Payment is fiat, so this is a "
            "reach-and-revenue channel rather than a crypto one -- the crypto leg stays the "
            "wallet footer this project already ships."
        ),
        "labels": ["storefront", "free-to-publish", "pay-what-you-want", "no-approval"],
        "cost_usd": 0.0,
        "manual_setup": "Owner creates an account and uploads the product; payment details for fiat payout.",
        "verified_note": "Free publishing and open revenue share confirmed on itch.io 2026-09-08.",
    },
    {
        "title": "Chrome Web Store — one-time $5, covers up to 20 extensions",
        "url": "https://developer.chrome.com/docs/webstore/register",
        "source": "channel-table",
        "kind": _CHANNEL,
        "body": (
            "For a browser extension this is the distribution channel with real organic "
            "discovery. The developer registration fee is a one-time $5 per account, with "
            "no annual renewal and no per-extension fee, and it covers up to 20 extensions. "
            "It is stated here rather than hidden because it is the only non-zero cost on "
            "this table: the store itself takes no cut of a free extension, so monetisation "
            "is the wallet ask or a paid upgrade sold through a storefront row above."
        ),
        "labels": ["distribution", "browser-extension", "one-time-fee", "discovery"],
        "cost_usd": 5.0,
        "manual_setup": "Owner pays the one-time $5 registration and submits the extension for review.",
        "verified_note": "One-time $5, no renewal, 20-extension limit confirmed on developer.chrome.com 2026-09-08.",
    },
    {
        "title": "Wallet ask on the product page and in every article (already live)",
        "url": "",
        "source": "channel-table",
        "kind": _CHANNEL,
        "body": (
            "The channel that needs no account at all, and the only one already running: "
            "the validated receive address that bot/earning/payout.py appends to every "
            "published post. For a digital product the same address belongs on the product "
            "page and in the README, so a user who never opens a storefront can still pay. "
            "Scores top marks on every Principle 2 row -- no new secret, no owner action "
            "per unit, within policy, verifiable on-chain, reuses output already produced."
        ),
        "labels": ["wallet", "usdt", "tron", "no-account", "already-live"],
        "cost_usd": 0.0,
        "manual_setup": "None. Already publishing.",
        "verified_note": "Live since 2026-09-04; coverage observed by receipt_check each cycle.",
    },
]

_REFUSED_CHANNELS = [
    {
        "name": "Sellix",
        "why": "Seized and shut down in 2024. Still widely recommended as the crypto storefront, which is exactly why it is written down here as refused.",
    },
    {
        "name": "Gumroad (for crypto)",
        "why": "Does not natively accept crypto and pays out USD via Stripe only. Fine as a fiat storefront; it is not a crypto receive path, and mrr_ideas should not imply it is.",
    },
    {
        "name": "Buy Me a Coffee / Ko-fi (main platforms)",
        "why": "No native stablecoin field for a supporter's own wallet. Ko-fi Web3 is a separate product on BEP-20 only, so the wallet footer already covers this better.",
    },
    {
        "name": "Any custodial crypto payment processor",
        "why": "Holds the money before the owner does. The published Tron address is non-custodial and already works; adding a custodian adds KYC risk for no gain.",
    },
]

_LOCAL_LEADS = [
    {
        "title": "Ship the product free, sell the upgrade, ask in the README",
        "url": "",
        "source": "local-playbook",
        "kind": _CHANNEL,
        "body": (
            "A free tool with a paid upgrade earns while nobody is working. The free tier "
            "does the discovery the owner cannot afford to buy, the upgrade is the price, "
            "and the wallet address in the README and on the product page takes money from "
            "users who never open a storefront. No per-sale owner action, so it passes "
            "Principle 2 row 2."
        ),
        "labels": ["digital-product", "freemium", "wallet", "no-owner-action"],
    },
    {
        "title": "One product, listed on every free channel at once",
        "url": "",
        "source": "local-playbook",
        "kind": _CHANNEL,
        "body": (
            "The same digital product listed on each zero-cost storefront multiplies reach "
            "without multiplying work, because the artifact is already built. Reuse of "
            "existing output is Principle 2 row 5. The cost is one manual signup per "
            "channel, which is a one-time step rather than a per-sale one."
        ),
        "labels": ["digital-product", "distribution", "reuse", "one-time-setup"],
    },
    {
        "title": "Write the article that the product is the answer to",
        "url": "",
        "source": "local-playbook",
        "kind": _ASSET,
        "body": (
            "This bot already publishes to dev.to daily and measures which shapes earn "
            "engagement -- problem-workaround outperforms build-tutorial by roughly 25x on "
            "this account. An article about the problem, where the product is the fix and "
            "the footer is the ask, is marketing that runs on infrastructure already paid "
            "for. It needs no new secret and no owner action."
        ),
        "labels": ["reach", "devto", "already-running", "content-marketing"],
    },
    {
        "title": "Free-tier stack so the product costs nothing to run",
        "url": "",
        "source": "local-playbook",
        "kind": _ASSET,
        "body": (
            "A product that costs nothing per user can stay free at the top of the funnel "
            "forever. Client-side work needs no server at all; GitHub Pages hosts a static "
            "page and GitHub Actions runs scheduled work, both on the free tier this project "
            "already runs on. Every dollar in is margin because there is no dollar out."
        ),
        "labels": ["free-stack", "zero-budget", "no-server", "margin"],
    },
    {
        "title": "Open-source the tool and take sponsorship on the repo",
        "url": "",
        "source": "local-playbook",
        "kind": _ASSET,
        "body": (
            "A public repository is discovery that keeps working after it is published, and "
            "the wallet address in the README is a receive path that needs no platform at "
            "all. GitHub Sponsors is the fiat version and needs the owner to enable it by "
            "hand once; the address needs nothing. Recorded as an asset rather than a "
            "channel because sponsorship income is not a product sale."
        ),
        "labels": ["open-source", "discovery", "wallet", "sponsors"],
    },
]

_GITHUB_MAX_PER_MIN = 10

_AI_TERM_RE = re.compile(
    r"\b(ai|llm|gpt|whisper|ocr|embedding|embeddings|tts|"
    r"transcription|inference|vision|speech)\b"
)
_FREE_WINDOW = 60

_RATE_RE = re.compile(
    r"\$\s?(\d{2,4})(?:\s*(?:-|--|to|–|—)\s*\$?\s?(\d{2,4}))?"
    r"\s*(?:usd)?\s*(?:/|\s+per\s+)?\s*(?:hr|hour)\b",
    re.IGNORECASE,
)
_PERIOD_LABELS = {
    "hourly": "/hr", "daily": "/day", "weekly": "/wk",
    "monthly": "/mo", "annual": "/yr", "yearly": "/yr",
}


@dataclass
class Opportunity:
    title: str
    url: str
    source: str
    buyer: str
    kind: str
    score: int
    score_parts: dict[str, float]
    value_usd: float | None
    value_basis: str
    value_note: str
    posted_at: str | None
    discovered_at: str
    age_hours: float | None
    reason: str
    next_step: str
    codex_prompt: str
    cost_usd: float | None = None
    manual_setup: str = ""
    verified_note: str = ""
    pursued: bool = False


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    cfg = _config()
    state = status.setdefault("code_tech_earning", {})
    if not _enabled(cfg):
        state["enabled"] = False
        return []

    now = datetime.now(timezone.utc)
    refresh_hours = max(1, int(cfg.get("refresh_hours", 24) or 24))
    last_run = parse_dt(state.get("last_refresh_at"))
    if last_run and now - last_run < timedelta(hours=refresh_hours):
        log.info("[code_techs] queue is fresh; next refresh after %sh", refresh_hours)
        return []

    max_items = max(1, int(cfg.get("max_items", 40) or 40))
    status_max_items = max(1, int(cfg.get("status_max_items", max_items) or max_items))
    min_score = max(0, int(cfg.get("min_score", 40) or 40))
    raw = _fetch_online_leads(cfg)
    opportunities = _rank(raw, cfg, max_items=max_items, min_score=min_score)

    pursued_count = 0
    if cfg.get("auto_pursue"):
        log.warning("[code_techs] auto_pursue ignored: research-only policy forbids posting comments")

    shown = opportunities[:status_max_items]
    channels = sum(1 for op in shown if op.kind == _CHANNEL)
    priced = sum(1 for op in shown if op.value_basis != "none")
    needs_setup = sum(
        1 for op in shown
        if str(getattr(op, "manual_setup", "")).strip()
        and not str(getattr(op, "manual_setup", "")).strip().lower().startswith("none")
    )
    state.update({
        "enabled": True,
        "last_refresh_at": now.isoformat(),
        "daily_target_usd": float(cfg.get("daily_target_usd", 10.0) or 10.0),
        "refresh_hours": refresh_hours,
        "opportunities": [op.__dict__ for op in shown],
        "channel_count": channels,
        "asset_count": len(shown) - channels,
        "demand_count": channels,
        "supply_count": len(shown) - channels,
        "priced_count": priced,
        "needs_setup_count": needs_setup,
        "refused_channels": [dict(x) for x in _REFUSED_CHANNELS],
        "ranked_total": len(opportunities),
        "requirements": _clean_list(cfg.get("requirements", [])),
        "reference_sources": _reference_sources(cfg),
        "product_shapes": _clean_list(cfg.get("product_shapes", [])),
        "free_ai_focus": _clean_list(cfg.get("free_ai_focus", [])),
        "monetization_patterns": _clean_list(cfg.get("monetization_patterns", [])),
        "online_ai_brief": _online_ai_brief(llm, raw, cfg),
        "focus": _clean_list(cfg.get("underserved_focus", [])),
        "strategy_playbook": _clean_list(cfg.get("strategy_playbook", [])),
        "avoid_patterns": _clean_list(cfg.get("avoid_patterns", []))
    })
    _write_report(state, [op.__dict__ for op in opportunities])

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

def _config() -> dict[str, Any]:
    return load_config("code_techs", _DEFAULT_CONFIG)

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
        "User-Agent": "e-evolve-code-techs"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    max_age_days = max(1, int(cfg.get("supply_max_age_days", 120) or 120))
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    sent = 0
    window_start = time.time()

    for query in cfg.get("github_searches", []):
        now = time.time()
        if now - window_start >= 60:
            window_start = now
            sent = 0
        if sent >= _GITHUB_MAX_PER_MIN:
            sleep_sec = 60 - (now - window_start) + 1
            log.info("[code_techs] GitHub rate limit reached, sleeping %ds", int(sleep_sec))
            time.sleep(sleep_sec)
            window_start = time.time()
            sent = 0
        sent += 1
        try:
            resp = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": str(query), "sort": "updated", "order": "desc", "per_page": 8},
                headers=headers,
                timeout=20
            )
            if resp.status_code in (403, 422):
                log.warning("[code_techs] GitHub search skipped (%s): %s", resp.status_code, query)
                continue
            resp.raise_for_status()
            for item in resp.json().get("items", []):
                pushed = str(item.get("pushed_at") or "")
                stamp = parse_dt(pushed)
                if stamp and stamp < cutoff:
                    continue
                stars = item.get("stargazers_count") or 0
                topics = [str(t) for t in (item.get("topics") or [])]
                leads.append({
                    "title": str(item.get("full_name") or ""),
                    "url": str(item.get("html_url") or ""),
                    "source": "github",
                    "kind": _ASSET,
                    "body": str(item.get("description") or ""),
                    "labels": topics,
                    "posted_at": pushed,
                    "stars": stars,
                    "buyer": "tooling, no buyer",
                })
        except Exception as exc:
            log.warning("[code_techs] GitHub search failed for %r: %s", query, exc)
    return _dedupe(leads)

def _fetch_online_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    leads: list[dict[str, Any]] = list(_PRODUCT_CHANNELS) + list(_LOCAL_LEADS)
    leads.extend(_fetch_hn_leads(cfg))
    leads.extend(_fetch_reddit_leads(cfg))
    leads.extend(_fetch_github_leads(cfg))
    return _dedupe(leads)

def _fetch_hn_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    leads: list[dict[str, Any]] = []
    headers = {"User-Agent": "e-evolve-code-techs"}
    max_age_hours = max(1, int(cfg.get("demand_max_age_hours", 72) or 72))
    since = int((datetime.now(timezone.utc) - timedelta(hours=max_age_hours)).timestamp())
    for query in cfg.get("community_searches", []):
        try:
            resp = requests.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": str(query),
                    "tags": "story,comment",
                    "hitsPerPage": 6,
                    "numericFilters": f"created_at_i>{since}",
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
                    "kind": _ASSET,
                    "body": strip_html(str(body)),
                    "labels": ["community", "market-evidence"],
                    "posted_at": item.get("created_at"),
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
    base_backoff = max(0, int(cfg.get("reddit_backoff_seconds", 5) or 0))
    request_count = 0
    
    for index, subreddit in enumerate(subreddits):
        if request_count >= max_requests:
            break
        query = queries[index % len(queries)]
        request_count += 1
        url = (
            f"https://www.reddit.com/r/{quote_plus(subreddit)}/search.rss"
            f"?q={quote_plus(query)}&restrict_sr=1&sort=new"
        )
        # Per-subreddit exponential backoff: 5s, 10s, 20s...
        backoff = base_backoff
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code in (403, 429):
                    if attempt < max_retries:
                        log.info(
                            "[code_techs] Reddit throttled (%s) at r/%s, retry %d/%d in %ds",
                            resp.status_code, subreddit, attempt + 1, max_retries, backoff
                        )
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    else:
                        log.info(
                            "[code_techs] Reddit throttled (%s) at r/%s after %d retries; skipping this subreddit",
                            resp.status_code, subreddit, max_retries
                        )
                        break
                resp.raise_for_status()
                leads.extend(_parse_reddit_rss(resp.text, subreddit))
                break  # Success, move to next subreddit
            except Exception as exc:
                log.warning("[code_techs] Reddit search failed for r/%s %r: %s", subreddit, query, exc)
                break
    return leads

def _parse_reddit_rss(feed_text: str, subreddit: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(feed_text)
    except ET.ParseError:
        return []

    leads: list[dict[str, Any]] = []
    for entry in root.findall(".//{*}entry"):
        title = xml_text(entry, "title")
        body = xml_text(entry, "content") or xml_text(entry, "summary")
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
            "kind": _ASSET,
            "body": strip_html(body),
            "labels": ["reddit", "community", "market-evidence"],
            "posted_at": xml_text(entry, "updated") or xml_text(entry, "published"),
            "buyer": f"r/{subreddit}",
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
    now = datetime.now(timezone.utc)
    discovered_at = now.isoformat()
    max_age_hours = max(1, int(cfg.get("demand_max_age_hours", 72) or 72))
    prompt_top_n = max(0, int(cfg.get("prompt_top_n", 12) or 0))
    ranked: list[Opportunity] = []

    for lead in leads:
        title = str(lead.get("title", "")).strip()
        body = str(lead.get("body", "")).strip()
        labels = [str(x).lower() for x in lead.get("labels", [])]
        text = " ".join([title, body, " ".join(labels)]).lower()
        is_local = lead.get("source") in ("local-playbook", "channel-table")
        kind = str(lead.get("kind") or (_ASSET if is_local else _CHANNEL))

        posted = parse_dt(lead.get("posted_at"))
        age_hours = round((now - posted).total_seconds() / 3600, 1) if posted else None
        value_usd, value_basis, value_note = _lead_value(lead)
        score, parts = _score(lead, text, labels, kind, age_hours, value_basis, cfg)
        if score < min_score and not is_local:
            continue

        title_for_prompt = title[:140] or "untitled code-tech lead"
        reason = _reason(lead, text, labels, kind, value_note, age_hours)
        next_step = _next_step(lead, kind, cfg)
        ranked.append(Opportunity(
            title=title_for_prompt,
            url=str(lead.get("url", "")),
            source=str(lead.get("source", "unknown")),
            buyer=str(lead.get("buyer") or "")[:80],
            kind=kind,
            score=score,
            score_parts=parts,
            value_usd=value_usd,
            value_basis=value_basis,
            value_note=value_note,
            posted_at=posted.isoformat() if posted else None,
            discovered_at=discovered_at,
            age_hours=age_hours,
            reason=reason,
            next_step=next_step,
            codex_prompt="",
            cost_usd=_cost(lead.get("cost_usd")),
            manual_setup=str(lead.get("manual_setup") or "")[:200],
            verified_note=str(lead.get("verified_note") or "")[:200],
            pursued=False
        ))

    ranked.sort(key=lambda op: (op.score, -(op.age_hours if op.age_hours is not None else 1e9)), reverse=True)
    selected = _apply_channel_share(ranked, cfg, max_items)

    for position, op in enumerate(selected):
        if position < prompt_top_n:
            op.codex_prompt = _codex_prompt(op, cfg)
    return selected

def _apply_channel_share(
    ranked: list[Opportunity], cfg: dict[str, Any], max_items: int
) -> list[Opportunity]:
    share = cfg.get("min_channel_share", cfg.get("min_demand_share", 0.5))
    share = float(share or 0.0)
    demand = [op for op in ranked if op.kind == _CHANNEL]
    if share <= 0 or not demand:
        return ranked[:max_items]
    reserved = min(len(demand), int(max_items * min(1.0, share)))
    keep = demand[:reserved]
    kept = {id(op) for op in keep}
    for op in ranked:
        if len(keep) >= max_items:
            break
        if id(op) not in kept:
            keep.append(op)
    keep.sort(key=lambda op: op.score, reverse=True)
    return keep[:max_items]

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
    if llm is None:
        return {
            "summary": "No LLM client was available; the queue used the verified channel table plus local scoring.",
            "owner_actions": [
                "Work the verified channel rows manually; they need no model to be useful.",
                "Add or refresh a free research LLM key to improve the product angle.",
            ],
        }

    ordered = (
        [x for x in leads if x.get("kind") == _CHANNEL]
        + [x for x in leads if x.get("kind") != _CHANNEL]
    )
    samples = []
    for lead in ordered[:12]:
        samples.append({
            "title": str(lead.get("title", ""))[:180],
            "source": str(lead.get("source", ""))[:80],
            "kind": str(lead.get("kind") or ""),
            "url": str(lead.get("url", ""))[:220],
            "excerpt": str(lead.get("body", ""))[:500],
            "labels": lead.get("labels", [])[:6] if isinstance(lead.get("labels"), list) else [],
        })

    prompt = {
        "task": (
            "The owner is building PASSIVE income from a digital product (for example a "
            "browser extension or a small utility) on a zero budget, and wants to be paid "
            "in crypto. Suggest how to sell and distribute such a product so that it earns "
            "without the owner working per sale."
        ),
        "hard_rules": [
            "PASSIVE INCOME ONLY. Never suggest freelancing, contract work, consulting, "
            "agency work or retainers: income per hour of the owner's time is a job.",
            "Every service or platform must be one you are confident exists right now. "
            "Sellix was seized in 2024 and is still widely recommended, so a dead platform "
            "is a real failure mode here.",
            "Prefer platforms that are free to list on and settle stablecoin (USDT/USDC) "
            "directly to the seller's own wallet address, with no custodian and no KYC.",
            "State every cost and every manual setup step out loud. Zero budget is the "
            "binding constraint, so a monthly fee usually disqualifies a platform.",
            "If unsure about a fee, limit or payout rule, write 'verify current terms' "
            "instead of inventing a number.",
            "Never estimate revenue or promise an amount. Real revenue is the on-chain "
            "balance only.",
            "Stay inside policy: no social posting, no cold outreach, no trading, no "
            "minting, no yield farming or staking.",
        ],
        "policy": "Research and suggestions only. Do not contact anyone, request payment, trade, or mint.",
        "product_shapes": _clean_list(cfg.get("product_shapes", [])),
        "monetization_patterns": _clean_list(cfg.get("monetization_patterns", [])),
        "avoid": _clean_list(cfg.get("avoid_patterns", [])),
        "already_running": (
            "A validated Tron (TRC-20) receive address is already appended to every "
            "article this project publishes to dev.to, and the same address can go on a "
            "product page and in a README at no cost. Prefer suggestions that reuse it."
        ),
        "lead_samples": samples,
        "required_json_shape": {
            "summary": "one concise paragraph on the best current route to passive product income on zero budget",
            "market_themes": [
                {
                    "theme": "a pattern in how products like this actually get paid",
                    "evidence": "which lead titles or platforms show it",
                    "offer": "what the owner should sell, and on which channel",
                }
            ],
            "sales_channels": [
                {
                    "name": "platform or channel name",
                    "what_it_does": "what it lists or distributes, in one short phrase",
                    "cost": "listing/monthly fee and revenue cut, or 'verify current terms'",
                    "crypto_payout": "which stablecoins and networks, to own wallet or custodial, or 'verify'",
                    "owner_setup": "what the owner must do by hand, once",
                    "why_passive": "why income from it needs no owner action per sale",
                }
            ],
            "product_ideas": [
                {
                    "idea": "short name for the product",
                    "who_buys": "the specific user who would pay",
                    "deliverable": "exactly what the buyer downloads or unlocks",
                    "pricing_model": "free tier plus paid upgrade, one-time licence, pay-what-you-want",
                    "marginal_cost": "what each additional user costs the owner to serve",
                    "free_stack": "the zero-cost stack it runs on",
                }
            ],
            "owner_actions": ["3-5 concrete next actions, most valuable first"],
        },
    }
    try:
        if hasattr(llm, "complete_json_for_role"):
            data = llm.complete_json_for_role("research", json.dumps(prompt), max_tokens=3000)
        else:
            data = llm.complete_json(json.dumps(prompt), max_tokens=3000)
    except Exception as exc:
        log.warning("[code_techs] online AI brief failed: %s", exc)
        return {
            "summary": f"Channel brief failed; used the verified channel table and local scoring only. Error: {str(exc)[:160]}",
            "sales_channels": [],
            "product_ideas": [],
            "owner_actions": [
                "Work the verified channel rows below: they are checked by hand and need no LLM.",
                "Verify each platform's current fees and payout terms yourself before listing.",
            ],
        }

    return {
        "summary": str(data.get("summary", "")).strip()[:900],
        "market_themes": _dicts(data.get("market_themes"), ["theme", "evidence", "offer"], limit=5),
        "sales_channels": _dicts(data.get("sales_channels"), [
            "name", "what_it_does", "cost", "crypto_payout",
            "owner_setup", "why_passive",
        ], limit=10),
        "product_ideas": _dicts(data.get("product_ideas"), [
            "idea", "who_buys", "deliverable", "pricing_model",
            "marginal_cost", "free_stack",
        ], limit=8),
        "owner_actions": _clean_list(data.get("owner_actions", []))[:5],
    }


def _dicts(value: Any, fields: list[str], limit: int) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        row = {f: str(item.get(f, "")).strip()[:300] for f in fields}
        if not any(row.values()):
            continue
        out.append(row)
        if len(out) >= limit:
            break
    return out

def _score(
    lead: dict[str, Any],
    text: str,
    labels: list[str],
    kind: str,
    age_hours: float | None,
    value_basis: str,
    cfg: dict[str, Any],
) -> tuple[int, dict[str, float]]:
    labels_set = {str(l).lower() for l in labels}

    sells_hours = any(
        t in text for t in
        ("per client", "per project", "hourly", "/hr", "per hour", "retainer",
         "consult", "freelance", "contractor")
    )
    if sells_hours and "no-owner-action" not in labels_set:
        owner_action = 0.1
    elif "already-live" in labels_set or "no-owner-action" in labels_set:
        owner_action = 1.0
    elif kind == _CHANNEL:
        owner_action = 0.85
    elif any(t in labels_set for t in ("reuse", "one-time-setup", "already-running")):
        owner_action = 0.7
    elif any(t in text for t in ("subscription", "recurring", "licence", "license", "royalt")):
        owner_action = 0.6
    else:
        owner_action = 0.4

    crypto_terms = ("usdt", "usdc", "trc-20", "trc20", "tron", "stablecoin", "crypto", "wallet")
    if "own-wallet" in labels_set or "wallet" in labels_set:
        receive_path = 1.0
    elif any(t in text for t in crypto_terms):
        receive_path = 0.8
    elif kind == _CHANNEL:
        receive_path = 0.5
    else:
        receive_path = 0.2

    cost = _cost(lead.get("cost_usd"))
    if cost is None:
        zero_budget = 0.5 if kind == _CHANNEL else 0.6
    elif cost <= 0:
        zero_budget = 1.0
    elif cost <= 10:
        zero_budget = 0.7
    elif cost <= 50:
        zero_budget = 0.3
    else:
        zero_budget = 0.0
    if _charges_a_subscription(text):
        zero_budget = min(zero_budget, 0.2)

    setup = str(lead.get("manual_setup") or "").strip().lower()
    if not setup or setup.startswith("none"):
        setup_burden = 1.0
    elif "kyc" in setup or "approval" in setup or "review" in setup:
        setup_burden = 0.3
    else:
        setup_burden = 0.6

    if lead.get("source") == "channel-table":
        recency = 1.0
    elif kind == _ASSET:
        max_age = max(1.0, float(cfg.get("supply_max_age_days", 120) or 120) * 24)
        recency = 0.3 if age_hours is None else max(0.0, 1.0 - (max(0.0, age_hours) / max_age))
    else:
        recency = 0.3 if age_hours is None else max(0.0, 1.0 - (max(0.0, age_hours) / 720.0))

    parts = {
        "owner_action": round(owner_action, 3),
        "receive_path": round(receive_path, 3),
        "zero_budget": round(zero_budget, 3),
        "setup_burden": round(setup_burden, 3),
        "recency": round(recency, 3),
    }
    score = (
        32 * parts["owner_action"]
        + 25 * parts["receive_path"]
        + 18 * parts["zero_budget"]
        + 15 * parts["setup_burden"]
        + 10 * parts["recency"]
    )

    penalty = 0
    if any(word in text for word in ("hiring", "apply now", "job description", "full-time", "salary")):
        penalty += 20
    if any(word in text for word in ("bounty", "prize", "contest")):
        penalty += 15
    if any(word in text for word in ("credit card required", "trial expires", "upgrade to unlock")):
        penalty += 10
    if any(word in text for word in ("get rich", "guaranteed income", "6-figure", "double your money")):
        penalty += 20
    if any(word in text for word in ("yield farm", "staking rewards", "airdrop", "nft mint", "presale")):
        penalty += 25
    if any(word in text for word in ("need an audience", "followers", "ad spend", "go viral")):
        penalty += 10
    if penalty:
        parts["penalty"] = float(-penalty)

    return max(0, min(100, round(score - penalty))), parts

def _charges_a_subscription(text: str) -> bool:
    terms = ("monthly fee", "per month subscription", "subscription required",
             "paid plan required", "monthly subscription", "billed monthly")
    negators = ("no ", "not ", "never ", "without ", "zero ", "free of ", "0 ")
    for term in terms:
        start = 0
        while True:
            at = text.find(term, start)
            if at < 0:
                break
            before = text[max(0, at - 14):at]
            if not any(before.rstrip().endswith(n.strip()) for n in negators):
                return True
            start = at + len(term)
    return False

def _is_free_ai_lead(text: str) -> bool:
    free_terms = (
        "free", "no credit card", "no-cost", "zero cost", "open source",
        "open-weight", "free tier", "free api", "generous",
    )
    for match in _AI_TERM_RE.finditer(text):
        lo = max(0, match.start() - _FREE_WINDOW)
        window = text[lo:match.end() + _FREE_WINDOW]
        if any(term in window for term in free_terms):
            return True
    return False

def _lead_value(lead: dict[str, Any]) -> tuple[float | None, str, str]:
    low = _money(lead.get("min_salary"))
    high = _money(lead.get("max_salary"))
    if low or high:
        currency = str(lead.get("currency") or "").upper()
        if currency in ("", "USD"):
            amount = low or high
            period = str(lead.get("salary_period") or "").lower()
            suffix = _PERIOD_LABELS.get(period, "")
            if low and high and high != low:
                note = f"${low:,.0f}-{high:,.0f}{suffix} posted"
            else:
                note = f"${amount:,.0f}{suffix} posted"
            return amount, "posted_salary", note

    if lead.get("allow_rate_extraction"):
        match = _RATE_RE.search(str(lead.get("body") or ""))
        if match:
            first = _money(match.group(1))
            second = _money(match.group(2))
            if first:
                note = f"${first:,.0f}-{second:,.0f}/hr stated" if second else f"${first:,.0f}/hr stated"
                return first, "stated_rate", note

    return None, "none", ""

def _money(value: Any) -> float | None:
    try:
        amount = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None
    return amount if amount > 0 else None

def _cost(value: Any) -> float | None:
    if value is None:
        return None
    try:
        amount = float(str(value).replace(",", "").replace("$", "").strip())
    except (TypeError, ValueError):
        return None
    return amount if amount >= 0 else None

def _reason(
    lead: dict[str, Any],
    text: str,
    labels: list[str],
    kind: str,
    value_note: str,
    age_hours: float | None,
) -> str:
    labels_set = {str(l).lower() for l in labels}
    parts: list[str] = []

    if "already-live" in labels_set:
        parts.append("already running, so it needs no account and no owner action")
    if "own-wallet" in labels_set:
        parts.append("settles to the wallet address this project already publishes")
    elif any(t in text for t in ("usdt", "usdc", "tron", "trc-20", "stablecoin")):
        parts.append("pays in stablecoin, so the receive path is on-chain and verifiable")
    if kind == _CHANNEL and "already-live" not in labels_set:
        parts.append("sells the product while nobody is working; the signup is one-time")
    if "free-to-publish" in labels_set or "no-approval" in labels_set:
        parts.append("free to list with no approval queue, so a refusal cannot block it")
    cost = _cost(lead.get("cost_usd"))
    if cost is not None and cost > 0:
        parts.append(f"costs ${cost:,.2f} once, stated rather than hidden")
    if kind == _ASSET:
        parts.append("free tooling or reach to build and market the product with")
    if any(t in text for t in ("hourly", "/hr", "per client", "retainer")):
        parts.append("priced per hour of the owner's time, which is a job and not passive income")

    if not parts:
        parts.append("zero-budget route to listing or promoting a digital product")
    return "; ".join(parts[:2])

def _next_step(lead: dict[str, Any], kind: str, cfg: dict[str, Any]) -> str:
    subject = " ".join([
        str(lead.get("title") or ""),
        " ".join(str(x) for x in lead.get("labels") or []),
    ]).lower()
    setup = str(lead.get("manual_setup") or "").strip()

    if kind == _CHANNEL:
        if "already-live" in subject or (setup.lower().startswith("none")):
            return (
                "Put the same published receive address on the product page and in the "
                "README, then confirm a reader can see it -- receipt_check already proves "
                "this for the articles."
            )
        first = (
            "List the product once, set the price, and point the payout at the "
            "published Tron address"
            if any(t in subject for t in ("usdt", "tron", "own-wallet"))
            else "List the product once and set the price"
        )
        return f"{first}. Owner does this by hand: {setup or 'open the account'}"

    if any(t in subject for t in ("devto", "reach", "content-marketing")):
        return (
            "Write the problem-shaped article this product answers and let the existing "
            "footer carry the ask -- no new channel, and the publishing path already runs."
        )
    if any(t in subject for t in ("free-stack", "zero-budget", "no-server")):
        return (
            "Confirm the free tier's real limits and terms, then keep the product's "
            "per-user cost at zero so the free tier can stay free indefinitely."
        )
    if any(t in subject for t in ("open-source", "discovery", "sponsors")):
        return (
            "Publish the repository with the receive address in the README, so discovery "
            "and the ask live in the same artifact."
        )
    return (
        "Check the free tier's real limits, then use it to build or promote the product "
        "without adding a per-user cost."
    )

def _codex_prompt(op: Opportunity, cfg: dict[str, Any]) -> str:
    free_stack = _clean_list(cfg.get("free_ai_focus", []))[:2]
    cost = _cost(getattr(op, "cost_usd", None))
    if cost is None:
        cost_line = "not published - do not quote or invent a figure"
    elif cost <= 0:
        cost_line = "$0.00 (free to list)"
    else:
        cost_line = f"${cost:,.2f} one-time, published by the platform"
    why = " ".join(str(op.reason or "").split())
    paid = "where it gets paid" if op.kind == _CHANNEL else "what builds or promotes it"
    stack = "; ".join(free_stack) or "any zero-cost tier"
    return (
        "Move a digital product one step closer to earning without owner involvement.\n\n"
        f"KIND           {op.kind} ({paid})\n"
        f"LEAD           {op.title}\n"
        f"SOURCE         {op.source}\n"
        f"LINK           {op.url or 'no public URL'}\n"
        f"COST           {cost_line}\n"
        f"OWNER MUST DO  {getattr(op, 'manual_setup', '') or 'nothing'}\n"
        f"NEXT STEP      {op.next_step}\n"
        f"FREE STACK     {stack}\n"
        f"WHY IT RANKS   {why}\n\n"
        "Constraints:\n"
        "- Keep the first change narrowly scoped to one file or script.\n"
        "- Use free tiers or offline code paths only; no paid service.\n"
        "- Include the exact commands to run it and paste the real output.\n"
        "- Do not contact anyone, post to social media, trade, or mint anything.\n"
        "- Do not open an account or accept terms on the owner's behalf.\n"
        "- Do not state a price or an earnings figure that COST does not give.\n"
        "- Revenue is the on-chain balance only; never estimate it."
    )

def _write_report(state: dict[str, Any], leads: list[dict[str, Any]] | None = None) -> None:
    _REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Passive Product Income Queue",
        "",
        f"Refreshed: {state.get('last_refresh_at')}",
        "",
        "Routes to passive income from a digital product on a zero budget: where it can",
        "be listed and paid for (channels) and what can build or market it (assets).",
        "",
        "**Freelance and contract postings are deliberately absent.** Income per hour of",
        "the owner's time is a job, not passive income, so those sources were removed",
        "rather than demoted.",
        "",
        "No revenue figure appears on this page. Real revenue is the on-chain wallet",
        "balance, and a listing is not a receipt.",
        "",
        "## Requirements",
        "",
    ]
    for item in state.get("requirements", []):
        lines.append(f"- {item}")

    brief = state.get("online_ai_brief") or {}
    summary = str(brief.get("summary", "")).strip()
    if summary:
        lines.extend(["", "## Current Best Angle", "", summary])

    services = brief.get("sales_channels") or []
    if services:
        lines.extend([
            "", "## Sales Channels", "",
            "| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |",
            "| --- | --- | --- | --- | --- | --- |"]
        )
        for svc in services:
            lines.append(
                "| {} | {} | {} | {} | {} | {} |".format(
                    _cell(svc.get("name")), _cell(svc.get("what_it_does")),
                    _cell(svc.get("cost")), _cell(svc.get("crypto_payout")),
                    _cell(svc.get("owner_setup")), _cell(svc.get("why_passive")),
                )
            )

    ideas = brief.get("product_ideas") or []
    if ideas:
        lines.extend(["", "## Product Ideas", ""])
        for index, idea in enumerate(ideas, start=1):
            lines.extend([
                f"{index}. **{idea.get('idea', 'untitled')}**",
                f"   - Who buys: {idea.get('who_buys', '')}",
                f"   - Deliverable: {idea.get('deliverable', '')}",
                f"   - Pricing model: {idea.get('pricing_model', '')}",
                f"   - Cost per extra user: {idea.get('marginal_cost', '')}",
                f"   - Free stack: {idea.get('free_stack', '')}",
            ])

    if brief.get("owner_actions"):
        lines.extend(["", "## Next Actions", ""])
        for action in brief["owner_actions"]:
            lines.append(f"- {action}")

    if state.get("monetization_patterns"):
        lines.extend(["", "## Monetization Patterns", ""])
        for item in state["monetization_patterns"]:
            lines.append(f"- {item}")

    if state.get("free_ai_focus"):
        lines.extend(["", "## Free AI Focus Areas", ""])
        for item in state["free_ai_focus"]:
            lines.append(f"- {item}")

    lines.extend(["", "## Reference Sources", ""])
    for item in state.get("reference_sources", []):
        title = item.get("title", "untitled")
        url = item.get("url", "")
        takeaway = item.get("takeaway", "")
        prefix = f"- [{title}]({url})" if url else f"- {title}"
        lines.append(f"{prefix}: {takeaway}" if takeaway else prefix)
    lines.extend(["", "## Underserved Niches", ""])
    for item in state.get("focus", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Strategy Playbook", ""])
    for item in state.get("strategy_playbook", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Avoid", ""])
    for item in state.get("avoid_patterns", []):
        lines.append(f"- {item}")
    refused = state.get("refused_channels") or []
    if refused:
        lines.extend([
            "", "## Refused Channels", "",
            "Written down so a later cycle does not re-derive them, and so a dead",
            "platform cannot climb back onto this page.",
            "",
        ])
        for item in refused:
            lines.append(f"- **{item.get('name', 'unnamed')}:** {item.get('why', '')}")

    lines.extend(["", "## Ranked Leads", ""])
    for index, op in enumerate(leads if leads is not None else state.get("opportunities", []), start=1):
        title = op.get("title", "untitled")
        url = op.get("url", "")
        pursued_tag = " [PURSUED]" if op.get("pursued") else ""
        heading = f"{index}. [{title}]({url}){pursued_tag}" if url else f"{index}. {title}{pursued_tag}"
        age = op.get("age_hours")
        cost = op.get("cost_usd")
        if isinstance(cost, (int, float)):
            cost_text = "free to list" if cost <= 0 else f"${cost:,.2f} one-time"
        else:
            cost_text = "not published"
        lines.extend([
            heading,
            f"   - Kind: {op.get('kind', 'unknown')}",
            f"   - Score: {op.get('score', 0)}/100",
            f"   - Cost: {cost_text}",
            f"   - Owner must do: {op.get('manual_setup') or 'nothing'}",
            f"   - Why: {op.get('reason', '')}",
            f"   - Next: {op.get('next_step', '')}",
        ])
        if op.get("verified_note"):
            lines.append(f"   - Verified: {op.get('verified_note')}")
        if op.get("posted_at"):
            lines.append(
                f"   - Posted: {op.get('posted_at')}"
                + (f" ({age:.0f}h ago)" if isinstance(age, (int, float)) else "")
            )
        if op.get("codex_prompt"):
            lines.extend([
                "   - Codex request:",
                _indent_block(str(op.get("codex_prompt", "")), "     "),
            ])
    _REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

def _indent_block(text: str, prefix: str) -> str:
    cleaned = text.strip() or "(none)"
    return "\n".join(f"{prefix}{line}" for line in cleaned.splitlines())

def _cell(value: Any) -> str:
    text = str(value or "").replace("|", "\\|")
    return re.sub(r"\s+", " ", text).strip() or "-"