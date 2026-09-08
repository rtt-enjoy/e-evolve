"""
Earning Module — Recurring-Revenue (MRR) Idea Triage

Research and suggestions only. Takes a catalogue of recurring-revenue business
models and scores each one against THIS project's hard constraints -- zero
server cost, no payment processing, no inbound HTTP, no outreach channel -- then
writes docs/mrr-ideas.md with the few that survive and the concrete first proof
artifact for each.

It never contacts anyone, never processes a payment, and never hosts a service.
Ideas whose delivery requires a blocked action are recorded as REFUSED with the
reason, so the report is honest about what this stack cannot do. The refusal is
computed in Python against ``_BLOCKERS``, not asked of a model, so no LLM can
argue one away.

Activates from config/strategy.json (``mrr_ideas.enabled``). No new secret.

Cost: ONE LLM call per refresh, and refresh_hours defaults to 48, so the module
costs about half a free-tier request per day. Every cheap gate -- disabled,
interval not due, nothing viable, no LLM client -- returns before that call.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ._shared import bounded_append, hours_until_due, load_config
from .code_techs import _cell, _clean_list, _dicts

log = logging.getLogger(__name__)

_REPORT_FILE = Path("docs/mrr-ideas.md")

# Earnings breakdown key. Distinct from the other modules so this product stays
# separately visible. It always reports 0.0 -- research earns nothing directly.
_PLATFORM = "mrr-ideas"

_DEFAULTS = {
	"enabled": True,
	"refresh_hours": 48,
	"max_ideas": 8,
	"min_score": 50,
	"history_limit": 100,
}


def _config() -> dict:
	"""Strategy config for this module, defaults filled in for missing keys."""
	return load_config("mrr_ideas", _DEFAULTS)


# Requirements that make a model impossible or unwanted here, so the idea is
# REFUSED.
#
# Two separate lines are drawn here, and the second one was missing for months.
#
# 1. **Delivery, not billing.** Every recurring-revenue model needs a way to
#    charge -- that is what MRR means -- and the owner can open a storefront by
#    hand in an afternoon. So "needs payments" is a manual setup step, not a
#    refusal. What disqualifies a model is delivery that requires an action
#    this project refuses in code, or infrastructure that does not exist here
#    and is not free.
#
# 2. **The owner's time is not the product.** `sells_owner_time` refuses any
#    model whose revenue is a fee for hours the owner works -- retainers,
#    per-client services, coaching. This was absent, and the omission showed:
#    the surviving list was fine only by accident, while ten retainers sat in
#    the refused table blamed on *cold outreach* rather than on being retainers.
#    That is the wrong reason recorded for the right answer, which is worse than
#    a wrong answer: unblock outreach tomorrow and the module would have started
#    recommending SEO retainers on a passive-income dashboard. Same failure as
#    `code_techs` ranking freelance postings -- see Principle 2b.
_BLOCKERS: dict[str, str] = {
	"sells_owner_time": (
		"revenue is a fee for the owner's hours — a job, not passive income "
		"(Principle 2 row 2)"
	),
	"outreach":        "client acquisition needs cold email/DM — blocked in code",
	"social_posting":  "delivery requires posting to social platforms — blocked in code",
	"inbound_http":    "needs a server accepting requests; GitHub Actions is outbound-only",
	"human_delivery":  "requires a human performing the service per client",
	"paid_dependency": "requires a paid third-party platform",
	"certification":   "requires a professional credential the owner does not hold",
}

# Requirements the owner can satisfy by hand. These do NOT refuse an idea; they
# are surfaced in the report as prerequisites so the plan stays honest about
# what has to happen off-bot before a dollar arrives.
_MANUAL_STEPS: dict[str, str] = {
	# Gumroad is named last and flagged, because it pays out USD via Stripe and
	# takes no crypto -- verified 2026-09-08 and recorded in
	# code_techs._REFUSED_CHANNELS. This module used to recommend it twice as
	# the default payment setup, on a dashboard whose whole receive path is a
	# Tron address. Crypto-settling options come first.
	# Kept to one short clause each: these repeat under every surviving model,
	# so an explanation inline made the report a wall of duplicated text. The
	# fiat/crypto caveat is printed once, in the section header.
	"payments": "owner opens a payout account by hand, once",
	"platform_setup": "owner opens the storefront or channel by hand, once",
	"audience_first": "needs an existing audience; the dev.to byline is the only one this stack builds",
}

# What this stack actually is, printed in the report so it explains itself.
_CONSTRAINTS: list[str] = [
	"Runs on GitHub Actions free tier: hourly, outbound-only, no always-on server.",
	"No inbound HTTP. Nothing can accept a request, a form, or a webhook.",
	"No payment processing. Nothing can charge a card or bill a subscription.",
	"No outreach. Cold email, DMs, and social posting are refused in code.",
	"Can research, analyse, draft, and publish articles to dev.to. That is the whole surface.",
]

# The 20 models from the source article, as static reference data -- seeded the
# same way code_techs._LOCAL_LEADS is. This is NOT a content fallback: nothing
# here is ever published to dev.to.
#
# `blockers` disqualify (see _BLOCKERS). `manual` are owner-by-hand prerequisites
# (see _MANUAL_STEPS) that do not. `bot_role` is the most the bot can contribute.
_CATALOGUE: list[dict[str, Any]] = [
	{
		"name": "Micro SaaS",
		"mrr_model": "$15-99/mo subscription",
		"source_note": "article cites EZ Fulfill, VendorHawk, PODTurbo; verify independently",
		"blockers": ["inbound_http"],
		"manual": ["payments"],
		"bot_role": "research",
	},
	{
		"name": "Local business AI automation agency",
		"mrr_model": "$300-800/mo retainer per client",
		"source_note": "niches: real estate, dental, law, wellness, gyms",
		"blockers": ["sells_owner_time", "outreach", "paid_dependency"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "Paid newsletter",
		"mrr_model": "$10-20/mo per subscriber",
		"source_note": "narrow niche beats broad; audience must exist first",
		"blockers": [],
		"manual": ["payments", "platform_setup", "audience_first"],
		"bot_role": "publish",
	},
	{
		"name": "Online course membership",
		"mrr_model": "$49/mo; ~204 members = $10K MRR",
		"source_note": "article advises building an audience before making content",
		"blockers": [],
		"manual": ["payments", "platform_setup", "audience_first"],
		"bot_role": "research",
	},
	{
		"name": "Notion / digital template store",
		"mrr_model": "$500-5K/mo, library subscription",
		"source_note": "specificity wins; Gumroad listing/updating is API-automatable (POST /v2/products, edit_products scope) once the owner has an account and OAuth token, but its payouts are fiat USD via Stripe — for stablecoin use a crypto-settling storefront; Payhip/Etsy stay manual",
		"blockers": [],
		"manual": ["payments", "platform_setup"],
		"bot_role": "draft",
	},
	{
		"name": "Bookkeeping as a service",
		"mrr_model": "$200-600/mo retainer",
		"source_note": "needs a certification course",
		"blockers": ["sells_owner_time", "certification", "human_delivery", "outreach"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "Social media management retainer",
		"mrr_model": "$500-1.5K/mo per client",
		"source_note": "priced on measurable follower/engagement metrics",
		"blockers": ["sells_owner_time", "social_posting", "outreach"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "SEO retainer",
		"mrr_model": "$400-3K/mo per client",
		"source_note": "results take 3-6 months; expectation-setting is the hard part",
		"blockers": ["sells_owner_time", "outreach", "human_delivery"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "Podcast production service",
		"mrr_model": "$500-2K/mo retainer",
		"source_note": "editing labour per episode",
		"blockers": ["sells_owner_time", "human_delivery", "outreach"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "White-label SaaS reselling",
		"mrr_model": "platform markup, $1-6K/mo",
		"source_note": "HighLevel-style reselling; specialization essential",
		"blockers": ["paid_dependency", "outreach"],
		"manual": ["payments"],
		"bot_role": "none",
	},
	{
		"name": "Email marketing management retainer",
		"mrr_model": "$400-1.2K/mo per client",
		"source_note": "segmentation, automations, monthly reporting",
		"blockers": ["sells_owner_time", "outreach", "human_delivery"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "Paid Discord / Slack community",
		"mrr_model": "$15-50/mo per member",
		"source_note": "needs active facilitation; churn spikes when engagement drops",
		"blockers": ["social_posting"],
		"manual": ["payments"],
		"bot_role": "none",
	},
	{
		"name": "No-code app dev for one industry",
		"mrr_model": "hosting + maintenance retainer",
		"source_note": "Bubble/Glide/Softr; build once, customize per client",
		"blockers": ["sells_owner_time", "outreach", "paid_dependency"],
		"manual": [],
		"bot_role": "research",
	},
	{
		"name": "YouTube automation channel",
		"mrr_model": "AdSense + affiliate + memberships",
		"source_note": "longest runway; 90-270 days, needs 1K subs and 4K watch hours",
		"blockers": ["social_posting"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "Freelance writing retainer",
		"mrr_model": "4-8 articles/mo, $1.5-8K",
		"source_note": "B2B content, ghostwriting; 3-4 clients to buffer churn",
		"blockers": ["sells_owner_time", "outreach"],
		"manual": [],
		"bot_role": "draft",
	},
	{
		"name": "Online tutoring / coaching subscription",
		"mrr_model": "$150-500/mo per client",
		"source_note": "group coaching scales better than one-on-one",
		"blockers": ["sells_owner_time", "human_delivery"],
		"manual": ["payments"],
		"bot_role": "none",
	},
	{
		"name": "API or data feed for a niche",
		"mrr_model": "recurring API access fee",
		"source_note": "article cites AirTrackBot, StageTimer, SheetBest; verify independently",
		"blockers": ["inbound_http"],
		"manual": ["payments"],
		"bot_role": "research",
	},
	{
		"name": "Virtual assistant agency",
		"mrr_model": "$500-2K/mo per client",
		"source_note": "scales by hiring; hiring/retention is the underestimated part",
		"blockers": ["sells_owner_time", "human_delivery", "outreach"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "Niche job board / marketplace",
		"mrr_model": "$99-499 per posting, recruiter memberships",
		"source_note": "cold-start problem: must seed supply and demand together",
		"blockers": ["inbound_http"],
		"manual": ["payments", "platform_setup"],
		"bot_role": "none",
	},
	{
		"name": "Content repurposing service",
		"mrr_model": "$500-1.5K/mo retainer",
		"source_note": "one piece into many formats; needs input quality standards",
		"blockers": ["sells_owner_time", "social_posting", "outreach"],
		"manual": [],
		"bot_role": "none",
	},

	# ── Product models, added 2026-09-08 ────────────────────────────────────
	#
	# The 20 entries above are the source article's list, and every one of them
	# is a *service* business: retainers, agencies, per-client work. Triaging
	# that list could therefore only ever return a newsletter and a template
	# store, because nothing else in it was a product.
	#
	# The owner's actual goal is selling their own digital products (a browser
	# extension was the example) and being paid in crypto. None of the twenty
	# covered that, so refusing eighteen of them was answering a question
	# nobody asked. These are the product-shaped models, and they are the ones
	# that fit a zero-server, outbound-only stack: an artifact is built once and
	# sold many times, with no owner action per sale.
	{
		"name": "Freemium browser extension with a paid upgrade",
		"mrr_model": "one-time or subscription upgrade; free tier drives discovery",
		"source_note": (
			"Chrome Web Store registration is a one-time $5 per account covering "
			"up to 20 extensions (verified 2026-09-08); the store takes no cut of "
			"a free listing. Client-side code means zero marginal cost per user, "
			"so the free tier can stay free indefinitely."
		),
		"blockers": [],
		"manual": ["payments", "platform_setup"],
		"bot_role": "draft",
	},
	{
		"name": "Paid desktop or CLI utility, sold as a download",
		"mrr_model": "one-time licence, or a paid major version",
		"source_note": (
			"Runs on the buyer's machine, so there is no server to pay for and no "
			"inbound HTTP. A crypto-settling storefront can pay out USDT on Tron "
			"to the owner's own wallet, which is the address this project already "
			"publishes."
		),
		"blockers": [],
		"manual": ["payments", "platform_setup"],
		"bot_role": "draft",
	},
	{
		"name": "Developer library or plugin with sponsorship",
		"mrr_model": "recurring sponsorship on a public repository",
		"source_note": (
			"The repository is the discovery channel and it keeps working after "
			"publication. A receive address in the README needs no platform at "
			"all; GitHub Sponsors is the fiat version and needs one manual "
			"enablement. Income is not per-sale, so nothing needs owner action."
		),
		"blockers": [],
		"manual": ["platform_setup"],
		"bot_role": "draft",
	},
	{
		"name": "Wallet ask on published work",
		"mrr_model": "voluntary stablecoin tips, no platform and no fee",
		"source_note": (
			"Already live in this project since 2026-09-04: payout.py appends a "
			"validated Tron address to every dev.to article, and receipt_check "
			"verifies readers can see it. The only model here needing no account, "
			"no fee and no owner action at all -- and therefore the only one "
			"already earning-capable rather than pending a manual step."
		),
		"blockers": [],
		"manual": [],
		"bot_role": "publish",
	},
]

# What the bot can contribute to a surviving idea, by bot_role.
_ROLE_VALUE: dict[str, int] = {
	"publish": 30,   # the bot already publishes to dev.to
	"draft":   20,   # the bot can produce the deliverable text
	"research": 10,  # the bot can only inform the decision
	"none":     0,
}


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
	"""Main entry point. Gate order matters: every cheap check precedes the LLM."""
	cfg = _config()
	state = status.setdefault("mrr_ideas", {})

	if not cfg.get("enabled", True):
		state["enabled"] = False
		log.debug("[mrr_ideas] disabled in strategy config — skipping")
		return []
	state["enabled"] = True

	forced = bool(status.get("_overrides", {}).get("force_mrr"))
	if not forced:
		waiting = hours_until_due(state, "last_refresh_at", int(cfg["refresh_hours"]))
		if waiting > 0:
			log.info("[mrr_ideas] next refresh due in %.1fh — skipping", waiting)
			return []
	else:
		log.info("[mrr_ideas] interval bypassed by 'force mrr' command")

	# Deterministic triage. No LLM call, so a refusal cannot be argued away.
	viable, refused = _triage(_CATALOGUE, cfg)
	log.info("[mrr_ideas] triage: %d viable, %d refused", len(viable), len(refused))

	now = datetime.now(timezone.utc)
	brief: dict[str, Any] = {}

	if not viable:
		# Still worth writing: the refusal list is the useful part.
		log.warning("[mrr_ideas] no idea survived the constraint matrix")
	elif llm is None:
		log.warning("[mrr_ideas] no LLM available — writing deterministic triage only")
	else:
		brief = _viability_brief(llm, viable, cfg)

	state.update({
		"enabled": True,
		"last_refresh_at": now.isoformat(),
		"refresh_hours": int(cfg["refresh_hours"]),
		"constraints": list(_CONSTRAINTS),
		"summary": str(brief.get("summary", "")),
		"ranked_ideas": brief.get("ranked_ideas", []),
		"validation_steps": brief.get("validation_steps", []),
		"owner_actions": brief.get("owner_actions", []),
		"viable": viable,
		"refused": refused,
		"llm_used": bool(brief),
	})
	_record_refresh(status, viable, int(cfg["history_limit"]))
	_write_report(state)

	return [{
		"platform": _PLATFORM,
		"success": True,
		"idea_count": len(viable),
		"refused_count": len(refused),
		"llm": bool(brief),
		"estimated_usd": 0.0,   # research only; nothing here pays
		"title": f"MRR idea triage refreshed ({len(viable)} viable, {len(refused)} refused)",
		"url": str(_REPORT_FILE),
	}]


def _triage(catalogue: list[dict], cfg: dict) -> tuple[list[dict], list[dict]]:
	"""Split the catalogue into (viable, refused). Deterministic, no LLM.

    An idea is refused when any of its blockers is in ``_BLOCKERS``. The refusal
    carries the human-readable reason, so docs/mrr-ideas.md explains WHY an idea
    the owner read about is not being pursued. Survivors are scored and cut to
    max_ideas, so the report stays a shortlist rather than a dump.
    """
	viable: list[dict] = []
	refused: list[dict] = []
	min_score = int(cfg.get("min_score", 50))

	for idea in catalogue:
		name = str(idea.get("name", "")).strip()
		if not name:
			continue
		reasons = [
			_BLOCKERS[key]
			for key in idea.get("blockers", [])
			if key in _BLOCKERS
		]
		if reasons:
			refused.append({
				"name": name,
				"mrr_model": str(idea.get("mrr_model", "")),
				"reason": "; ".join(reasons),
			})
			continue

		score = _score_viability(idea)
		if score < min_score:
			refused.append({
				"name": name,
				"mrr_model": str(idea.get("mrr_model", "")),
				"reason": f"fit score {score} is below the {min_score} threshold for this stack",
			})
			continue

		viable.append({
			"name": name,
			"mrr_model": str(idea.get("mrr_model", "")),
			"source_note": str(idea.get("source_note", "")),
			"bot_role": str(idea.get("bot_role", "none")),
			"score": score,
			# Prerequisites the owner must handle off-bot before any money moves.
			"manual_steps": [
				_MANUAL_STEPS[key]
				for key in idea.get("manual", [])
				if key in _MANUAL_STEPS
			],
		})

	viable.sort(key=lambda i: i["score"], reverse=True)
	return viable[: max(1, int(cfg.get("max_ideas", 8)))], refused


def _score_viability(idea: dict) -> int:
	"""0-100 fit against a zero-cost, outbound-only, research-first stack.

    Rewards an unblocked model the bot can already contribute real work to, and
    one whose revenue does not depend on an audience the owner does not have.
    Deliberately simple: the score only orders the survivors, and every hard
    exclusion has already happened in ``_triage``.

    ``audience_first`` is penalised harder than the other prerequisites because
    it is not a step the owner can just *do*. A payout account takes an
    afternoon; an audience takes months and may never arrive. Scoring them the
    same put "Paid newsletter" -- which needs subscribers this project does not
    have -- above every product model, which needs only a listing. That is the
    same mistake as ranking work above income, one level down: it ordered by
    what the bot can help with rather than by what can actually earn.
    """
	score = 50   # an unblocked model starts at the threshold
	score += _ROLE_VALUE.get(str(idea.get("bot_role", "none")), 0)
	# Evidence of real revenue in the source, rather than an assertion.
	if "verify independently" in str(idea.get("source_note", "")):
		score += 5
	# Each off-bot prerequisite is real work the owner must do before earning.
	manual = [k for k in idea.get("manual", []) if k in _MANUAL_STEPS]
	score -= 5 * len(manual)
	# An audience cannot be opened by hand in an afternoon.
	if "audience_first" in manual:
		score -= 15
	return max(0, min(100, score))


def _viability_brief(llm: Any, viable: list[dict], cfg: dict) -> dict:
	"""ONE research-role LLM call over the whole shortlist.

    Returns {} on any failure -- the report then shows the deterministic triage
    alone, which is still useful. A dead LLM must not cost a second call.
    """
	prompt = {
		"task": (
			"Turn each surviving recurring-revenue model below into a concrete, "
			"honest plan for an owner who can research, write, and publish articles "
			"to dev.to, and nothing else."
		),
		"hard_rules": [
			"Never invent an MRR figure, a customer count, or a company name. "
			"If a number matters, write 'verify independently'.",
			"Every idea must name a specific buyer, a specific first deliverable, "
			"and a realistic monthly price in USD.",
			"The owner has NO client-acquisition channel and NO payment processor. "
			"Never propose a step that requires either.",
			"State plainly what the owner must do by hand, because no automation "
			"here can do it.",
			"Narrow beats broad. Name the actual niche, not the category.",
			"No passive-income framing, no get-rich framing, no autopilot claims.",
		],
		"policy": (
			"Research and suggestions only. Do not propose contacting anyone, "
			"posting to social platforms, collecting payment, trading, or minting."
		),
		"owner_constraints": list(_CONSTRAINTS),
		"surviving_models": [
			{
				"name": i["name"],
				"mrr_model": i["mrr_model"],
				"what_the_bot_can_do": i["bot_role"],
				"owner_must_set_up_by_hand": i.get("manual_steps", []),
			}
			for i in viable
		],
		"required_json_shape": {
			"summary": (
				"one paragraph: the single best recurring-revenue angle for a "
				"zero-cost, research-first, publish-to-dev.to stack"
			),
			"ranked_ideas": [
				{
					"name": "the model name",
					"why_this_stack_fits": "one short reason",
					"narrow_niche": "the specific niche, not the category",
					"first_proof_artifact": "the one thing to make before charging anyone",
					"who_pays": "the specific buyer",
					"monthly_price_usd": "number or small range",
					"runway_to_first_dollar": "e.g. '4-8 weeks'",
					"owner_must_do_by_hand": "the part no automation here can cover",
				}
			],
			"validation_steps": [
				"how to find 10 people with the problem and talk to them WITHOUT "
				"cold outreach — inbound only: an article that ends in a question, "
				"a thread the owner posts by hand, a community they already belong to"
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
		log.warning("[mrr_ideas] viability brief failed: %s — keeping deterministic triage", exc)
		return {}

	if not isinstance(data, dict):
		log.warning("[mrr_ideas] viability brief returned no object — keeping deterministic triage")
		return {}

	return {
		"summary": str(data.get("summary", "")).strip()[:900],
		"ranked_ideas": _dicts(data.get("ranked_ideas"), [
			"name", "why_this_stack_fits", "narrow_niche", "first_proof_artifact",
			"who_pays", "monthly_price_usd", "runway_to_first_dollar",
			"owner_must_do_by_hand",
		], limit=int(cfg.get("max_ideas", 8))),
		"validation_steps": _clean_list(data.get("validation_steps", []))[:6],
		"owner_actions": _clean_list(data.get("owner_actions", []))[:5],
	}


def _history(status: dict) -> dict:
	"""Names already surfaced, so a later report can tell new from repeated."""
	return status.setdefault("mrr_ideas_history", {})


def _record_refresh(status: dict, ideas: list[dict], limit: int) -> None:
	"""Remember which models have been surfaced, bounded by history_limit."""
	hist = _history(status)
	entries = hist.setdefault("names", [])
	for idea in ideas:
		bounded_append(entries, str(idea.get("name", "")).strip(), limit)


def _write_report(state: dict[str, Any]) -> None:
	"""Write docs/mrr-ideas.md. The refusal section is the point of the file."""
	lines: list[str] = [
		"# Recurring Revenue (MRR) Idea Triage",
		"",
		f"Refreshed: {state.get('last_refresh_at', '')}",
		"",
		"Research and suggestions only. This bot does not contact anyone, collect",
		"payment, or host a service. Every figure quoted from the source article",
		"is unverified — check it yourself before acting on it.",
		"",
		"## What This Stack Can Actually Support",
		"",
	]
	lines += [f"- {c}" for c in state.get("constraints", [])]

	summary = str(state.get("summary", "")).strip()
	if summary:
		lines += ["", "## Best Current Angle", "", summary]

	ranked = state.get("ranked_ideas") or []
	if ranked:
		lines += ["", "## Ranked Ideas", ""]
		for idea in ranked:
			lines += [
				f"### {idea.get('name', 'Unnamed')}",
				"",
				f"- **Niche:** {idea.get('narrow_niche', '')}",
				f"- **Who pays:** {idea.get('who_pays', '')}",
				f"- **Monthly price:** {idea.get('monthly_price_usd', '')}",
				f"- **Why this stack fits:** {idea.get('why_this_stack_fits', '')}",
				f"- **First proof artifact:** {idea.get('first_proof_artifact', '')}",
				f"- **Runway to first dollar:** {idea.get('runway_to_first_dollar', '')}",
				f"- **You must do by hand:** {idea.get('owner_must_do_by_hand', '')}",
				"",
			]
	else:
		viable = state.get("viable") or []
		if viable:
			# The heading is chosen by `llm_used`, not by whether `ranked_ideas`
			# came back. It used to key off `ranked_ideas` alone, so a brief
			# that returned a summary but no ranked list printed "no LLM brief
			# this refresh" directly beneath that model's own summary -- a
			# field reporting on work it did not actually check (Principle 3d).
			note = (
				"the LLM brief returned no ranked list this refresh"
				if state.get("llm_used")
				else "no LLM brief this refresh"
			)
			lines += ["", f"## Surviving Models ({note})", ""]
			lines += ["| Model | MRR model | Bot can | Score |", "|---|---|---|---|"]
			lines += [
				f"| {_cell(i.get('name'))} | {_cell(i.get('mrr_model'))} "
				f"| {_cell(i.get('bot_role'))} | {_cell(i.get('score'))} |"
				for i in viable
			]

	# Prerequisites always come from the deterministic triage, never the model,
	# so this section is present whether or not the LLM brief succeeded.
	prereqs = [
		(i.get("name", ""), i.get("manual_steps", []))
		for i in (state.get("viable") or [])
		if i.get("manual_steps")
	]
	if prereqs:
		lines += [
			"",
			"## Set Up By Hand First",
			"",
			"None of these is a blocker — but no money moves until you do them.",
			"",
			"**On the payout account:** to be paid in stablecoin, pick a storefront",
			"that settles to your own wallet — the Leads page lists the verified",
			"ones. Gumroad, Substack and Stripe are fiat-only and pay out in USD,",
			"so they do not reach the Tron address this project already publishes.",
			"",
		]
		for name, steps in prereqs:
			lines.append(f"- **{name}:** " + "; ".join(steps))

	steps = state.get("validation_steps") or []
	if steps:
		lines += ["", "## How To Validate Without Outreach", ""]
		lines += [f"- {s}" for s in steps]

	refused = state.get("refused") or []
	lines += [
		"",
		"## Refused, And Why",
		"",
		"These are not oversights. Each one needs an action this project refuses in",
		"code, or infrastructure that does not exist here and is not free.",
		"",
		"| Model | MRR model | Why not |",
		"|---|---|---|",
	]
	lines += [
		f"| {_cell(r.get('name'))} | {_cell(r.get('mrr_model'))} | {_cell(r.get('reason'))} |"
		for r in refused
	]

	actions = state.get("owner_actions") or []
	if actions:
		lines += ["", "## Next Actions", ""]
		lines += [f"{n}. {a}" for n, a in enumerate(actions, 1)]

	lines.append("")
	_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
	_REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
