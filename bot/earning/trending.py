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
from typing import Any
from urllib.parse import quote_plus, urlparse

import requests

log = logging.getLogger(__name__)

_UA = "e-evolve-trending/1.0 read-only article research"

# Public RSS/Atom feeds. All are free, keyless, and publisher-sanctioned.
_FEEDS = [
    ("tldr", "https://tldr.tech/api/rss/tech"),
    ("infoq", "https://feed.infoq.com/"),
    ("lobsters", "https://lobste.rs/rss"),
    ("hackernoon", "https://hackernoon.com/feed"),
    ("devto-top", "https://dev.to/feed/tag/programming"),
    ("smashing", "https://www.smashingmagazine.com/feed/"),
    ("github-blog", "https://github.blog/feed/"),
]

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

_MIN_TITLE_LEN = 20
_MAX_PER_SOURCE = 8


def fetch_candidates(max_age_hours: int = 24, limit: int = 40) -> list[dict[str, Any]]:
    """Return recent tech-article candidates, newest first.

    Each candidate: {title, url, source, summary, published_at, score}.
    Sources that fail are logged and skipped -- a dead feed never breaks a cycle.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, max_age_hours))
    items: list[dict[str, Any]] = []

    items.extend(_fetch_hn_front_page(cutoff))
    for source, url in _FEEDS:
        items.extend(_fetch_feed(source, url, cutoff))
    for tag in _MEDIUM_TAGS:
        items.extend(_fetch_feed(f"medium:{tag}", f"https://medium.com/feed/tag/{quote_plus(tag)}", cutoff))
    items.extend(_fetch_feed("hackerrank", _HACKERRANK_FEED, cutoff))

    relevant = [i for i in _dedupe(items) if is_technical(i)]
    relevant.sort(key=lambda i: (i.get("score", 0), i.get("published_at") or ""), reverse=True)
    return relevant[:limit]


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
}


def is_technical(item: dict[str, Any]) -> bool:
    """True when a candidate looks like engineering content.

    Feed-based sources are already topic-scoped by the feed itself; only the
    open-ended HN front page needs keyword screening.
    """
    source = str(item.get("source", ""))
    if source != "hacker-news":
        return True
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    words = set(re.split(r"[^a-z0-9+#-]+", text))
    return bool(words & _TECH_TERMS)


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
            # Feeds carry no engagement metric; score by recency presence only.
            "score": 20 if published else 10,
        })
        if len(out) >= _MAX_PER_SOURCE:
            break
    return out


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


def _strip_html(value: str) -> str:
    value = re.sub(r"<script.*?</script>", " ", value, flags=re.DOTALL | re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"&[a-z]+;", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _xml_text(parent: ET.Element, tag: str) -> str:
    element = parent.find(f"{{*}}{tag}")
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def _parse_dt(value: Any) -> datetime | None:
    """Parse ISO-8601 or RFC-822 (RSS pubDate) timestamps."""
    if not value:
        return None
    raw = str(value).strip()
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(raw)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None
