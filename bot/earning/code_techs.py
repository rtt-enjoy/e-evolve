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
	# max_items sizes the markdown report; status_max_items sizes the snapshot
	# that is committed every hour. One cap would force a choice between a thin
	# page and a repo that grows hourly, so there are two.
	"max_items": 40,
	"status_max_items": 18,
	"prompt_top_n": 10,
	"min_score": 40,
	"min_demand_share": 0.5,
	"demand_max_age_hours": 72,
	# The HN hiring post is a *monthly* thread, so its replies are up to ~30
	# days old by design and the best of them quote a real hourly rate. Judging
	# them by the 72h window built for a job feed would throw away the
	# highest-intent leads on the page for being what they are.
	"hn_hiring_max_age_hours": 744,
	"supply_max_age_days": 120,
	"himalayas_pages": 3,
	"reddit_backoff_seconds": 5,
	"auto_pursue": False,
	"pursue_score_threshold": 75,
	"requirements": [
		"Lead with free AI services and free AI APIs: no credit card, generous free tier, usable today.",
		"Every suggestion must name the free service, its real limits, and one concrete way to earn with it.",
		"Prefer easy money: something the owner can start in under 2 hours with no upfront spend.",
		"Prefer repeatable offers over one-off tasks, and same-week payout over deferred upside.",
		"State the earning path in plain language: who pays, for what, and roughly how much.",
		"Skip anything needing paid infrastructure, approval queues, or an audience the owner lacks.",
		"Do not count discovery or speculative upside as earnings."
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
		"Resell a free API as a tiny fixed-price service (transcribe, summarize, clean, convert).",
		"Sell the setup, not the compute: charge to configure a free AI tool inside someone's workflow.",
		"Bundle a free API into a one-page tool and charge a small one-time fee.",
		"Offer a done-for-you batch job: send files, get results back, fixed price per batch.",
		"Charge for the prompt library and workflow, and let the client bring their own free key.",
		"Package a recurring report built on free-tier APIs as a low-cost monthly retainer."
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
	# These are *repository* queries and they run against search/repositories.
	# They used to be sent to search/issues, which ignores `in:readme` and
	# `stars:` -- the same query string returned 12 junk issues there versus
	# 511 real repositories here.
	"github_searches": [
		"free AI API list no credit card in:name,description,readme stars:>200",
		"awesome free LLM API in:name,readme stars:>100",
		"free tier AI services awesome list in:readme stars:>150",
		"free OCR API python in:readme stars:>100",
		"free speech to text API in:readme stars:>100",
		"free image generation API wrapper in:readme stars:>100",
		"free embeddings API tier in:readme stars:>50"
	],
	# Contract-shaped terms in an HN "Who is hiring" reply. A reply that says
	# none of these is a full-time posting, which this project cannot sell into.
	"hn_contract_terms": [
		"contract", "contractor", "freelance", "part-time", "part time"
	],
	# Himalayas returns every remote job on the site, so employment type or
	# category has to narrow it or unrelated roles bury the technical ones.
	"job_employment_types": ["Contractor", "Part Time", "Freelance"],
	"job_categories": [
		"Software Development", "Data Science", "Design", "Writing",
		"Marketing", "Customer Support", "Product"
	],
	"deliverable_terms": [
		"transcri", "ocr", "extract", "convert", "summari", "translat",
		"cleanup", "clean up", "automat", "scrape", "scraper", "dashboard",
		"report", "integration", "migration", "pipeline"
	],
	"community_searches": [
		"free AI API no credit card",
		"free LLM API free tier",
		"best free AI API for",
		"free tier AI service generous",
		"free transcription API",
		"free OCR API",
		"free image generation API free",
		"how I make money with AI free tools",
		"side income AI automation no upfront cost",
		"easiest way to make money with AI",
		"charge clients for AI automation",
		"productized AI service small",
		"free API to build a paid tool",
		"is there a free tool for"
	],
	"reddit_subreddits": [
		"SideProject",
		"sideproject",
		"Entrepreneur",
		"smallbusiness",
		"SaaS",
		"LocalLLaMA",
		"artificial",
		"automation",
		"freelance",
		"WorkOnline"
	],
	"reddit_searches": [
		"free AI API",
		"free LLM API no credit card",
		"free tier AI service",
		"free transcription API",
		"free OCR API",
		"make money with AI tools",
		"easy side income automation",
		"charge for AI automation setup",
		"productized service AI",
		"built a tool with free API",
		"is there a free tool",
		"how much to charge automation"
	],
	# Measured, not guessed: 10 sequential search.rss calls returned 1x200 and
	# 9x429, and 2s spacing returned 0/5. Reddit blocks the IP, not the query,
	# so a large budget just burns the whole cycle on the first subreddit --
	# which is why the live page only ever showed r/SideProject.
	"max_reddit_requests": 3,
	"underserved_focus": [
		"free AI APIs with real free tiers that most people have not heard of yet",
		"boring conversions people pay for: audio to text, image to text, PDF to data",
		"one-task tools that wrap a single free API and solve one annoyance well",
		"AI setup help for non-technical owners who cannot configure a key themselves",
		"batch jobs where the client sends files and gets clean output back",
		"recurring reports assembled from free-tier APIs on a schedule",
		"prompt libraries and workflows sold as a template, client brings their own free key",
		"small-business tasks still done by hand that a free AI API removes entirely",
		"niches where the buyer values the result and never asks what model produced it"
	],
	"strategy_playbook": [
		"Search online for currently-free AI services first, then have the LLM turn them into concrete earning offers.",
		"Sell the outcome, not the technology. Buyers pay for clean output, not for an API name.",
		"Keep input cost at zero: free API, free hosting, free scheduler. Every dollar in is margin.",
		"Prefer offers the owner can deliver the same day with no upfront spend.",
		"Start with one narrow task and a fixed price. Expand scope only after the first payment.",
		"Let the free tier set the batch size, and price per batch so limits are never a problem.",
		"Reuse each delivery as a public example that brings the next buyer."
	],
	"avoid_patterns": [
		"Anything requiring paid infrastructure, credit-card-gated tiers, or upfront spend.",
		"Services whose free tier is a short trial rather than an ongoing allowance.",
		"Offers needing a large audience, ad spend, or a following the owner does not have.",
		"Vague 'AI consulting' with no specific deliverable, fixed price, or named buyer.",
		"Reselling an API in a way its terms of service forbid.",
		"Bounty and prize hunting where many contributors compete for low-value visibility.",
		"Crypto/NFT hype work and anything promising passive income without delivery."
	]
}

