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

from . import payout

log = logging.getLogger(__name__)


# The house voice, shared by every writing prompt published under this byline,
# so ``articles`` and ``newsletter`` cannot drift apart on style. Gates below
# enforce the mechanical half of it; this tells the model the whole of it.
VOICE = """\
VOICE -- professional, plain and calm. Write the way a respected senior engineer
explains something to a colleague: clear first, never clever for its own sake.
- Short sentences, one idea each. Aim for 12-20 words on average. If a sentence
  needs a semicolon or a second "and", split it.
- Short paragraphs: 2-4 sentences, never more than about 80 words.
- Address the reader as "you". Use "I" only for your own judgement. Do not write
  "we", and never switch voice partway through.
- Active voice, present tense: "the client retries the call", not "the call is
  retried by the client".
- Prefer the plain word: "use" not "utilize", "start" not "commence", "about" not
  "approximately", "so" not "consequently", "help" not "facilitate".
- Be specific. Name the function, flag, file, or error message instead of
  describing it in general terms.
- Explain each acronym or term of art the first time, in one short clause.
- Contractions are fine ("it's", "you'll", "doesn't").
- Respect the reader. No "simply", "just", "obviously", or "of course" -- if it
  were obvious they would not be reading.
- Calm and factual. No hype, no exclamation marks, no stacked rhetorical questions.
- Cut filler. Do not narrate the piece ("In this article", "Let's dive in", "As
  mentioned above"). Do not open sentences with stiff connectors ("Furthermore",
  "Moreover", "Additionally", "Consequently", "In conclusion"). Avoid "delve",
  "seamless", "landscape", and "it's important to note".
- Keep acronyms and product names in their real casing: PDF, JSON, API, GitHub,
  PostgreSQL, macOS."""


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


# Softer style tells: stiff, padded, or machine-sounding prose. Kept apart from
# TONE_PATTERNS on purpose. ``newsletter`` treats a tone problem as a hard
# reject, so adding these there would let one "Additionally" cancel a weekly
# issue. ``articles`` only ever answers them with a revision call.
STYLE_PATTERNS = [
	(r"\b(in this (article|post|guide|tutorial)|let's dive in|without further ado|as mentioned (above|earlier))\b",
	 "meta narration"),
	(r"(^|[.!?]\s+)(furthermore|moreover|additionally|consequently|in conclusion)\b",
	 "stiff transition"),
	(r"\b(delve|delves|delving|seamless|seamlessly)\b", "machine-sounding word"),
	(r"\bit(?: is|'s|’s) (worth noting|important to note)\b", "filler phrase"),
]

# Paragraphs longer than this read as a wall of text on a phone screen.
_MAX_PARAGRAPH_WORDS = 90


def style_problems(body: str) -> list[str]:
	"""Flag prose that is correct but hard to read: padding, stiffness, walls of text.

    Revision-only. Never use this as a reject gate -- see STYLE_PATTERNS.
    """
	prose = strip_code_blocks(body)
	found: list[str] = []
	for pattern, label in STYLE_PATTERNS:
		if re.search(pattern, prose, re.IGNORECASE | re.MULTILINE) and label not in found:
			found.append(label)

	# Lists, tables, quotes and headings are blocks too, but not paragraphs.
	long_paras = [
		p for p in re.split(r"\n\s*\n", prose)
		if p.strip()
		and not re.match(r"\s*([#>|*-]|\d+[.)]\s)", p)
		and len(p.split()) > _MAX_PARAGRAPH_WORDS
	]
	if long_paras:
		found.append(
			f"{len(long_paras)} paragraph(s) over {_MAX_PARAGRAPH_WORDS} words; "
			"split into 2-4 sentence paragraphs"
		)
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


# A fenced code block, opening and closing fence at the start of a line.
_FENCE_RE = re.compile(r"(^```.*?^```[ \t]*$)", re.MULTILINE | re.DOTALL)

# Models emit non-breaking hyphens and spaces ("re‑type"). They render the same
# but break search, copy-paste into a terminal, and any code they land in.
_ODD_CHARS = str.maketrans({"‑": "-", "‐": "-", " ": " ", " ": " "})


def _tidy_prose(text: str) -> str:
	"""Heading fixes for prose only -- never run inside a code fence."""
	# dev.to renders the title itself, so a top-level '#' heading shows up as a
	# duplicate title. Demote any '# ' to '## '.
	text = re.sub(r"^# (?!#)", "## ", text, flags=re.MULTILINE)
	# Strip "1. "/"2) " numbering the model adds to headings. dev.to renders a
	# clean outline without it, and the numbers go stale if sections are reordered.
	text = re.sub(r"^(#{2,3} )\d+[.)]\s+", r"\1", text, flags=re.MULTILINE)
	# Collapse 3+ blank lines to 2, then guarantee one blank line on both sides of
	# every heading. Without the trailing one, dev.to runs the first paragraph
	# into the heading.
	text = re.sub(r"\n{4,}", "\n\n\n", text)
	text = re.sub(r"(?<!\n)\n(#{2,3} )", r"\n\n\1", text)
	return re.sub(r"^(#{2,3} .*)\n(?!\n)(?=\S)", r"\1\n\n", text, flags=re.MULTILINE)


