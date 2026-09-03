"""
Trending tech article sourcing.

Finds recent (last 24h) technology articles from free public feeds and public
tag pages, so the articles module can write an improved, attributed take on a
real story instead of recycling a static topic list.

Read-only. No API keys. Every source is a public feed or public HTML page.
"""
from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from collections.abc import Iterable
from typing import Any
from urllib.parse import quote_plus, urlparse

import requests

from ._shared import parse_dt as _parse_dt, strip_html as _strip_html, xml_text as _xml_text

log = logging.getLogger(__name__)

_UA = "e-evolve-trending/1.0 read-only article research"

# Public RSS/Atom feeds. All are free, keyless, and publisher-sanctioned.
#
# Ordered by editorial authority, which is what `_AUTHORITY` below encodes. A
# story that cleared an editor at InfoQ or shipped on the GitHub engineering
# blog is a better article subject than an arbitrary Medium tag-feed post, and
# readers can tell the difference in the first paragraph.
_FEEDS = [
	("tldr", "https://tldr.tech/api/rss/tech"),
	("infoq", "https://feed.infoq.com/"),
	("lobsters", "https://lobste.rs/rss"),
	("hackernoon", "https://hackernoon.com/feed"),
	("devto-top", "https://dev.to/feed/tag/programming"),
	("smashing", "https://www.smashingmagazine.com/feed/"),
	("github-blog", "https://github.blog/feed/"),
	# Named engineering blogs and outlets. These carry the stories a developer
	# audience already recognises, which is the point of "famous source".
	("aws-arch", "https://aws.amazon.com/blogs/architecture/feed/"),
	("cloudflare", "https://blog.cloudflare.com/rss/"),
	("netflix-tech", "https://netflixtechblog.com/feed"),
	("stackoverflow", "https://stackoverflow.blog/feed/"),
	("martinfowler", "https://martinfowler.com/feed.atom"),
	("gcp-blog", "https://cloudblog.withgoogle.com/rss/"),
	("gitlab", "https://about.gitlab.com/atom.xml"),
	("go-blog", "https://go.dev/blog/feed.atom"),
	("rust-blog", "https://blog.rust-lang.org/feed.xml"),
	("python-insider", "https://blog.python.org/feeds/posts/default"),
	("chrome-dev", "https://developer.chrome.com/static/blog/feed.xml"),
	("mozilla-hacks", "https://hacks.mozilla.org/feed/"),
]

# Editorial authority per source, 0-100. This is the fix for a real ranking
# bug: every feed item used to score a flat 20, which left ~26 of 40 candidates
# tied and made recency the only tiebreak. A Medium tag-feed post then ranked
# level with InfoQ, and the bot wrote articles from sources no reader has heard
# of. Higher here means "a developer audience recognises this masthead".
_AUTHORITY = {
	"github-blog": 62,
	"martinfowler": 62,
	"rust-blog": 60,
	"go-blog": 60,
	"python-insider": 60,
	"cloudflare": 58,
	"netflix-tech": 56,
	"infoq": 55,
	"stackoverflow": 55,
	"chrome-dev": 54,
	"mozilla-hacks": 54,
	"lobsters": 52,
	"aws-arch": 50,
	"gcp-blog": 50,
	"gitlab": 48,
	"tldr": 46,
	"smashing": 44,
	"devto-top": 34,
	"hackernoon": 26,
	"hackerrank": 24,
}

# Medium tag feeds are public RSS -- no scraping needed for these.
_MEDIUM_TAGS = [
	"programming",
	"artificial-intelligence",
	"software-engineering",
	"python",
	"devops",
]

# HackerRank's blog exposes a WordPress-style feed.
_HACKERRANK_FEED = "https://www.hackerrank.com/blog/feed/"

# Medium tag feeds are open-submission: anyone can publish to a tag. They stay
# in the pool for coverage but must never outrank an edited publication.
_MEDIUM_AUTHORITY = 18
_DEFAULT_AUTHORITY = 20

def _feed_score(source: str, dated: bool) -> int:
	"""Rank a feed item by how much authority its publisher carries.

    Recency is a small bonus, not the deciding factor: a two-day-old GitHub
    Blog post is a better article subject than a fresh anonymous tag-feed post.
    """
	if source.startswith("medium:"):
		base = _MEDIUM_AUTHORITY
	else:
		base = _AUTHORITY.get(source, _DEFAULT_AUTHORITY)
	return base + (8 if dated else 0)