# There is deliberately no `outreach` block. This module used to render a
# ready-to-send cold-outreach email per lead, and cold outreach is refused in
# code. Every live draft also quoted a fabricated price and ended with
# "Payment address (USDT_WALLET_ADDRESS): [redacted]", because status.py
# redacts any env name containing WALLET. Repairing it would mean widening that
# redaction exemption to expose the receive address inside research notes for a
# channel the bot may not use. Removed 2026-09-08 by owner decision.

_LOCAL_LEADS = [
	{
		"title": "Meeting and podcast transcription with a free speech-to-text API",
		"url": "",
		"source": "local-playbook",
		"body": "Free tiers from Groq Whisper, Deepgram, and AssemblyAI transcribe hours of audio at no cost. Sell a fixed price per hour of audio: clean transcript, speaker labels, and a short summary returned the same day. Buyers are podcasters, coaches, and small agencies who currently type it themselves.",
		"labels": ["free-ai-api", "speech-to-text", "easy-money", "same-day"]
	},
	{
		"title": "Scanned document and receipt data extraction with a free OCR API",
		"url": "",
		"source": "local-playbook",
		"body": "Free OCR tiers plus a free vision LLM turn scans, receipts, and invoices into a clean spreadsheet. Charge per batch of pages. Bookkeepers and small shops pay for this because the alternative is manual retyping.",
		"labels": ["free-ai-api", "ocr", "batch-job", "easy-money"]
	},
	{
		"title": "Free-tier AI setup service for non-technical business owners",
		"url": "",
		"source": "local-playbook",
		"body": "Most owners cannot get an API key, pick a model, or write a prompt. Charge a flat fee to configure one free AI tool inside the workflow they already use, hand over a short prompt library, and let them keep the free key. Zero input cost, all the value is in the setup.",
		"labels": ["free-ai-api", "setup-service", "no-cost", "repeatable"]
	},
	{
		"title": "Product description and listing generation on a free LLM tier",
		"url": "",
		"source": "local-playbook",
		"body": "Free tiers from Groq, Gemini, and OpenRouter generate hundreds of listings per day at no cost. Sell per-batch copy for Etsy, Shopify, and marketplace sellers who have inventory but no time to write. Price per 50 listings.",
		"labels": ["free-ai-api", "content", "batch-job", "easy-money"]
	},
	{
		"title": "Recurring AI summary report built on free scheduled compute",
		"url": "",
		"source": "local-playbook",
		"body": "GitHub Actions plus a free LLM tier produces a weekly digest of competitor pricing, review sentiment, or industry news. Sell it as a low-cost monthly retainer. The whole stack runs on free allowances, so margin is near total.",
		"labels": ["free-ai-api", "retainer", "recurring", "free-compute"]
	},
	{
		"title": "Spreadsheet and CSV cleanup with a free LLM",
		"url": "",
		"source": "local-playbook",
		"body": "Messy exports need categorizing, deduping, and normalizing. A free LLM tier handles this in bulk. Charge per file. Buyers are small businesses migrating CRMs or preparing data for an accountant.",
		"labels": ["free-ai-api", "data-cleanup", "batch-job", "easy-money"]
	},
	{
		"title": "Image background removal and product photo cleanup on free tiers",
		"url": "",
		"source": "local-playbook",
		"body": "Free background-removal and image APIs clean up product photos at no cost. Sell per-image or per-batch to marketplace sellers who need consistent white-background shots.",
		"labels": ["free-ai-api", "image", "batch-job", "easy-money"]
	},
	{
		"title": "Translation and localization batches on a free API tier",
		"url": "",
		"source": "local-playbook",
		"body": "Free translation and LLM tiers localize listings, menus, and help docs. Charge per thousand words. Small exporters and local restaurants need this and do not want a full agency.",
		"labels": ["free-ai-api", "translation", "batch-job"]
	}
]

_GITHUB_MAX_PER_MIN = 10

# Word-boundary AI capability terms. Bare "ai" as a substring matched
# *contain*, *available* and *email*, so it is anchored here instead.
_AI_TERM_RE = re.compile(
	r"\b(ai|llm|gpt|whisper|ocr|embedding|embeddings|tts|"
	r"transcription|inference|vision|speech)\b"
)
# How near a "free" signal has to sit to an AI term to count as related.
_FREE_WINDOW = 60

