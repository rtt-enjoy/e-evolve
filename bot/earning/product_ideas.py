"""
Earning Module — Product Ideas Generation

Generates concrete product ideas for passive income using free AI APIs.
Leverages the existing wallet address and free-tier services to create
opportunities that earn without owner involvement per sale.

Activates with: DEV_TO_API_KEY (for publishing follow-up articles)
No new secrets required.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ._shared import load_config, bounded_append
from . import devto, devto_stats

log = logging.getLogger(__name__)

_REPORT_FILE = Path("docs/product-ideas.md")

_DEFAULTS = {
    "enabled": True,
    "refresh_hours": 24,
    "max_ideas": 5,
    "min_score": 60,
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
    ],
    "channels": [
        {
            "name": "Getly",
            "url": "https://www.getly.store/sell/crypto",
            "crypto_payout": "USDT/USDC on Tron (TRC-20), paid directly to your own wallet address",
            "cost": "No monthly fee; free to list and sell",
            "owner_setup": "Create a free Getly account, connect your Tron wallet, and list your product with the validated receive address",
            "why_passive": "Once listed, no owner action is required per sale; buyers pay directly to your wallet"
        },
        {
            "name": "GitHub Releases",
            "url": "https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository",
            "crypto_payout": "USDT/USDC paid directly to your wallet",
            "cost": "Zero cost; no listing fee, no identity verification",
            "owner_setup": "Upload the product file to a GitHub repository, add the validated Tron receive address to the README and release notes",
            "why_passive": "Files are downloaded instantly; no ongoing maintenance or per-sale processing"
        },
        {
            "name": "Wallet Ask on Product Page",
            "url": "",
            "crypto_payout": "USDT/USDC sent to your wallet",
            "cost": "Zero cost; no platform fee",
            "owner_setup": "Add a clear payment link in the README, tool help text, and footer",
            "why_passive": "Users who never visit a storefront can still pay directly from the product page"
        }
    ]
}


def _config() -> dict[str, Any]:
    return load_config("product_ideas", _DEFAULTS)


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Main entry point for the product ideas earning module."""
    cfg = _config()
    state = status.setdefault("product_ideas", {})
    
    if not cfg.get("enabled", True):
        state["enabled"] = False
        return []
    state["enabled"] = True

    # Check cadence
    from ._shared import hours_until_due
    waiting = hours_until_due(state, "last_refresh_at", int(cfg.get("refresh_hours", 24)))
    if waiting > 0:
        log.info("[product_ideas] next refresh due in %.1fh — skipping", waiting)
        return []

    if llm is None:
        log.warning("[product_ideas] no LLM available — skipping")
        return []

    # Generate product ideas using LLM
    ideas = _generate_ideas(llm, status, cfg)
    if not ideas:
        log.warning("[product_ideas] no ideas generated")
        return []

    # Score and filter ideas
    scored_ideas = _score_ideas(ideas, cfg, status)
    top_ideas = scored_ideas[:int(cfg.get("max_ideas", 5))]

    # Update state
    now = datetime.now(timezone.utc)
    state.update({
        "last_refresh_at": now.isoformat(),
        "refresh_hours": int(cfg.get("refresh_hours", 24)),
        "ideas": top_ideas,
        "total_generated": len(ideas),
        "channels": cfg.get("channels", []),
        "product_shapes": cfg.get("product_shapes", []),
        "monetization_patterns": cfg.get("monetization_patterns", []),
        "free_ai_focus": cfg.get("free_ai_focus", []),
    })
    
    # Write report
    _write_report(state, top_ideas)

    log.info("[product_ideas] generated %d ideas, kept %d", len(ideas), len(top_ideas))
    return [{
        "platform": "product_ideas",
        "success": True,
        "idea_count": len(top_ideas),
        "estimated_usd": 0.0,
        "title": f"Product ideas refreshed ({len(top_ideas)} ideas)",
        "url": str(_REPORT_FILE)
    }]


def _generate_ideas(llm: Any, status: dict, cfg: dict) -> list[dict]:
    """Generate product ideas using the research LLM."""
    # Get article interest data for context
    interest = status.get("article_interest", {})
    best_archetype = interest.get("best_archetype", "problem-workaround")
    winning_tags = status.get("article_stats", {}).get("winning_tags", ["python", "ai", "automation"])
    wallet = status.get("payout_public", {}).get("address", "")
    
    prompt = {
        "task": (
            "Generate 10 concrete product ideas for a solo developer to build and sell "
            "as digital products with passive income on a zero budget. Each idea must:"
            "- Be buildable with free-tier AI APIs (no credit card required)"
            "- Have zero marginal cost per user"
            "- Settle payments in USDT/USDC on Tron (TRC-20) to the owner's wallet"
            "- Require no owner action per sale (truly passive)"
            "- Target developers or technical users (the existing audience)"
            "- Solve ONE specific annoyance well"
        ),
        "context": {
            "best_performing_archetype": best_archetype,
            "winning_tags": winning_tags[:6],
            "wallet_address": wallet,
            "existing_channels": [c["name"] for c in cfg.get("channels", [])],
            "product_shapes": cfg.get("product_shapes", []),
            "monetization_patterns": cfg.get("monetization_patterns", []),
            "free_ai_focus": cfg.get("free_ai_focus", [])
        },
        "hard_rules": [
            "Never suggest freelancing, consulting, or selling hours."
            "Every idea must name a specific buyer, deliverable, and price."
            "Prefer one-time license over subscription (simpler, no recurring billing)."
            "State the exact free-tier services the product would use."
            "If a platform fee exists, state it; if unknown, write 'verify current terms'."
            "Revenue is on-chain balance only; never estimate earnings."
        ],
        "required_json_shape": {
            "ideas": [
                {
                    "name": "short product name",
                    "who_buys": "specific user persona who would pay",
                    "deliverable": "exactly what the buyer downloads or unlocks",
                    "problem": "the specific annoyance this solves",
                    "pricing_model": "free tier + paid upgrade / one-time license / pay-what-you-want",
                    "price_usd": "e.g., $5 one-time or $10-20 one-time",
                    "free_stack": "which free-tier APIs/services it uses",
                    "channel": "which channel from context.existing_channels",
                    "build_effort": "low/medium/high - hours to build MVP",
                    "marginal_cost": "cost per additional user (should be ~$0)",
                    "why_this_audience": "why dev.to readers of this account would buy"
                }
            ]
        }
    }

    try:
        if hasattr(llm, "complete_json_for_role"):
            data = llm.complete_json_for_role("research", json.dumps(prompt), max_tokens=4000)
        else:
            data = llm.complete_json(json.dumps(prompt), max_tokens=4000)
    except Exception as exc:
        log.warning("[product_ideas] LLM generation failed: %s", exc)
        return []

    ideas = data.get("ideas", []) if isinstance(data, dict) else []
    valid_ideas = []
    for idea in ideas:
        if not isinstance(idea, dict):
            continue
        if not all(k in idea for k in ("name", "who_buys", "deliverable", "problem", "pricing_model", "price_usd", "free_stack", "channel")):
            continue
        valid_ideas.append(idea)
    return valid_ideas