_MIN_TITLE_LEN = 20
_MAX_PER_SOURCE = 8

# Hosts that truncate their RSS summary behind a paywall or member wall, so the
# feed gives us a title and two sentences at most.
_PAYWALLED_HOSTS = ("medium.com", "towardsdatascience.com", "betterprogramming.app",
					"levelup.gitconnected.com", "itnext.io", "javascript.plainenglish.io",
					"python.plainenglish.io", "blog.stackademic.com")

# Public Freedium mirror, used only to read the full text of an article we intend
# to write our own take on. Read-only, and only for paywalled hosts.
_FREEDIUM_MIRROR = "https://freedium-mirror.cfd/"

# Below this many characters the summary is too thin to write a real article from.
_MIN_SUMMARY_CHARS = 400


def fetch_candidates(
	max_age_hours: int = 24,
	limit: int = 40,
	exclude_authors: Iterable[str] = (),
) -> list[dict[str, Any]]:
	"""Return recent tech-article candidates, newest first.

    Each candidate: {title, url, source, summary, published_at, score}.
    Sources that fail are logged and skipped -- a dead feed never breaks a cycle.

    ``exclude_authors`` drops the bot's own published work. One of the feeds
    here is dev.to's programming tag, which is also where this bot publishes, so
    its own posts come back as "trending news" a day later. That is not
    hypothetical: it wrote a trending take on its own top article, and the
    resulting post credited itself in a ``## Source`` section as though it were
    somebody else's reporting. Following up on our own work is a real feature --
    it is ``articles._generate_followup``, which recaps honestly and backlinks
    the parent -- so this path must not counterfeit it.
    """
	cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, max_age_hours))
	items: list[dict[str, Any]] = []

	items.extend(_fetch_hn_front_page(cutoff))
	for source, url in _FEEDS:
		items.extend(_fetch_feed(source, url, cutoff))
	for tag in _MEDIUM_TAGS:
		items.extend(_fetch_feed(f"medium:{tag}", f"https://medium.com/feed/tag/{quote_plus(tag)}", cutoff))
	items.extend(_fetch_feed("hackerrank", _HACKERRANK_FEED, cutoff))

	own = _author_keys(exclude_authors)
	relevant = [
		i for i in _dedupe(items)
		if is_technical(i)
		and not is_spam(i)
		and not is_off_topic(i)
		and not is_own_post(i, own)
	]
	relevant.sort(key=lambda i: (i.get("score", 0), i.get("published_at") or ""), reverse=True)
	return relevant[:limit]


def _author_keys(authors: Iterable[str]) -> set[str]:
	"""Normalize author URLs or handles into ``host/handle`` prefix keys.

    Accepts whatever the caller has to hand: a full article URL from the dev.to
    API, a profile URL, or a bare handle. A bare handle is assumed to be dev.to,
    since that is the only place this bot publishes.
    """
	keys: set[str] = set()
	for raw in authors or ():
		value = str(raw or "").strip()
		if not value:
			continue
		if "/" not in value and "." not in value:
			keys.add(f"dev.to/{value.lower().lstrip('@')}")
			continue
		canon = _canonical_url(value if "//" in value else f"https://{value}")
		if not canon:
			continue
		host, _, path = canon.partition("/")
		handle = path.split("/")[0] if path else ""
		if handle:
			keys.add(f"{host}/{handle}")
	return keys


def is_own_post(item: dict[str, Any], author_keys: set[str]) -> bool:
	"""True when a candidate was published by this bot's own account."""
	if not author_keys:
		return False
	canon = _canonical_url(item.get("url", ""))
	if not canon:
		return False
	host, _, path = canon.partition("/")
	handle = path.split("/")[0] if path else ""
	return bool(handle) and f"{host}/{handle}" in author_keys


