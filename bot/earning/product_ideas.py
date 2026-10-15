"""
Earning Module — Product Ideas Generator

Generates concrete, buildable digital product ideas using free AI APIs,
leveraging the existing wallet address and article audience to create
zero-marginal-cost products that can be sold on free channels (Getly,
GitHub Releases, wallet ask).

Activates with: any free-tier LLM key (Atria, Gemini, Groq, OpenRouter).
No new secrets required.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ._shared import load_config

log = logging.getLogger(__name__)

_REPORT_FILE = Path("docs/product-ideas.md")

_DEFAULTS = {
    "enabled": True,
    "refresh_hours": 24,
    "max_ideas": 8,
    "min_score": 50,
    "history_limit": 50,
    "product_shapes": [
        "browser extension solving one specific annoyance",
        "single-purpose desktop or CLI utility",
        "static web tool that runs entirely client-side",
        "template, preset, or asset pack for a tool people already use",
        "developer library or plugin for an existing ecosystem",
        "self-hostable script the buyer runs on their own machine",
        "data set or reference compiled once and sold as a download"
    ],
    "monetization_patterns": [
        "Ship the tool free and sell the upgrade: the free tier buys discovery the owner cannot.",
        "One-time licence for a digital download, delivered by the storefront with no owner action.",
        "Put the published receive address on the product page and in the README, so a user can pay with no platform at all.",
        "Sell a template, preset, or asset pack built once and downloaded many times.",
        "Charge for the paid tier of a tool whose free tier costs nothing per user to run.",
        "List the same product on every zero-cost channel, since the artifact is already built."
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
    ]
}

_SYSTEM_PROMPT = """You are a product strategist for a solo developer building passive income.

Constraints:
- Zero budget: no paid services, no credit cards, no monthly fees.
- No server: GitHub Actions only (outbound, hourly, no inbound HTTP).
- No payment processing: cannot charge cards or bill subscriptions.
- No outreach: cold email, DMs, social posting are blocked in code.
- Can research, analyse, draft, and publish articles to dev.to.
- Payment must settle to the owner's Tron (TRC-20) wallet: TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
- Product must earn without owner action per sale (passive).

Output ONLY a JSON array of product ideas. Each idea:
{
  "name": "short product name",
  "shape": "one of the product_shapes",
  "who_buys": "specific user persona with budget",
  "deliverable": "exactly what the buyer downloads or unlocks",
  "pricing_model": "free tier + paid upgrade OR one-time licence OR pay-what-you-want",
  "marginal_cost": "what each additional user costs (must be ~$0)",
  "free_stack": "the zero-cost stack it runs on",
  "channel": "where it gets listed (Getly, GitHub Releases, wallet ask, Chrome Web Store)",
  "owner_setup": "what the owner must do by hand, once",
  "codex_prompt": "a prompt for the coding agent to build the MVP in one file"
}

Prioritise:
1. Browser extensions (Chrome Web Store = real discovery, $5 one-time, 20 extensions)
2. Client-side tools (zero server cost, zero marginal cost)
3. Templates/asset packs (built once, sold many times)
4. CLI utilities (distributed via GitHub Releases, wallet ask in --help)