def normalize(data: dict) -> dict:
	"""Clean up markdown artifacts that hurt rendering on dev.to."""
	body = str(data.get("body_markdown", "")).translate(_ODD_CHARS)
	# Strip a stray wrapping code fence around the whole article.
	if body.lstrip().startswith("```markdown"):
		body = re.sub(r"^\s*```markdown\s*\n", "", body)
		body = re.sub(r"\n```\s*$", "", body)
	# Heading fixes run on prose only. Applied to the whole body they rewrote a
	# Python or bash comment at column 0 ("# retry once") into "## retry once".
	# Each fence also gets one blank line on both sides, so a paragraph never
	# starts on the line straight after a closing fence.
	parts = _FENCE_RE.split(body)
	out = _tidy_prose(parts[0]).rstrip()
	for fence, prose in zip(parts[1::2], parts[2::2]):
		out = (out + "\n\n" if out.strip() else "") + fence
		prose = _tidy_prose(prose).strip("\n")
		if prose.strip():
			out += "\n\n" + prose.rstrip()
	data["body_markdown"] = out.strip()
	if "title" in data:
		data["title"] = str(data["title"]).translate(_ODD_CHARS)

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


# Title Case turns acronyms into words: the bot published "The Pdf Parsing
# Script That Wastes Your Hours". Only terms whose capitalised form is never
# right belong here -- "Git" and "Redis" are correct as written, so they are not.
_TITLE_CASING = {w.lower(): w for w in (
	"PDF", "API", "APIs", "JSON", "YAML", "HTML", "CSS", "SQL", "HTTP", "HTTPS",
	"URL", "URLs", "CLI", "SDK", "SDKs", "LLM", "LLMs", "AI", "GPU", "GPUs", "CPU",
	"DNS", "TLS", "SSH", "JWT", "CSV", "XML", "UI", "UX", "AWS", "GCP", "CI", "CD",
	"GitHub", "GitLab", "JavaScript", "TypeScript", "PostgreSQL", "SQLite",
	"GraphQL", "OAuth", "macOS", "iOS", "DevOps", "WebAssembly",
)}


def fix_title_casing(title: str) -> str:
	"""Restore the real casing of acronyms and product names in a title.

    An all-lowercase word is left alone: in a Title Case headline it was written
    that way on purpose (`cd`, `npm`), and Title Case never produces one.
    """
	def fix(m: re.Match) -> str:
		word = m.group(0)
		return word if word.islower() else _TITLE_CASING.get(word.lower(), word)
	return re.sub(r"[A-Za-z]+", fix, str(title or ""))


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
	# Here, not in normalize: titles are also replaced later by _revise_title and
	# re-applied after a format revision, and this is the one place all converge.
	article["title"] = fix_title_casing(article.get("title", "")) or "Untitled"
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
			# Still 0.0, and still for the original reason: a non-zero constant
			# here fabricates earnings. dev.to pays nothing for a post.
			#
			# What changed is that publishing is no longer *only* reach. The
			# support footer gives a reader a way to pay, so a post can now
			# lead to money -- but the amount is unknowable at publish time and
			# arrives days later, if at all. Real revenue stays exactly where
			# it was: the on-chain wallet balance, which is the one figure that
			# cannot be guessed. Attributing a speculative dollar value to a
			# post because it carries a tip address would be the same lie in a
			# new costume.
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


# A dev.to body may open with a YAML front-matter block, and when it does the
# front matter wins over the JSON params on the way in: Forem re-reads title,
# tags and canonical_url from it, and its tag handling starts by clearing the
# existing tag list. So a body-only update on such a post can rewrite the
# title and wipe the tags of a post that took months to earn its traffic.
#
# Nothing this bot publishes uses front matter -- ``publish`` sends title and
# tags as JSON fields -- but the account may hold posts written by hand, and
# "probably not front matter" is not a safe basis for editing a live post that
# is the account's whole readership. Detected and skipped instead.
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
		resp = requests.put(
			url,
			headers={
				"api-key": api_key,
				"Content-Type": "application/json",
				"Accept": "application/vnd.forem.api-v1+json",
			},
			json={"article": {"body_markdown": body_markdown}},
			timeout=30,
		)
		resp.raise_for_status()
		# The write has already landed by here. A body that will not parse is a
		# cosmetic problem, so it must not be reported as a failed update: that
		# would abort the rest of the run over a post that was in fact fixed.
		try:
			data = resp.json() if resp.content else {}
		except Exception:
			data = {}
		return {"success": True, "url": str(data.get("url") or "")}
	except Exception as exc:
		log.warning("[devto] update %s failed: %s", article_id, exc)
		return {"success": False, "error": str(exc)[:200]}