# A dev.to audience wants engineering content. HN's front page also carries
# science, law, and culture stories that would make a bad developer article.
_TECH_TERMS = {
	"ai", "llm", "gpt", "model", "models", "agent", "agents", "prompt", "rag",
	"python", "javascript", "typescript", "rust", "go", "golang", "java", "ruby",
	"c", "cpp", "zig", "kotlin", "swift", "php", "sql", "bash",
	"api", "apis", "sdk", "cli", "library", "framework", "compiler", "runtime",
	"database", "postgres", "postgresql", "mysql", "sqlite", "redis", "kafka",
	"docker", "kubernetes", "k8s", "devops", "ci", "cd", "terraform", "serverless",
	"aws", "azure", "gcp", "cloud", "linux", "kernel", "unix", "os",
	"code", "coding", "programming", "developer", "developers", "software",
	"engineering", "architecture", "refactor", "debugging", "debug", "testing",
	"performance", "latency", "throughput", "benchmark", "optimization",
	"security", "vulnerability", "cve", "exploit", "encryption", "auth",
	"git", "github", "gitlab", "open-source", "opensource", "release", "version",
	"browser", "frontend", "backend", "fullstack", "react", "vue", "svelte",
	"webassembly", "wasm", "http", "tcp", "dns", "network", "protocol",
	"self-hosted", "selfhosted", "server", "deploy", "deployment", "build",
	"data", "pipeline", "etl", "embedding", "embeddings", "vector", "inference",
	"gpu", "cpu", "memory", "cache", "concurrency", "async", "thread", "threads",
	# Named technologies and engineering nouns the live dev.to feed exposed as
	# gaps: real posts ("What Boot adds over plain Spring", "Production
	# Multi-Agent Systems") were being dropped because no word in them was
	# listed. A missing term costs a genuine article, which is the worse error.
	"spring", "boot", "django", "flask", "rails", "laravel", "spark", "hadoop",
	"nginx", "grpc", "graphql", "rest", "json", "yaml", "regex", "orm",
	"microservice", "microservices", "multi-agent", "agentic", "llms",
	"tokenizer", "quantization", "finetuning", "fine-tuning", "transformer",
	"observability", "telemetry", "logging", "profiler", "profiling",
	"scaling", "distributed", "queue", "webhook", "oauth", "jwt", "tls", "ssl",
	"compiler", "linker", "runtime", "garbage", "allocator", "syscall",
	"container", "containers", "pod", "pods", "helm", "ansible", "nixos",
	"goroutine", "goroutines", "leak", "leaks", "deadlock", "mutex", "race",
	"heap", "stack", "pointer", "buffer", "parser", "lexer", "ast", "bytecode",
	"schema", "migration", "index", "indexes", "query", "queries", "transaction",
	"lambda", "kubectl", "webassembly", "polyfill", "middleware", "daemon",
	# Game and graphics engineering. Real posts here are not gambling ads, and
	# the vocabulary has to be able to tell them apart.
	"engine", "renderer", "rendering", "shader", "physics", "timestep",
	"framerate", "raytracing", "simd", "vulkan", "opengl", "webgl",
}


# Open-submission sources: anyone can publish into these, so the feed's own
# topic scoping guarantees nothing. Medium tag feeds delivered both outright spam
# ("13 Reliable Platforms to Buy Gmail Accounts") and non-technical personal
# essays into the candidate pool, because only Hacker News was being screened.
_UNSCREENED_SOURCES = ("hacker-news", "hackernoon", "devto-top")

# Titles matching these never make a good developer article, whatever the feed.
#
# These are intent signals, not vocabulary. Screening on technical words alone
# cannot separate "MATLAB Online Training | MATLAB Training Courses Online" from
# a real MATLAB post -- both are full of technical words -- and a clothing advert
# whose blurb happened to say "build" and "data" was published as a story in a
# weekly developer digest on exactly that failure. What marks these out is that
# they are selling something or padding a listicle, and the title says so.
_SPAM_PATTERNS = (
	r"\bbuy\s+\w+\s+accounts?\b",
	r"\b(?:best|top)\s+\d+\s+(?:sites?|places?|platforms?|websites?)\b",
	r"\bbuy\s+(?:verified|aged|cheap|bulk)\b",
	r"\b(?:casino|betting|essay writing|write my|coupon|promo code)\b",
	r"\bfollowers?\s+for\s+sale\b",
	r"\b(?:crypto|forex)\s+signals?\b",
	# Agency and course marketing. "Content Marketing Services in Noida",
	# "Best PPC and SEO Company in Noida" and "MATLAB Online Training | MATLAB
	# Training Courses Online" all reached the pool through dev.to's tag feed.
	r"\b(?:seo|ppc|smm|digital marketing|content marketing)\b",
	r"\b(?:services?|company|agency|solutions?)\s+in\s+[a-z]",
	r"\b(?:online\s+training|training\s+courses?|courses?\s+online)\b",
	r"\|.*\b(?:training|courses?|services?|company|agency)\b",
	# Listicle and roundup padding: "100+ ChatGPT Prompts for Developers -- The
	# Ultimate Collection", "MeetGeek vs MeetingMinutes vs Otter.ai".
	r"\b\d{2,}\+?\s+\w+\s+(?:prompts?|tools?|tips?|tricks?|resources?|ideas?)\b",
	r"\bultimate\s+(?:collection|guide|list)\b",
	r"\b[\w.]+\s+vs\.?\s+[\w.]+\s+vs\.?\s+[\w.]+",
	# Feeds in scripts this audience does not read. Two Arabic-language finance
	# posts came through the dev.to programming tag.
	r"[؀-ۿЀ-ӿ]{4,}",
)