Reject:
- Anything needing a server, database, or inbound HTTP
- Anything needing payment processing or subscriptions
- Anything needing cold outreach or social posting
- Consulting, freelancing, retainers (selling hours = job, not passive)"""


def _config() -> dict[str, Any]:
    return load_config("product_ideas", _DEFAULTS)


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    cfg = _config()
    state = status.setdefault("product_ideas", {})
    
    if not cfg.get("enabled", True):
        state["enabled"] = False
        return []
    state["enabled"] = True

    forced = bool(status.get("_overrides", {}).get("force_product_ideas"))
    if not forced:
        from ._shared import hours_until_due
        waiting = hours_until_due(state, "last_refresh_at", int(cfg["refresh_hours"]))
        if waiting > 0:
            log.info("[product_ideas] next refresh due in %.1fh — skipping", waiting)
            return []
    else:
        log.info("[product_ideas] interval bypassed by 'force product_ideas' command")

    if llm is None:
        log.warning("[product_ideas] no LLM available — skipping")
        return []

    # Pull context from code_techs and mrr_ideas for grounded suggestions
    code_techs_state = status.get("code_tech_earning", {})
    mrr_state = status.get("mrr_ideas", {})
    
    prompt = {
        "task": "Generate 5-8 concrete digital product ideas fitting the constraints.",
        "context": {
            "wallet_address": "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY (TRC-20 USDT/USDC/USDD)",
            "existing_articles": len(status.get("article_history", {}).get("own_urls", [])),
            "top_article_archetype": status.get("article_interest", {}).get("best_archetype", "problem-workaround"),
            "verified_channels": [c["title"] for c in code_techs_state.get("opportunities", []) if c.get("kind") == "channel"][:5],
            "viable_mrr": [v["name"] for v in mrr_state.get("viable", [])],
            "product_shapes": cfg["product_shapes"],
            "monetization_patterns": cfg["monetization_patterns"],
            "free_ai_focus": cfg["free_ai_focus"]
        },
        "required_json_shape": [
            {
                "name": "FocusFlow",
                "shape": "browser extension solving one specific annoyance",
                "who_buys": "Remote workers and students who lose hours to distracting sites",
                "deliverable": "Chrome extension (MV3) that blocks a custom site list when a focus timer starts; free tier blocks 10 default sites, $5 licence unlocks custom schedules, per-site limits, and usage analytics",
                "pricing_model": "Free base (10 sites, manual timer); $5 one-time licence for schedules, custom lists, analytics",
                "marginal_cost": "$0 — client-side only, no server, no per-user cost",
                "free_stack": "Chrome MV3 extension, GitHub Releases for distribution, Getly for payments",
                "channel": "Getly (USDT to own wallet) + Chrome Web Store (discovery) + wallet ask in README",
                "owner_setup": "1) Create Getly account, add Tron address. 2) Pay $5 Chrome Web Store registration. 3) Upload extension to both.",
                "codex_prompt": "Build a Manifest V3 Chrome extension called FocusFlow. Features: popup with start/stop focus timer, default blocklist (twitter.com, reddit.com, youtube.com, facebook.com, instagram.com, tiktok.com, linkedin.com, news.ycombinator.com, github.com/notifications, dev.to/notifications), custom blocklist storage in chrome.storage.sync, per-site time limits, focus session logging to local JSON. No external APIs. Single background.js, popup.html, manifest.json. Output as a zip-ready folder structure."
            }
        ]
    }

    try:
        if hasattr(llm, "complete_json_for_role"):
            ideas = llm.complete_json_for_role("research", json.dumps(prompt), system=_SYSTEM_PROMPT, max_tokens=4000)
        else:
            ideas = llm.complete_json(json.dumps(prompt), system=_SYSTEM_PROMPT, max_tokens=4000)
    except Exception as exc:
        log.warning("[product_ideas] LLM call failed: %s", exc)
        return []

    if not isinstance(ideas, list):
        log.warning("[product_ideas] invalid response shape: %s", type(ideas).__name__)
        return []

    # Score and filter
    scored = []
    for idea in ideas[:cfg["max_ideas"]]:
        if not isinstance(idea, dict) or not idea.get("name"):
            continue
        score = _score_idea(idea, cfg)
        if score >= cfg["min_score"]:
            idea["score"] = score
            scored.append(idea)

    scored.sort(key=lambda x: x["score"], reverse=True)
    
    now = datetime.now(timezone.utc)
    state.update({
        "last_refresh_at": now.isoformat(),
        "refresh_hours": int(cfg["refresh_hours"]),
        "ideas": scored[:cfg["max_ideas"]],
        "product_shapes": cfg["product_shapes"],
        "monetization_patterns": cfg["monetization_patterns"],
        "free_ai_focus": cfg["free_ai_focus"]
    })
    
    _write_report(state, scored)
    
    log.info("[product_ideas] generated %d ideas", len(scored))
    return [{
        "platform": "product_ideas",
        "success": True,
        "idea_count": len(scored),
        "estimated_usd": 0.0,
        "title": f"Product ideas refreshed ({len(scored)} viable)",
        "url": str(_REPORT_FILE)
    }]


def _score_idea(idea: dict, cfg: dict) -> int:
    """Score 0-100: how well does this fit passive, zero-budget, crypto-settled?"""
    score = 50
    text = json.dumps(idea).lower()
    
    # Channel quality
    channel = str(idea.get("channel", "")).lower()
    if "getly" in channel:
        score += 20  # verified no-KYC, USDT to own wallet
    if "chrome web store" in channel or "chrome store" in channel:
        score += 15  # real discovery, $5 one-time
    if "wallet ask" in channel or "github releases" in channel:
        score += 10  # zero cost, already works
    
    # Marginal cost
    if "$0" in str(idea.get("marginal_cost", "")) or "zero" in str(idea.get("marginal_cost", "")).lower():
        score += 15
    
    # Owner setup burden (lower is better)
    setup = str(idea.get("owner_setup", "")).lower()
    if "$5" in setup and "chrome" in setup:
        score += 5  # acceptable one-time cost
    elif "kyc" in setup or "id verification" in setup:
        score -= 20
    
    # Shape alignment
    shape = str(idea.get("shape", "")).lower()
    if "browser extension" in shape:
        score += 10
    elif "client-side" in shape or "static web tool" in shape:
        score += 8
    elif "template" in shape or "asset pack" in shape:
        score += 5
    
    # Pricing model
    pricing = str(idea.get("pricing_model", "")).lower()
    if "one-time" in pricing or "licence" in pricing or "license" in pricing:
        score += 5
    if "free tier" in pricing or "freemium" in pricing:
        score += 5
    
    return max(0, min(100, score))


def _write_report(state: dict[str, Any], ideas: list[dict]) -> None:
    _REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Product Ideas for Passive Income",
        "",
        f"Refreshed: {state.get('last_refresh_at')}",
        "",
        "Zero-budget digital products that can earn USDT/USDC on Tron to the published wallet",
        "(TFTNsfyomKrnUutRjBTGVULp19ByW29KbY) without owner action per sale.",
        "",
        "## Ideas",
        ""
    ]
    for i, idea in enumerate(ideas, 1):
        lines.extend([
            f"### {i}. {idea.get('name', 'Unnamed')} (score: {idea.get('score', 0)}/100)",
            f"- **Shape:** {idea.get('shape', '')}",
            f"- **Who buys:** {idea.get('who_buys', '')}",
            f"- **Deliverable:** {idea.get('deliverable', '')}",
            f"- **Pricing:** {idea.get('pricing_model', '')}",
            f"- **Marginal cost:** {idea.get('marginal_cost', '')}",
            f"- **Free stack:** {idea.get('free_stack', '')}",
            f"- **Channel:** {idea.get('channel', '')}",
            f"- **Owner setup (once):** {idea.get('owner_setup', '')}",
            "",
            "**Codex prompt to build MVP:**",
            "```",
            idea.get('codex_prompt', ''),
            "```",
            ""
        ])
    
    lines.extend([
        "## Product Shapes",
        ""
    ])
    for shape in state.get("product_shapes", []):
        lines.append(f"- {shape}")
    
    lines.extend(["", "## Monetization Patterns", ""])
    for pattern in state.get("monetization_patterns", []):
        lines.append(f"- {pattern}")
    
    lines.extend(["", "## Free AI Focus Areas", ""])
    for focus in state.get("free_ai_focus", []):
        lines.append(f"- {focus}")
    
    _REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    # Manual test: python -m bot.earning.product_ideas
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    class MockLLM:
        def complete_json(self, prompt, system, max_tokens):
            return [{
                "name": "FocusFlow",
                "shape": "browser extension solving one specific annoyance",
                "who_buys": "Remote workers and students who lose hours to distracting sites",
                "deliverable": "Chrome extension (MV3) that blocks a custom site list when a focus timer starts; free tier blocks 10 default sites, $5 licence unlocks custom schedules, per-site limits, and usage analytics",
                "pricing_model": "Free base (10 sites, manual timer); $5 one-time licence for schedules, custom lists, analytics",
                "marginal_cost": "$0 — client-side only, no server, no per-user cost",
                "free_stack": "Chrome MV3 extension, GitHub Releases for distribution, Getly for payments",
                "channel": "Getly (USDT to own wallet) + Chrome Web Store (discovery) + wallet ask in README",
                "owner_setup": "1) Create Getly account, add Tron address. 2) Pay $5 Chrome Web Store registration. 3) Upload extension to both.",
                "codex_prompt": "Build a Manifest V3 Chrome extension called FocusFlow. Features: popup with start/stop focus timer, default blocklist (twitter.com, reddit.com, youtube.com, facebook.com, instagram.com, tiktok.com, linkedin.com, news.ycombinator.com, github.com/notifications, dev.to/notifications), custom blocklist storage in chrome.storage.sync, per-site time limits, focus session logging to local JSON. No external APIs. Single background.js, popup.html, manifest.json. Output as a zip-ready folder structure."
            }]
    run(MockLLM(), {})