# An hourly rate a human typed: the unit is mandatory, so "$4,500 in funding"
# cannot match. Deliberately does not accept "$120k" -- a full-time annual
# salary is not a price for a deliverable this project can sell.
_RATE_RE = re.compile(
	r"\$\s?(\d{2,4})(?:\s*(?:-|--|to|–|—)\s*\$?\s?(\d{2,4}))?"
	# "USD" often sits between the figure and the unit ("$23-$34 USD/hour").
	r"\s*(?:usd)?\s*(?:/|\s+per\s+)?\s*(?:hr|hour)\b",
	re.IGNORECASE,
)
_PERIOD_LABELS = {
	"hourly": "/hr", "daily": "/day", "weekly": "/wk",
	"monthly": "/mo", "annual": "/yr", "yearly": "/yr",
}

# A lead is one of two things, and conflating them is what made the page
# useless: "demand" means somebody is paying for work right now, "supply"
# means free tooling to deliver that work with. GitHub answers the second
# question well and the first one badly.
_DEMAND = "demand"
_SUPPLY = "supply"


@dataclass
class Opportunity:
	title: str
	url: str
	source: str
	# Who is actually paying, when the source names them. The feed name
	# ("himalayas") is not a buyer, and a prompt that says it is gives the
	# reading model nothing to write to.
	buyer: str
	kind: str
	score: int
	score_parts: dict[str, float]
	# None, never 0.0, when no price was published. 0.0 sums silently into a
	# total and sorts as the worst lead; None forces the UI to render an em
	# dash. Same reasoning as `receipt_check`'s third "unreachable" state.
	value_usd: float | None
	value_basis: str
	value_note: str
	# posted_at is when the market said it; discovered_at is when we saw it.
	# Collapsing the two lets an old post masquerade as fresh.
	posted_at: str | None
	discovered_at: str
	age_hours: float | None
	reason: str
	next_step: str
	codex_prompt: str
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
	raw = _fetch_online_leads(cfg) or list(_LOCAL_LEADS)
	opportunities = _rank(raw, cfg, max_items=max_items, min_score=min_score)

	pursued_count = 0
	if cfg.get("auto_pursue"):
		log.warning("[code_techs] auto_pursue ignored: research-only policy forbids posting comments")

	# These counts describe the leads actually in the snapshot, not the longer
	# ranked list. A count that exceeds what the page can show is a claim the
	# page cannot back up -- the same "field reports on more than it covers"
	# problem `receipt_check` exists to catch. `ranked_total` carries the rest.
	shown = opportunities[:status_max_items]
	demand = sum(1 for op in shown if op.kind == _DEMAND)
	priced = sum(1 for op in shown if op.value_basis != "none")
	state.update({
		"enabled": True,
		"last_refresh_at": now.isoformat(),
		"daily_target_usd": float(cfg.get("daily_target_usd", 10.0) or 10.0),
		"refresh_hours": refresh_hours,
		# The report may be long; the snapshot is committed hourly, so it is
		# the one that gets trimmed.
		"opportunities": [op.__dict__ for op in shown],
		"demand_count": demand,
		"supply_count": len(shown) - demand,
		"priced_count": priced,
		"ranked_total": len(opportunities),
		"requirements": _clean_list(cfg.get("requirements", [])),
		"reference_sources": _reference_sources(cfg),
		"remote_service_niches": _clean_list(cfg.get("remote_service_niches", [])),
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
	"""Free AI tooling to deliver with -- a SUPPLY source, not a demand one.

    This used to query ``search/issues`` with repository qualifiers
    (``in:readme``, ``stars:>200``) that endpoint ignores, so it returned
    whatever issue happened to match the loose text: a studio's roadmap, an
    "awesome ideas" PR, a bot's own trend digest. The identical query string
    returns 12 junk issues on ``search/issues`` and 511 real repositories here.

    Asking GitHub *who will pay* was also tried -- ``label:"help wanted"``,
    ``label:bounty``, ``"willing to pay"``, all with ``created:>`` windows --
    and every variant returned noise. The doctrine refuses bounty hunting
    anyway. So GitHub answers "what can I build with" and the job boards
    answer "who is paying".
    """
	leads: list[dict[str, Any]] = []
	token = os.getenv("GITHUB_TOKEN", "").strip()
	headers = {
		"Accept": "application/vnd.github+json",
		"User-Agent": "e-evolve-code-techs"
	}
	# Optional. The search endpoints are keyless; a token only raises the rate
	# limit, so this module still needs no secret of its own.
	if token:
		headers["Authorization"] = f"Bearer {token}"

	max_age_days = max(1, int(cfg.get("supply_max_age_days", 120) or 120))
	cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
	# Local, not module-global: module-level mutable counters make the
	# rate-limit test depend on which test ran first.
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
					"kind": _SUPPLY,
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
	"""Fetch public, read-only leads from free, keyless sources.

    Ordered demand-first so that if a later source fails, what survives is
    still market signal rather than a page of tooling.

    Two sources were probed and refused, recorded here so a later cycle does
    not re-derive them: **Jobicy** is fresh but publishes no salary field at
    all, and **RemoteOK** had 1 of 100 jobs posted within three days (the
    staleness this module exists to fix) and its terms require a permanent
    follow-backlink on the consuming page.
    """
	leads: list[dict[str, Any]] = []
	leads.extend(_fetch_remote_job_leads(cfg))
	leads.extend(_fetch_hn_hiring_leads(cfg))
	leads.extend(_fetch_hn_leads(cfg))
	leads.extend(_fetch_reddit_leads(cfg))
	leads.extend(_fetch_github_leads(cfg))
	return _dedupe(leads)

def _fetch_remote_job_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
	"""Remote contract postings from Himalayas -- keyless, and genuinely current.

    This is the fix for "too old": every sampled job was posted within 24h,
    some minutes before the fetch. It is also the only source with a
    *structured* salary field, so it is where an honest `value_usd` can come
    from at all (see `_lead_value`).
    """
	leads: list[dict[str, Any]] = []
	pages = max(1, int(cfg.get("himalayas_pages", 3) or 3))
	max_age_hours = max(1, int(cfg.get("demand_max_age_hours", 72) or 72))
	cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
	wanted_types = {str(t).lower() for t in cfg.get("job_employment_types", [])}
	wanted_cats = {str(c).lower() for c in cfg.get("job_categories", [])}
	headers = {"User-Agent": "e-evolve-code-techs", "Accept": "application/json"}
	cursor = ""

	for _ in range(pages):
		params: dict[str, Any] = {"limit": 50}
		if cursor:
			params["cursor"] = cursor
		try:
			resp = requests.get(
				"https://himalayas.app/jobs/api",
				params=params,
				headers=headers,
				timeout=25,
			)
			if resp.status_code in (403, 429):
				log.warning("[code_techs] Himalayas skipped (%s)", resp.status_code)
				return leads
			resp.raise_for_status()
			payload = resp.json()
		except Exception as exc:
			log.warning("[code_techs] Himalayas fetch failed: %s", exc)
			return leads

		jobs = payload.get("jobs") or []
		if not jobs:
			break
		for job in jobs:
			stamp = parse_dt(job.get("pubDate"))
			if stamp and stamp < cutoff:
				continue
			emp = str(job.get("employmentType") or "")
			cats = [str(c) for c in (job.get("parentCategories") or [])]
			# Himalayas lists every remote job on the site. Without this the
			# technical postings are buried under unrelated roles.
			type_match = emp.lower() in wanted_types
			cat_match = any(c.lower() in wanted_cats for c in cats)
			if wanted_types and wanted_cats and not (type_match or cat_match):
				continue
			company = str(job.get("companyName") or "")
			title = str(job.get("title") or "")
			leads.append({
				"title": f"{title} - {company}" if company else title,
				"url": str(job.get("applicationLink") or job.get("guid") or ""),
				"source": "himalayas",
				"kind": _DEMAND,
				"body": strip_html(str(job.get("excerpt") or job.get("description") or "")),
				"labels": [c.lower() for c in cats] + ([emp.lower()] if emp else []),
				"posted_at": job.get("pubDate"),
				"buyer": company,
				"employment_type": emp,
				"seniority": str(job.get("seniority") or ""),
				"min_salary": job.get("minSalary"),
				"max_salary": job.get("maxSalary"),
				"salary_period": str(job.get("salaryPeriod") or ""),
				"currency": str(job.get("currency") or ""),
			})
		cursor = str(payload.get("nextCursor") or "")
		if not cursor:
			break
	return leads

def _fetch_hn_hiring_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
	"""Contract offers inside the monthly HN "Who is hiring" thread.

    The highest-intent free source available: a live thread carried 242 replies
    of which 26 offered contract, freelance or part-time work, some quoting a
    real hourly rate. Two requests total, both keyless.

    The thread is found by ``author_whoishiring`` rather than by title. The
    title query also matches unrelated "Show HN: I filtered Who is Hiring..."
    posts; the account name is the reliable selector. An empty result is a
    normal outcome here, never an error -- if HN ever renames that account
    this source simply yields nothing.
    """
	headers = {"User-Agent": "e-evolve-code-techs", "Accept": "application/json"}
	terms = [str(t).lower() for t in cfg.get("hn_contract_terms", []) if str(t).strip()]
	if not terms:
		return []
	try:
		resp = requests.get(
			"https://hn.algolia.com/api/v1/search_by_date",
			params={"tags": "story,author_whoishiring", "hitsPerPage": 5},
			headers=headers,
			timeout=20,
		)
		resp.raise_for_status()
		hits = [h for h in resp.json().get("hits", []) if "hiring" in str(h.get("title") or "").lower()]
		# "Who wants to be hired?" is posted by the same account in the same
		# hour; those replies are people seeking work, not buyers.
		hits = [h for h in hits if "wants to be hired" not in str(h.get("title") or "").lower()]
		if not hits:
			log.info("[code_techs] no HN hiring thread found this cycle")
			return []
		thread_id = str(hits[0].get("objectID") or "")
		if not thread_id:
			return []
		item = requests.get(
			f"https://hn.algolia.com/api/v1/items/{thread_id}",
			headers=headers,
			timeout=30,
		)
		item.raise_for_status()
		children = item.json().get("children") or []
	except Exception as exc:
		log.warning("[code_techs] HN hiring thread fetch failed: %s", exc)
		return []

	max_age_hours = max(1, int(cfg.get("hn_hiring_max_age_hours", 744) or 744))
	cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
	leads: list[dict[str, Any]] = []
	for child in children:
		raw = str(child.get("text") or "")
		if not raw:
			continue
		stamp = parse_dt(child.get("created_at"))
		if stamp and stamp < cutoff:
			continue
		body = strip_html(raw)
		if not any(term in body.lower() for term in terms):
			continue
		# HN hiring replies open with "Company | Role | REMOTE | Contract",
		# so the first segment is the buyer and the head is the headline.
		head = body.split("\n")[0]
		buyer = head.split("|")[0].strip()[:80]
		child_id = str(child.get("id") or "")
		leads.append({
			"title": head[:180] or "Hacker News contract offer",
			"url": f"https://news.ycombinator.com/item?id={child_id}" if child_id else "",
			"source": "hn-hiring",
			"kind": _DEMAND,
			"body": body,
			"labels": ["hn-hiring", "contract"],
			"posted_at": child.get("created_at"),
			"buyer": buyer,
			"allow_rate_extraction": True,
		})
	return leads

def _fetch_hn_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
	leads: list[dict[str, Any]] = []
	headers = {"User-Agent": "e-evolve-code-techs"}
	max_age_hours = max(1, int(cfg.get("demand_max_age_hours", 72) or 72))
	# Algolia can filter by age server-side, so a stale thread with one recent
	# comment never arrives in the first place.
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
					"kind": _DEMAND,
					"body": strip_html(str(body)),
					"labels": ["community-request", "free-api"],
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
	backoff = max(0, int(cfg.get("reddit_backoff_seconds", 5) or 0))
	request_count = 0
	# One query per subreddit, so a tiny budget still spans several
	# communities. The old nested loop spent all 24 requests on the first two
	# subreddits, which is why the live page showed nothing but r/SideProject.
	for index, subreddit in enumerate(subreddits):
		if request_count >= max_requests:
			break
		query = queries[index % len(queries)]
		request_count += 1
		url = (
			f"https://www.reddit.com/r/{quote_plus(subreddit)}/search.rss"
			f"?q={quote_plus(query)}&restrict_sr=1&sort=new"
		)
		try:
			resp = requests.get(url, headers=headers, timeout=20)
			if resp.status_code in (403, 429):
				# Reddit throttles the IP, not the query, so continuing would
				# burn the rest of the budget on certain failures. Stopping is
				# not an error: this source is a bonus, never required.
				log.info(
					"[code_techs] Reddit throttled (%s) at r/%s; stopping Reddit for this cycle",
					resp.status_code, subreddit
				)
				if backoff:
					time.sleep(backoff)
				break
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
			"kind": _DEMAND,
			"body": strip_html(body),
			"labels": ["reddit", "community-request", "free-rss"],
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
		is_local = lead.get("source") == "local-playbook"
		# A playbook entry is a written-down offer, not a market signal: it has
		# no timestamp and must never carry a price.
		kind = str(lead.get("kind") or (_SUPPLY if is_local else _DEMAND))

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
			pursued=False
		))

	# Sort by score, then freshness. Value is deliberately not a sort key here:
	# most leads have none, so it would rank on its own absence.
	ranked.sort(key=lambda op: (op.score, -(op.age_hours if op.age_hours is not None else 1e9)), reverse=True)
	selected = _apply_demand_share(ranked, cfg, max_items)

	# Prompts are the expensive field (~1.7 KB each) and status.json is
	# committed hourly, so only the leads worth acting on carry one.
	for position, op in enumerate(selected):
		if position < prompt_top_n:
			op.codex_prompt = _codex_prompt(op, cfg)
	return selected