# Subjects that are never a developer article, however the blurb is worded.
# A summary keyword cannot rescue these: "Family Matching Outfits: How to Create
# Stylish Looks for Every Family Member" reached a weekly developer digest
# because its marketing blurb happened to contain "build" and "data", and no
# amount of counting technical words in that blurb would have stopped it. The
# title's subject is the thing that disqualifies it.
_OFF_TOPIC_PATTERNS = (
	r"\b(?:outfits?|clothing|fashion|apparel|jewell?ery|footwear|shoes)\b",
	r"\b(?:weight loss|diet|skincare|makeup|perfume|supplements?)\b",
	r"\b(?:astrology|horoscope|tarot|manifestation)\b",
	r"\b(?:visa|immigration|passport|travel packages?|honeymoon)\b",
	r"\b(?:real estate|mortgages?|insurance quotes?|loan offers?)\b",
	r"\b(?:matching|stylish)\s+(?:looks?|outfits?|styles?)\b",
	# Gambling and betting fronts. "Shree Win Game Online - How the Platform
	# Works" cleared the summary rule on a single mention of "security" in
	# otherwise pure ad copy -- the same failure as the clothing advert: one
	# incidental keyword in a blurb about something else entirely.
	r"\b(?:casino|lottery|jackpot|rummy|teen patti|betting\s+(?:app|site|platform))\b",
	r"\b(?:win|earn)\s+(?:real\s+)?(?:money|cash)\b",
	r"\bgame\s+online\b",
)


def is_off_topic(item: dict[str, Any]) -> bool:
	"""True when the title's subject rules a post out for a developer audience."""
	return any(re.search(p, str(item.get("title", "")).lower())
			   for p in _OFF_TOPIC_PATTERNS)


def is_spam(item: dict[str, Any]) -> bool:
	"""True for listicle/affiliate spam that leaks in through open feeds."""
	title = str(item.get("title", "")).lower()
	return any(re.search(p, title) for p in _SPAM_PATTERNS)


def _tech_words(text: str) -> set[str]:
	"""Technical vocabulary present in a piece of text."""
	return set(re.split(r"[^a-z0-9+#-]+", str(text).lower())) & _TECH_TERMS


def is_technical(item: dict[str, Any]) -> bool:
	"""True when a candidate looks like engineering content.

    Curated single-publisher feeds (InfoQ, the Go blog, Cloudflare) are edited,
    so their scoping can be trusted. Open-submission sources cannot be: Hacker
    News carries science and culture stories, and a Medium tag is whatever the
    author typed. Both get keyword-screened.

    The title has to earn its place on its own. This used to pour title and
    summary into one bag of words, so a single incidental hit anywhere in a
    marketing blurb whitelisted the post: a dev.to clothing-store advert reached
    a weekly developer digest because its summary said "build" and "data" while
    its title said nothing technical at all. A technical title is decisive; an
    untechnical one has to be carried by a summary that is technical too.

    Vocabulary alone cannot catch promotional content -- "MATLAB Online Training
    | MATLAB Training Courses Online" is full of real technical words. That is
    what ``is_spam`` is for, and the two run together in ``fetch_candidates``.
    """
	source = str(item.get("source", ""))
	if not (source in _UNSCREENED_SOURCES or source.startswith("medium:")):
		return True
	if _tech_words(item.get("title", "")):
		return True
	return len(_tech_words(item.get("summary", ""))) >= 1


