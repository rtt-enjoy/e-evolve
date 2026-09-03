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

import logging
import re
from typing import Any

import requests

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

	# Long average sentences read as dense no matter how good the content is.
	sentences = [s for s in re.split(r"[.!?]+\s", prose) if len(s.split()) > 2]
	if sentences:
		avg = sum(len(s.split()) for s in sentences) / len(sentences)
		if avg > 26:
			found.append(f"sentences too long (avg {avg:.0f} words, aim under 22)")
	return found


FABRICATION_PATTERNS = [
	(r"\b\d+\s*[-‐-―~]?\s*\d*\s*ms\b", "invented latency figures (ms)"),
	(r"\$\s?\d+(\.\d+)?\s*(/|per\s)", "invented pricing"),
	(r"\b\d+(\.\d+)?\s*(tokens?/s|tok/s|req/s|requests?/(sec|second))", "invented throughput"),
	(r"\b\d+\s*%\s*(faster|slower|cheaper|better|more accurate)", "invented benchmark deltas"),
]

# Deliberately absent: a rule matching bare model sizes (r"\d+(\.\d+)?\s*[BTM]\b"
# labelled "invented model parameter counts"). It was removed, not narrowed.
#
# It rejected correct prose. "A 7B model in 4-bit sits around 4 GB" is how every
# practitioner writes it, and 7B is a published property of a real model, not a
# figure the writer invented -- so the gate blocked the very articles it should
# wave through. Two of three drafts on an LLM-hardware source died here with
# their prose intact; that is why nothing published on 2026-09-01.
#
# Under re.IGNORECASE it was wider still, also firing on "3 m", "2 T of data"
# and "5 M rows", none of which are parameter counts at all.
#
# Narrowing it was tried and abandoned: the honest test is whether a size is a
# real published model's or one the model made up, and no regex over surrounding
# words decides that. Every attempt either kept rejecting correct prose or
# reduced to a check that could never fire -- dead code wearing a gate's name.
#
# The other four rules are unaffected and still catch invented latency, pricing,
# throughput and benchmark deltas. Fabricated parameter counts are now the one
# claim this gate does not police; the writing prompt still forbids them.


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
		# A table is a run of consecutive lines that all contain a pipe.
		if "|" in lines[i]:
			start = i
			while i < len(lines) and "|" in lines[i]:
				i += 1
			block = lines[start:i]
			# Two lines (header + separator) is the minimum real table.
			if len(block) >= 2 and fabrication_problems("\n".join(block)):
				removed += 1
				while i < len(lines) and not lines[i].strip():
					i += 1
				# Leave exactly one blank line so the next block does not butt
				# against the previous heading or paragraph.
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
	# Strip a stray wrapping code fence around the whole article.
	if body.lstrip().startswith("```markdown"):
		body = re.sub(r"^\s*```markdown\s*\n", "", body)
		body = re.sub(r"\n```\s*$", "", body)
	# dev.to renders the title itself, so a top-level '#' heading shows up as a
	# duplicate title. Demote any '# ' to '## '.
	body = re.sub(r"^# (?!#)", "## ", body, flags=re.MULTILINE)
	# Strip "1. "/"2) " numbering the model adds to headings. dev.to renders a
	# clean outline without it, and the numbers go stale if sections are reordered.
	body = re.sub(r"^(#{2,3} )\d+[.)]\s+", r"\1", body, flags=re.MULTILINE)
	# Collapse 3+ blank lines to 2, then guarantee one blank line on both sides of
	# every heading. Without the trailing one, dev.to runs the first paragraph
	# into the heading.
	body = re.sub(r"\n{4,}", "\n\n\n", body)
	body = re.sub(r"(?<!\n)\n(#{2,3} )", r"\n\n\1", body)
	body = re.sub(r"^(#{2,3} .*)\n(?!\n)(?=\S)", r"\1\n\n", body, flags=re.MULTILINE)
	data["body_markdown"] = body.strip()

	tags = [
		re.sub(r"[^a-z0-9]", "", str(t).lower())
		for t in (data.get("tags") or ["python", "automation"])
	]
	data["tags"] = [t for t in tags if t][:4] or ["python", "automation"]
	return data


def own_post_urls(status: dict) -> list[str]:
	"""This account's own dev.to post URLs, for excluding them as sources.

    Lives here, not in a product, because both ``articles`` and ``newsletter``
    read the same trending feeds and publish to the same account -- there is one
    identity, so there is one list. ``articles._refresh_stats`` writes it from
    the dev.to API each cycle; a product importing it from the other would be
    reaching across a boundary for one account's identity.
    """
	hist = (status or {}).get("article_history") or {}
	return [str(u) for u in hist.get("own_urls", []) if u]


def publish(article: dict, api_key: str) -> dict:
	"""Publish article to dev.to and return action result."""
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
		resp = requests.post(url, headers=headers, json=payload, timeout=30)
		resp.raise_for_status()
		data = resp.json()
		article_url = data.get("url", "")
		log.info("[devto] published: %s", article_url)
		return {
			"platform": "dev.to",
			"success": True,
			"title": article.get("title", "Untitled"),
			"url": article_url,
			# dev.to pays nothing. Publishing is reach, not revenue, so this
			# must stay 0.0 — a non-zero constant here fabricates earnings.
			# Real money is only ever the on-chain wallet balance.
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