def _score_ideas(ideas: list[dict], cfg: dict, status: dict) -> list[dict]:
    """Score ideas against passive income criteria."""
    scored = []
    for idea in ideas:
        score = 0
        parts = {}
        
        # Zero marginal cost (critical)
        marginal = str(idea.get("marginal_cost", "")).lower()
        if "$0" in marginal or "zero" in marginal or "near zero" in marginal or "free" in marginal:
            score += 30
            parts["marginal_cost"] = 1.0
        else:
            parts["marginal_cost"] = 0.0
        
        # Passive (no owner action per sale)
        pricing = str(idea.get("pricing_model", "")).lower()
        if "one-time" in pricing or "license" in pricing or "pay-what-you-want" in pricing:
            score += 25
            parts["passive"] = 1.0
        elif "subscription" in pricing:
            score += 10
            parts["passive"] = 0.5
        else:
            parts["passive"] = 0.0
        
        # Crypto payout to own wallet
        channel = str(idea.get("channel", "")).lower()
        if "getly" in channel or "github" in channel or "wallet" in channel or "direct" in channel:
            score += 20
            parts["crypto_payout"] = 1.0
        else:
            parts["crypto_payout"] = 0.3
        
        # Free-tier stack
        free_stack = str(idea.get("free_stack", "")).lower()
        free_terms = ["free", "no credit card", "open source", "open-weight", "free tier", "generous"]
        if any(term in free_stack for term in free_terms):
            score += 15
            parts["free_stack"] = 1.0
        else:
            parts["free_stack"] = 0.5
        
        # Build effort (lower is better)
        effort = str(idea.get("build_effort", "")).lower()
        if "low" in effort:
            score += 10
            parts["build_effort"] = 1.0
        elif "medium" in effort:
            score += 5
            parts["build_effort"] = 0.5
        else:
            parts["build_effort"] = 0.0
        
        # Audience fit
        why = str(idea.get("why_this_audience", "")).lower()
        if any(tag in why for tag in ["python", "ai", "automation", "devops", "developer", "tool"]):
            score += 10
            parts["audience_fit"] = 1.0
        else:
            parts["audience_fit"] = 0.5
        
        idea["score"] = score
        idea["score_parts"] = parts
        scored.append(idea)
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def _write_report(state: dict, ideas: list[dict]) -> None:
    """Write the markdown report."""
    _REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Product Ideas for Passive Income",
        "",
        f"Generated: {state.get('last_refresh_at')}",
        "",
        "Concrete product ideas for a solo developer to build once and sell passively",
        "using free-tier AI APIs and crypto payments direct to wallet.",
        "",
        "## Top Ideas",
        ""
    ]
    
    for i, idea in enumerate(ideas, 1):
        lines.extend([
            f"### {i}. {idea.get('name', 'Untitled')} (Score: {idea.get('score', 0)}/100)",
            "",
            f"**Problem:** {idea.get('problem', '')}",
            f"**Who buys:** {idea.get('who_buys', '')}",
            f"**Deliverable:** {idea.get('deliverable', '')}",
            f"**Pricing:** {idea.get('pricing_model', '')} — {idea.get('price_usd', '')}",
            f"**Free stack:** {idea.get('free_stack', '')}",
            f"**Channel:** {idea.get('channel', '')}",
            f"**Build effort:** {idea.get('build_effort', '')}",
            f"**Marginal cost:** {idea.get('marginal_cost', '')}",
            f"**Why this audience:** {idea.get('why_this_audience', '')}",
            ""
        ])
    
    lines.extend([
        "## Channels for Passive Distribution",
        ""
    ])
    for ch in state.get("channels", []):
        lines.extend([
            f"### {ch.get('name', '')}",
            f"- **What it does:** {ch.get('what_it_does', ch.get('crypto_payout', ''))}",
            f"- **Cost:** {ch.get('cost', '')}",
            f"- **Crypto payout:** {ch.get('crypto_payout', '')}",
            f"- **Owner setup:** {ch.get('owner_setup', '')}",
            f"- **Why passive:** {ch.get('why_passive', '')}",
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