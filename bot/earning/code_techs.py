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
	"refresh_hours": 24,
	"daily_target_usd": 10.0,
	"max_items": 8,
	"min_score": 55,
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
	"github_searches": [
		"free AI API list no credit card in:readme stars:>200",
		"awesome free LLM API in:name,readme stars:>100",
		"free tier AI services awesome list in:readme stars:>150",
		"free OCR API python in:readme stars:>100",
		"free speech to text API in:readme stars:>100",
		"free image generation API wrapper in:readme stars:>100",
		"free embeddings API tier in:readme stars:>50"
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
	"max_reddit_requests": 24,
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
		"Search online for currently-free AI services first, then have Kimi K3 turn them into concrete earning offers.",
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
	last_run = parse_dt(state.get("last_refresh_at"))
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
		"free_ai_focus": _clean_list(cfg.get("free_ai_focus", [])),
		"monetization_patterns": _clean_list(cfg.get("monetization_patterns", [])),
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
					"body": strip_html(str(body)),
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
			"body": strip_html(body),
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

def _score(text: str, labels: list[str], value: float) -> int:
	"""Rank leads by: free AI service signal, ease of earning, and payout clarity."""
	score = 30
	if value:
		score += min(25, int(value / 5))

	# Core signal: a genuinely free AI service or API.
	if _is_free_ai_lead(text):
		score += 26
	if any(word in text for word in ("no credit card", "no card", "without credit card")):
		score += 14
	if any(word in text for word in ("free tier", "free api", "free plan", "free quota", "free allowance")):
		score += 12
	if any(word in text for word in ("open source", "open-weight", "self-host", "local model")):
		score += 6

	# Ease of earning: fast to start, clear buyer, clear price.
	if any(word in text for word in ("fixed price", "per batch", "per hour", "per file", "flat fee", "one-time")):
		score += 12
	if any(word in text for word in ("easy", "simple", "quick", "same day", "under an hour", "no setup")):
		score += 10
	if any(word in text for word in ("retainer", "recurring", "monthly", "subscription")):
		score += 10
	if any(word in text for word in ("productized", "template", "repeatable", "batch")):
		score += 8

	# Concrete, boring, well-paid conversion work.
	if any(word in text for word in ("transcri", "ocr", "extract", "convert", "summari", "translat", "clean up", "cleanup")):
		score += 12
	if any(word in text for word in ("small business", "client", "customer", "seller", "freelance")):
		score += 8
	if "community-request" in labels or "free-ai-api" in labels:
		score += 8

	# Penalties: cost, competition, vagueness.
	if any(word in text for word in ("bounty", "reward", "prize", "contest")):
		score -= 20
	if any(word in text for word in ("credit card required", "paid plan", "trial expires", "14-day trial", "30-day trial")):
		score -= 20
	if any(word in text for word in ("passive income", "get rich", "guaranteed income", "6-figure")):
		score -= 25
	if any(word in text for word in ("need an audience", "followers", "ad spend", "go viral")):
		score -= 15
	return max(0, min(100, score))


def _is_free_ai_lead(text: str) -> bool:
	"""True when the lead names an AI capability AND a free-access signal."""
	ai_terms = (
		"ai", "llm", "gpt", "model", "api", "whisper", "transcri", "ocr",
		"embedding", "vision", "speech", "tts", "image generation", "inference",
	)
	free_terms = (
		"free", "no credit card", "no-cost", "zero cost", "open source",
		"open-weight", "free tier", "free api", "generous",
	)
	return any(t in text for t in ai_terms) and any(t in text for t in free_terms)

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
	if _is_free_ai_lead(text):
		parts.append("runs on a free AI tier, so input cost is zero and margin is total")
	if any(word in text for word in ("no credit card", "no card", "free tier", "free api")):
		parts.append("no card and no upfront spend needed to start")
	if any(word in text for word in ("transcri", "ocr", "extract", "convert", "summari", "translat", "cleanup")):
		parts.append("boring conversion work buyers already pay humans to do by hand")
	if any(word in text for word in ("fixed price", "per batch", "per hour", "per file", "flat fee")):
		parts.append("priceable per unit, so scope and payout are unambiguous")
	if any(word in text for word in ("retainer", "recurring", "monthly")):
		parts.append("recurring revenue from one setup effort")
	if any(word in text for word in ("easy", "simple", "quick", "same day")):
		parts.append("startable today without new skills or tools")
	if any(word in text for word in ("small business", "client", "seller", "customer")):
		parts.append("buyer values the output and never asks which model made it")
	if not parts:
		parts.append("low-cost AI service lead with limited competition")
	return "; ".join(parts[:2])

def _next_step(text: str) -> str:
	if any(word in text for word in ("transcri", "speech", "whisper", "audio")):
		return "Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio."
	if any(word in text for word in ("ocr", "receipt", "invoice", "scan", "pdf")):
		return "Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages."
	if any(word in text for word in ("image", "background", "photo", "logo")):
		return "Process a handful of sample photos on the free image tier and offer a per-image or per-batch rate."
	if any(word in text for word in ("translat", "localiz")):
		return "Translate one sample page on the free tier, verify quality, and price per thousand words."
	if any(word in text for word in ("spreadsheet", "csv", "data", "cleanup", "dedupe")):
		return "Clean one messy sample export with the free LLM tier and quote a flat rate per file."
	if any(word in text for word in ("retainer", "recurring", "report", "monthly", "digest")):
		return "Build the recurring report once on free scheduled compute, then sell it as a low monthly retainer."
	if any(word in text for word in ("setup", "configure", "install", "onboard")):
		return "Document the exact free-tier setup steps once, then charge a flat fee to perform it inside a client's workflow."
	if _is_free_ai_lead(text):
		return "Confirm the free tier limits and terms, build one small working demo, then attach a fixed price to a single narrow task."
	return "Verify the service is genuinely free to use, produce one sample output as proof, and quote a fixed price for one narrow task."

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

def _write_report(state: dict[str, Any]) -> None:
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

def _cell(value: Any) -> str:
	"""Escape a value for use inside a markdown table cell."""
	text = str(value or "").replace("|", "\\|")
	return re.sub(r"\s+", " ", text).strip() or "-"