def _fetch_hn_front_page(cutoff: datetime) -> list[dict[str, Any]]:
	"""Hacker News front-page stories via the free Algolia API."""
	try:
		resp = requests.get(
			"https://hn.algolia.com/api/v1/search",
			params={"tags": "front_page", "hitsPerPage": 30},
			headers={"User-Agent": _UA},
			timeout=20,
		)
		if resp.status_code in (403, 429):
			log.warning("[trending] HN front page skipped (%s)", resp.status_code)
			return []
		resp.raise_for_status()
		hits = resp.json().get("hits", [])
	except Exception as exc:
		log.warning("[trending] HN front page failed: %s", exc)
		return []

	out: list[dict[str, Any]] = []
	for hit in hits:
		title = str(hit.get("title") or "").strip()
		url = str(hit.get("url") or "").strip()
		if not title or not url or len(title) < _MIN_TITLE_LEN:
			continue
		published = _parse_dt(hit.get("created_at"))
		if published and published < cutoff:
			continue
		points = int(hit.get("points") or 0)
		comments = int(hit.get("num_comments") or 0)
		# HN engagement is a real quality signal. Keep it unclipped so ranking
		# still discriminates between a 60-point and a 900-point story, but
		# compress it so one viral item can't crowd out every feed source.
		engagement = points + comments // 2
		out.append({
			"title": title,
			"url": url,
			"source": "hacker-news",
			"summary": _strip_html(str(hit.get("story_text") or "")),
			"published_at": published.isoformat() if published else "",
			"score": 30 + min(70, engagement // 10),
		})
	return out[:_MAX_PER_SOURCE * 2]


def _fetch_feed(source: str, feed_url: str, cutoff: datetime) -> list[dict[str, Any]]:
	"""Parse a public RSS or Atom feed. Handles both element shapes."""
	headers = {
		"Accept": "application/atom+xml, application/rss+xml, text/xml;q=0.9, */*;q=0.5",
		"User-Agent": _UA,
	}
	try:
		resp = requests.get(feed_url, headers=headers, timeout=20)
		if resp.status_code in (403, 404, 429):
			log.info("[trending] %s feed skipped (%s)", source, resp.status_code)
			return []
		resp.raise_for_status()
		root = ET.fromstring(resp.content)
	except ET.ParseError as exc:
		log.info("[trending] %s feed unparseable: %s", source, exc)
		return []
	except Exception as exc:
		log.info("[trending] %s feed failed: %s", source, exc)
		return []

	out: list[dict[str, Any]] = []
	# RSS <item> and Atom <entry> cover every feed in _FEEDS.
	for node in list(root.findall(".//{*}item")) + list(root.findall(".//{*}entry")):
		title = _xml_text(node, "title")
		if not title or len(title) < _MIN_TITLE_LEN:
			continue

		url = _xml_text(node, "link")
		if not url:
			for link in node.findall("{*}link"):
				href = str(link.attrib.get("href", "")).strip()
				if href:
					url = href
					break
		if not url.startswith("http"):
			continue

		published = (
			_parse_dt(_xml_text(node, "pubDate"))
			or _parse_dt(_xml_text(node, "published"))
			or _parse_dt(_xml_text(node, "updated"))
			or _parse_dt(_xml_text(node, "date"))
		)
		if published and published < cutoff:
			continue

		summary = (
			_xml_text(node, "description")
			or _xml_text(node, "summary")
			or _xml_text(node, "content")
		)
		out.append({
			"title": title,
			"url": url,
			"source": source,
			"summary": _strip_html(summary)[:1200],
			"published_at": published.isoformat() if published else "",
			# Feeds carry no engagement metric, so rank them by the credibility
			# of the masthead instead. A flat score here used to tie most of the
			# pool together and let recency alone decide.
			"score": _feed_score(source, published is not None),
		})
		if len(out) >= _MAX_PER_SOURCE:
			break
	return out


def is_paywalled(url: str) -> bool:
	"""True when a URL's host truncates its feed summary behind a member wall."""
	host = _canonical_url(url).split("/")[0]
	return any(host == p or host.endswith("." + p) for p in _PAYWALLED_HOSTS)


def needs_unlock(item: dict[str, Any]) -> bool:
	"""True when we have a paywalled source with too little text to write from."""
	return (
		is_paywalled(str(item.get("url", "")))
		and len(str(item.get("summary", ""))) < _MIN_SUMMARY_CHARS
	)


def unlock_summary(item: dict[str, Any], max_chars: int = 6000) -> str:
	"""Fetch fuller text for a paywalled article via the public Freedium mirror.

    Returns the existing summary unchanged on any failure -- a mirror being down
    must degrade the article's research depth, never break the cycle. Read-only.
    """
	url = str(item.get("url", "")).strip()
	current = str(item.get("summary", ""))
	if not url:
		return current

	try:
		resp = requests.get(
			_FREEDIUM_MIRROR + url,
			headers={"User-Agent": _UA, "Accept": "text/html"},
			timeout=25,
		)
		if resp.status_code != 200:
			log.info("[trending] freedium unlock skipped (%s) for %s", resp.status_code, url)
			return current
		text = _extract_article_text(resp.text)
	except Exception as exc:
		log.info("[trending] freedium unlock failed: %s", exc)
		return current

	# Only accept the mirror's text if it is genuinely richer than the feed blurb.
	if len(text) <= max(len(current), _MIN_SUMMARY_CHARS):
		log.info("[trending] freedium returned no usable body for %s", url)
		return current
	log.info("[trending] unlocked %d chars via freedium for %s", len(text), url)
	return text[:max_chars]


def _extract_article_text(html: str) -> str:
	"""Pull readable prose out of a Freedium page without a parser dependency."""
	# Drop non-content elements entirely before stripping tags.
	for tag in ("script", "style", "nav", "header", "footer", "aside", "noscript"):
		html = re.sub(rf"<{tag}\b.*?</{tag}>", " ", html, flags=re.DOTALL | re.IGNORECASE)
	body = re.search(r"<(?:article|main)\b.*?>(.*?)</(?:article|main)>",
					 html, flags=re.DOTALL | re.IGNORECASE)
	if body:
		html = body.group(1)
	# Keep paragraph boundaries so the LLM sees structure, not one long run-on.
	# A sentinel survives _strip_html's whitespace collapsing; a raw \n would not.
	html = re.sub(r"</(p|h[1-6]|li|pre|blockquote)>", " ¶ ", html, flags=re.IGNORECASE)
	text = _strip_html(html)
	text = re.sub(r"(\s*¶\s*)+", "\n\n", text)
	return text.strip()


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
	"""Drop repeats by URL and by normalized title."""
	seen_url: set[str] = set()
	seen_title: set[str] = set()
	out: list[dict[str, Any]] = []
	for item in items:
		url_key = _canonical_url(item.get("url", ""))
		title_key = normalize_title(item.get("title", ""))
		if not url_key or not title_key:
			continue
		if url_key in seen_url or title_key in seen_title:
			continue
		seen_url.add(url_key)
		seen_title.add(title_key)
		out.append(item)
	return out


def _canonical_url(url: str) -> str:
	"""Strip tracking params and trailing slash so the same story matches."""
	try:
		parsed = urlparse(url.strip())
	except Exception:
		return ""
	if not parsed.netloc:
		return ""
	host = parsed.netloc.lower().removeprefix("www.")
	path = parsed.path.rstrip("/").lower()
	return f"{host}{path}"


def normalize_title(title: str) -> str:
	"""Lowercase, strip punctuation/filler, and stem for duplicate detection.

    Crude plural stemming matters here: "Cutting LLM Costs" and "Cutting LLM
    Cost" are the same article for our purposes, and that near-miss is exactly
    how a repeat slips past an exact-match check.
    """
	text = re.sub(r"[^a-z0-9\s]", " ", str(title).lower())
	words = [_stem(w) for w in text.split() if w not in _STOPWORDS]
	return " ".join(w for w in words if w)


def _stem(word: str) -> str:
	"""Strip common English plural/gerund endings. Not linguistically correct,
    just stable enough that trivial variants collapse to one key."""
	for suffix in ("ies", "es", "s"):
		if len(word) > 4 and word.endswith(suffix):
			return word[: -len(suffix)] + ("y" if suffix == "ies" else "")
	return word


# Function words are dropped before comparison so that swapping one preposition
# ("under" -> "during") cannot disguise a repeat of the same article.
_STOPWORDS = {
	"a", "an", "the", "and", "or", "but", "for", "of", "to", "in", "on", "with",
	"your", "you", "how", "why", "what", "is", "are", "was", "were", "be", "been",
	"that", "this", "it", "its", "as", "at", "by", "from", "into", "over",
	"under", "during", "while", "when", "after", "before", "through", "via",
	"about", "against", "between", "without", "within", "using", "use", "used",
	"my", "our", "their", "his", "her", "we", "i", "they", "not", "no",
	"can", "will", "should", "would", "could", "do", "does", "did", "get", "got",
	"guide", "tutorial", "introduction", "intro", "part", "beginners", "beginner",
}
