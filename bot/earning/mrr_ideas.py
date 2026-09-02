"""
Earning Module \u2014 Recurring-Revenue (MRR) Idea Triage

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


# Requirements that make a model impossible here, so the idea is REFUSED.
#
# The line is drawn at delivery, not at billing. Every recurring-revenue model
# needs a way to charge -- that is what MRR means -- and the owner can open a
# Gumroad or Substack account by hand in an afternoon. So "needs payments" is a
# manual setup step, not a refusal. What genuinely disqualifies a model is
# delivery that requires an action this project refuses in code, or
# infrastructure that does not exist here and is not free.
_BLOCKERS: dict[str, str] = {
	"outreach":        "client acquisition needs cold email/DM \u2014 blocked in code",
	"social_posting":  "delivery requires posting to social platforms \u2014 blocked in code",
	"inbound_http":    "needs a server accepting requests; GitHub Actions is outbound-only",
	"human_delivery":  "requires a human performing the service per client",
	"paid_dependency": "requires a paid third-party platform",
	"certification":   "requires a professional credential the owner does not hold",
}

# Requirements the owner can satisfy by hand. These do NOT refuse an idea; they
# are surfaced in the report as prerequisites so the plan stays honest about
# what has to happen off-bot before a dollar arrives.
_MANUAL_STEPS: dict[str, str] = {
	"payments":       "owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe)",
	"platform_setup": "owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API)",
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
		"blockers": ["outreach", "paid_dependency"],
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
		"source_note": "specificity wins; Gumroad listing/updating is API-automatable (POST /v2/products, edit_products scope) once the owner has an account and OAuth token \u2014 Payhip/Etsy stay manual",
		"blockers": [],
		"manual": ["payments", "platform_setup"],
		"bot_role": "draft",
	},
	{
		"name": "Bookkeeping as a service",
		"mrr_model": "$200-600/mo retainer",
		"source_note": "needs a certification course",
		"blockers": ["certification", "human_delivery", "outreach"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "Social media management retainer",
		"mrr_model": "$500-1.5K/mo per client",
		"source_note": "priced on measurable follower/engagement metrics",
		"blockers": ["social_posting", "outreach"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "SEO retainer",
		"mrr_model": "$400-3K/mo per client",
		"source_note": "results take 3-6 months; expectation-setting is the hard part",
		"blockers": ["outreach", "human_delivery"],
		"manual": [],
		"bot_role": "none",
	},
	{
		"name": "Podcast production service",
		"mrr_model": "$500-2K/mo retainer",
		"source_note": "editing labour per episode",
		"blockers": ["human_delivery", "outreach"],
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
		"blockers": ["outreach", "human_delivery"],
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
		"blockers": ["outreach", "paid_dependency"],
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
		"blockers": ["outreach"],
		"manual": [],
		"bot_role": "draft",
	},
	{
		"name": "Online tutoring / coaching subscription",
		"mrr_model": "$150-500/mo per client",
		"source_note": "group coaching scales better than one-on-one",
		"blockers": ["human_delivery"],
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
		"blockers": ["human_delivery", "outreach"],
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
		"blockers": ["social_posting", "outreach"],
		"manual": [],
		"bot_role": "none",
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
		log.debug("[mrr_ideas] disabled in strategy config \u2014 skipping")
		return []
	state["enabled"] = True

	forced = bool(status.get("_overrides", {}).get("force_mrr"))
	if not forced:
		waiting = hours_until_due(state, "last_refresh_at", int(cfg["refresh_hours"]))
		if waiting > 0:
			log.info("[mrr_ideas] next refresh due in %.1fh \u2014 skipping", waiting)
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
		log.warning("[mrr_ideas] no LLM available \u2014 writing deterministic triage only")
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

    Rewards an unblocked model the bot can already contribute real work to.
    Deliberately simple: the score only orders the survivors, and every hard
    exclusion has already happened in ``_triage``.
    """
	score = 50   # an unblocked model starts at the threshold
	score += _ROLE_VALUE.get(str(idea.get("bot_role", "none")), 0)
	# Evidence of real revenue in the source, rather than an assertion.
	if "verify independently" in str(idea.get("source_note", "")):
		score += 5
	# Each off-bot prerequisite is real work the owner must do before earning.
	score -= 5 * len([k for k in idea.get("manual", []) if k in _MANUAL_STEPS])
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
				"cold outreach \u2014 inbound only: an article that ends in a question, "
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
		log.warning("[mrr_ideas] viability brief failed: %s \u2014 keeping deterministic triage", exc)
		return {}

	if not isinstance(data, dict):
		log.warning("[mrr_ideas] viability brief returned no object \u2014 keeping deterministic triage")
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
		"is unverified \u2014 check it yourself before acting on it.",
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
			lines += ["", "## Surviving Models (no LLM brief this refresh)", ""]
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
			"None of these is a blocker \u2014 but no money moves until you do them.",
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

	# Always bound the history lists in the report itself. The status dict is
	# already trimmed by _record_refresh, but doc readers land here first, and a
	# report that only ever shows the last dozen triages is more useful than one
	# that grows without end. The same value is the soft cap, not a separate one.
	hist = state.get("mrr_ideas_history") or {}
	names = list(hist.get("names") or [])
	if names:
		lines += ["", "## Recently Triaged", ""]
		for name in names[-20:]:
			lines.append(f"- {name}")

	lines.append("")
	_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
	_REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")