def _apply_demand_share(
	ranked: list[Opportunity], cfg: dict[str, Any], max_items: int
) -> list[Opportunity]:
	"""Reserve part of the page for demand leads.

    Supply leads are plentiful and score well on tooling signals, so without a
    floor a good crop of repositories can crowd out every posting where
    somebody is actually paying -- the exact failure the owner reported.
    """
	share = float(cfg.get("min_demand_share", 0.5) or 0.0)
	demand = [op for op in ranked if op.kind == _DEMAND]
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
	"""Use the configured research LLM to synthesize online lead signals."""
	if llm is None:
		return {
			"summary": "No LLM client was available; queue used online searches plus local fallback heuristics.",
			"owner_actions": [
				"Review the ranked leads manually before doing local implementation work.",
				"Add or refresh a free research LLM key to improve lead synthesis.",
			],
		}

	# Demand leads first. This used to take leads[:12] in fetch order, so the
	# brief could be written entirely from tooling repositories and say
	# nothing about what anyone is currently paying for.
	ordered = (
		[x for x in leads if x.get("kind") == _DEMAND]
		+ [x for x in leads if x.get("kind") != _DEMAND]
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
			"Find FREE AI services and FREE AI APIs the owner can use to earn money, "
			"and turn them into easy, concrete earning suggestions."
		),
		"hard_rules": [
			"Every free_ai_service entry must be a real service you are confident exists.",
			"Prefer services with an ongoing free tier, not a time-limited trial.",
			"Say plainly whether a credit card is required.",
			"If unsure about a specific limit, write 'verify current limit' instead of inventing a number.",
			"Each earning idea must state who pays, for what, and a realistic price in USD.",
			"Prefer ideas startable in under 2 hours with zero upfront spend.",
			"No passive-income promises, no get-rich framing, no audience-dependent plans.",
		],
		"policy": "Research and suggestions only. Do not contact anyone, request payment, trade, or mint.",
		"focus_areas": _clean_list(cfg.get("free_ai_focus", [])),
		"monetization_patterns": _clean_list(cfg.get("monetization_patterns", [])),
		"avoid": _clean_list(cfg.get("avoid_patterns", [])),
		"lead_samples": samples,
		"required_json_shape": {
			"summary": "one concise paragraph on the best current free-AI earning angle",
			"market_themes": [
				{
					"theme": "what the demand leads above have in common",
					"evidence": "which lead titles show it",
					"offer": "the specific service to sell into that theme",
				}
			],
			"free_ai_services": [
				{
					"name": "service or API name",
					"what_it_does": "capability in one short phrase",
					"free_tier": "what you get free, or 'verify current limit'",
					"credit_card_required": "no | yes | verify",
					"earn_with_it": "one concrete way to make money using it",
					"price_guide": "realistic price the owner could charge, in USD",
				}
			],
			"easy_earning_ideas": [
				{
					"idea": "short name for the offer",
					"who_pays": "the specific buyer",
					"deliverable": "exactly what the buyer receives",
					"price_usd": "number or small range",
					"time_to_first_dollar": "e.g. 'same day', '2-3 days'",
					"free_stack": "the free services this runs on",
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
			"summary": f"Online AI brief failed; used online search and local scoring only. Error: {str(exc)[:160]}",
			"free_ai_services": [],
			"easy_earning_ideas": [],
			"owner_actions": [
				"Review the ranked free-AI leads below and pick the one with the clearest buyer.",
				"Verify the free tier limits yourself before quoting a price.",
			],
		}

	return {
		"summary": str(data.get("summary", "")).strip()[:900],
		"market_themes": _dicts(data.get("market_themes"), ["theme", "evidence", "offer"], limit=5),
		"free_ai_services": _dicts(data.get("free_ai_services"), [
			"name", "what_it_does", "free_tier", "credit_card_required",
			"earn_with_it", "price_guide",
		], limit=10),
		"easy_earning_ideas": _dicts(data.get("easy_earning_ideas"), [
			"idea", "who_pays", "deliverable", "price_usd",
			"time_to_first_dollar", "free_stack",
		], limit=8),
		"owner_actions": _clean_list(data.get("owner_actions", []))[:5],
	}


def _dicts(value: Any, fields: list[str], limit: int) -> list[dict[str, str]]:
	"""Coerce an LLM list-of-objects into clean string dicts with known fields."""
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
	"""Weighted 0-100 score that actually discriminates between leads.

    The old version started at 30 and added up to ~140 of overlapping bonuses
    before clamping to 100, so anything half-decent saturated: the live queue
    scored 100, 100, 100, 100, 100, 98, 96, 96 and ``min_score: 55`` filtered
    nothing at all.

    Each component is normalised to 0..1 and multiplied by a weight, so a
    lead's rank is a blend rather than a race to the clamp. ``score_parts`` is
    returned alongside so the dashboard can show *why* a lead ranks, and so a
    later cycle can see which component is doing the work.
    """
	# Recency is judged against the window the lead's own source works on. A
	# reply in the monthly HN hiring thread is not stale at 100h the way a job
	# feed posting would be, and scoring both on one scale would bury the
	# highest-intent leads for being what they are.
	if str(lead.get("source") or "") == "hn-hiring":
		max_age = max(1.0, float(cfg.get("hn_hiring_max_age_hours", 744) or 744))
	elif kind == _SUPPLY:
		max_age = max(1.0, float(cfg.get("supply_max_age_days", 120) or 120) * 24)
	else:
		max_age = max(1.0, float(cfg.get("demand_max_age_hours", 72) or 72))

	# Linear decay over that window. An unknown age is not free -- it scores
	# below anything confirmed fresh, above anything stale.
	if age_hours is None:
		recency = 0.3
	else:
		recency = max(0.0, 1.0 - (max(0.0, age_hours) / max_age))

	has_rate = value_basis in ("posted_salary", "stated_rate")
	contract_terms = ("contract", "freelance", "part-time", "part time", "contractor")
	request_terms = ("looking for", "need help", "does anyone", "anyone know", "hiring", "wanted")
	if kind == _SUPPLY:
		intent = 0.15
	elif any(term in text for term in contract_terms) and has_rate:
		intent = 1.0
	elif any(term in text for term in contract_terms):
		intent = 0.7
	elif any(term in text for term in request_terms):
		intent = 0.4
	else:
		intent = 0.25

	deliverables = [str(t).lower() for t in cfg.get("deliverable_terms", [])]
	hits = sum(1 for term in deliverables if term and term in text)
	deliverability = min(1.0, hits / 3.0)

	parts = {
		"recency": round(recency, 3),
		"demand_intent": round(intent, 3),
		"value_clarity": 1.0 if has_rate else 0.0,
		"deliverability": round(deliverability, 3),
		"free_stack_fit": 1.0 if _is_free_ai_lead(text) else 0.0,
	}
	score = (
		30 * parts["recency"]
		+ 25 * parts["demand_intent"]
		+ 20 * parts["value_clarity"]
		+ 15 * parts["deliverability"]
		+ 10 * parts["free_stack_fit"]
	)

	penalty = 0
	if any(word in text for word in ("bounty", "prize", "contest")):
		penalty += 15
	if any(word in text for word in ("credit card required", "paid plan", "trial expires")):
		penalty += 10
	if any(word in text for word in ("passive income", "get rich", "guaranteed income", "6-figure")):
		penalty += 15
	if any(word in text for word in ("need an audience", "followers", "ad spend", "go viral")):
		penalty += 10
	if penalty:
		parts["penalty"] = float(-penalty)

	return max(0, min(100, round(score - penalty))), parts


def _is_free_ai_lead(text: str) -> bool:
	"""True when the lead names an AI capability AND a nearby free-access signal.

    Both halves used to be substring checks over the whole blob, which is how
    "I spent a year making a Markdown editor for Windows ... free" was
    classified as a free-AI earning lead: bare ``"ai"`` matches *contain*,
    *available* and *email*, and the free term could sit paragraphs away.

    So: word-boundary matching on the capability, and the free signal has to
    appear within ``_FREE_WINDOW`` characters of it. Proximity is what carries
    the claim that the two words are actually about each other.
    """
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
	"""Return ``(value_usd, value_basis, value_note)`` -- published prices only.

    This replaces ``_extract_value``, which took ``max()`` of every ``$N``
    regex match in the lead text and, failing that, invented
    ``daily_target_usd`` because the body contained the word "need". Every
    lead therefore carried a figure: the live queue's top lead read **$4,500**,
    scraped out of an unrelated repository roadmap, and the dashboard summed
    those into a "$5.6k pipeline value" shown beside a real on-chain balance
    of $0.00.

    Only two things count as a price here: a salary field the job board
    published, or a rate the poster themselves typed. Everything else returns
    ``None`` -- not ``0.0``, because 0.0 sums silently into totals and sorts as
    the cheapest lead, while None forces the UI to admit it does not know.
    """
	low = _money(lead.get("min_salary"))
	high = _money(lead.get("max_salary"))
	if low or high:
		currency = str(lead.get("currency") or "").upper()
		# A CAD figure rendered with a "$" is simply a wrong number, and
		# converting it would need a rate -- i.e. an estimate.
		if currency in ("", "USD"):
			amount = low or high
			period = str(lead.get("salary_period") or "").lower()
			suffix = _PERIOD_LABELS.get(period, "")
			if low and high and high != low:
				note = f"${low:,.0f}-{high:,.0f}{suffix} posted"
			else:
				note = f"${amount:,.0f}{suffix} posted"
			# Never normalise hourly to annual: the multiplier (2080? 1000?)
			# would itself be the estimate this function exists to refuse.
			return amount, "posted_salary", note

	# A rate the poster wrote, and only from sources where that text is the
	# offer itself. Requires an explicit unit, so "$4,500 of funding" cannot
	# match. On a live thread this fired on 2 of 242 comments -- both real.
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
	"""Positive float or None. Zero is not a price, it is a missing price."""
	try:
		amount = float(str(value).replace(",", "").strip())
	except (TypeError, ValueError):
		return None
	return amount if amount > 0 else None


def _reason(
	lead: dict[str, Any],
	text: str,
	labels: list[str],
	kind: str,
	value_note: str,
	age_hours: float | None,
) -> str:
	parts: list[str] = []
	if value_note:
		parts.append(f"{value_note} by the source, not inferred")
	if kind == _DEMAND and age_hours is not None and age_hours <= 24:
		parts.append(f"posted {int(age_hours)}h ago, so the buyer is still looking")
	if kind == _SUPPLY:
		parts.append("free tooling you can deliver paid work with")
	if any(word in text for word in ("contract", "freelance", "part-time", "contractor")):
		parts.append("scoped as contract or part-time work, which suits one narrow deliverable")
	if any(word in text for word in ("transcri", "ocr", "extract", "convert", "summari", "translat", "cleanup")):
		parts.append("boring conversion work buyers already pay humans to do by hand")
	if _is_free_ai_lead(text):
		parts.append("runs on a free AI tier, so input cost is zero and margin is total")
	if not parts:
		parts.append("matches the free-AI service niche with no upfront spend")
	return "; ".join(parts[:2])


def _next_step(lead: dict[str, Any], kind: str, cfg: dict[str, Any]) -> str:
	"""One concrete move, chosen from the lead's OWN subject.

    This used to keyword-match the title, body and labels concatenated
    together, so a single stray word anywhere decided the advice: all three
    GitHub leads in the live queue were told to "transcribe one sample file"
    and none of them involved audio. Matching the title and labels only keeps
    the recommendation about what the lead is actually for.
    """
	subject = " ".join([
		str(lead.get("title") or ""),
		" ".join(str(x) for x in lead.get("labels") or []),
	]).lower()
	buyer = str(lead.get("buyer") or "").strip()

	if kind == _SUPPLY:
		return (
			"Confirm the free tier's real limits and terms, run one small end-to-end sample, "
			"then attach a fixed price to a single narrow task built on it."
		)
	who = buyer or "the poster"
	if any(word in subject for word in ("transcri", "speech", "whisper", "audio", "podcast")):
		deliverable = "transcribe one sample file end to end and quote per hour of audio"
	elif any(word in subject for word in ("ocr", "receipt", "invoice", "scan", "pdf", "document")):
		deliverable = "run one scanned sample to a clean spreadsheet and quote per batch of pages"
	elif any(word in subject for word in ("image", "photo", "design", "logo", "video")):
		deliverable = "process a handful of sample assets and quote per image or per batch"
	elif any(word in subject for word in ("translat", "localiz", "content", "writing", "copy")):
		deliverable = "produce one sample page and quote per thousand words"
	elif any(word in subject for word in ("csv", "spreadsheet", "analytics", "etl", "scrap")):
		deliverable = "clean one messy sample export and quote a flat rate per file"
	elif any(word in subject for word in ("engineer", "developer", "programming", "backend", "frontend", "software")):
		deliverable = "build the smallest working slice of the stated problem and quote per milestone"
	elif any(word in subject for word in ("support", "customer", "success")):
		deliverable = "draft one worked reply set from their own docs and quote per month"
	else:
		deliverable = "build the smallest working slice of what they asked for and quote a fixed price"
	return f"Read what {who} actually asked for, then {deliverable}."


def _codex_prompt(op: Opportunity, cfg: dict[str, Any]) -> str:
	"""A prompt built from this lead's real fields, not a fixed template.

    Six labelled slots so the reading model gets the market context it needs:
    who the buyer is, what they signalled, what to deliver, what the price
    basis is, which free stack to use, and how to verify.

    The PRICE BASIS slot states the *absence* of a price out loud when there
    is none. A prompt that simply omitted it invited the model to invent a
    figure, which would rebuild the fabrication this module just removed
    inside the one field the owner reads most.
    """
	free_stack = _clean_list(cfg.get("free_ai_focus", []))[:2]
	price = op.value_note or "no stated price - do not quote or invent a figure"
	age = f"{op.age_hours:.0f}h ago" if op.age_hours is not None else "age unknown"
	why = " ".join(str(op.reason or "").split())
	return (
		"Build a small, verifiable deliverable for this real market signal.\n\n"
		f"BUYER          {op.buyer or 'not named'} (via {op.source})\n"
		f"DEMAND SIGNAL  {op.title}\n"
		f"POSTED         {op.posted_at or 'unknown'} ({age})\n"
		f"LINK           {op.url or 'no public URL'}\n"
		f"DELIVERABLE    {op.next_step}\n"
		f"PRICE BASIS    {price}\n"
		f"FREE STACK     {'; '.join(free_stack) or 'any zero-cost AI tier'}\n"
		f"WHY IT RANKS   {why}\n\n"
		"Constraints:\n"
		"- Keep the first change narrowly scoped to one file or script.\n"
		"- Use free API tiers or offline code paths only; no paid service.\n"
		"- Include the exact commands to run it and paste the real output.\n"
		"- Verify on at least 3 sample inputs before calling it done.\n"
		"- Do not contact anyone, publish anything, or request payment.\n"
		"- Do not state a price unless PRICE BASIS gives one."
	)


def _write_report(state: dict[str, Any], leads: list[dict[str, Any]] | None = None) -> None:
	"""Write the markdown report.

    ``leads`` carries the full ranked list, which is longer than the copy kept
    in ``state`` -- a static page can be long, while status.json is committed
    every hour. Falls back to the snapshot when not supplied.
    """
	_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
	lines = [
		"# Free AI Earning Queue",
		"",
		f"Refreshed: {state.get('last_refresh_at')}",
		f"Daily target: ${float(state.get('daily_target_usd', 10.0) or 10.0):.2f}",
		"",
		"Suggestions favour free AI services and free AI APIs with zero upfront cost.",
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

	services = brief.get("free_ai_services") or []
	if services:
		lines.extend([
			"", "## Free AI Services To Use", "",
			"| Service | What it does | Free tier | Card? | How to earn | Price guide |",
			"| --- | --- | --- | --- | --- | --- |",
		])
		for svc in services:
			lines.append(
				"| {} | {} | {} | {} | {} | {} |".format(
					_cell(svc.get("name")), _cell(svc.get("what_it_does")),
					_cell(svc.get("free_tier")), _cell(svc.get("credit_card_required")),
					_cell(svc.get("earn_with_it")), _cell(svc.get("price_guide")),
				)
			)

	ideas = brief.get("easy_earning_ideas") or []
	if ideas:
		lines.extend(["", "## Easy Earning Ideas", ""])
		for index, idea in enumerate(ideas, start=1):
			lines.extend([
				f"{index}. **{idea.get('idea', 'untitled')}**",
				f"   - Who pays: {idea.get('who_pays', '')}",
				f"   - Deliverable: {idea.get('deliverable', '')}",
				f"   - Price: {idea.get('price_usd', '')}",
				f"   - Time to first dollar: {idea.get('time_to_first_dollar', '')}",
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
	lines.extend(["", "## Ranked Leads From Online Search", ""])
	for index, op in enumerate(leads if leads is not None else state.get("opportunities", []), start=1):
		title = op.get("title", "untitled")
		url = op.get("url", "")
		pursued_tag = " [PURSUED]" if op.get("pursued") else ""
		heading = f"{index}. [{title}]({url}){pursued_tag}" if url else f"{index}. {title}{pursued_tag}"
		age = op.get("age_hours")
		lines.extend([
			heading,
			f"   - Kind: {op.get('kind', 'unknown')}",
			f"   - Score: {op.get('score', 0)}/100",
			# The published price or nothing. A figure with no basis is what
			# this module used to print, and it was invented.
			f"   - Price: {op.get('value_note') or 'no stated price'}",
			f"   - Posted: {op.get('posted_at') or 'unknown'}"
			+ (f" ({age:.0f}h ago)" if isinstance(age, (int, float)) else ""),
			f"   - Why: {op.get('reason', '')}",
			f"   - Next: {op.get('next_step', '')}",
		])
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
	"""Escape a value for use inside a markdown table cell."""
	text = str(value or "").replace("|", "\\|")
	return re.sub(r"\s+", " ", text).strip() or "-"
