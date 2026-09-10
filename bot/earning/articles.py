import re
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

_TITLE_BANNED = [
    (r"\bultimate\b", 'clickbait word "ultimate"'),
    (r"\bcomplete guide\b", 'overused "complete guide"'),
    (r"\beverything you (need|ever needed) to know\b", 'overused "everything you need to know"'),
    (r"\byou need to know\b", 'clickbait "you need to know"'),
    (r"\b(amazing|awesome|incredible|mind.blowing|insane|crazy)\b", "hype adjective"),
    (r"\b(secrets?|hacks?)\b", 'content-farm word "secrets/hacks"'),
    (r"\bdeep dive\b", 'overused "deep dive"'),
    (r"\btop \d+\b", 'listicle "top N"'),
    (r"\bmust.(know|read|have)\b", 'clickbait "must-know"'),
    (r"!", "exclamation mark"),
    ("__SHOUTING__", "ALL-CAPS word"),
    (r"\b\d+\s*(things|ways|tips|tricks|reasons)\s+(you|to|that|for|about)\b", "generic listicle framing"),
]

_TITLE_VAGUE = (
    "better code", "best practices", "getting started", "introduction to",
    "a guide to", "an overview", "the basics", "explained simply", "made easy",
    "for beginners",
)

_KNOWN_ACRONYMS = {
    "JSON", "HTTP", "HTTPS", "HTML", "CSS", "YAML", "TOML", "CSV", "XML", "SQL",
    "REST", "GRPC", "GRAPHQL", "JWT", "OAUTH", "SAML", "CORS", "CRUD", "ACID",
    "TCP", "UDP", "DNS", "SSH", "TLS", "SSL", "VPN", "CDN", "URL", "URI", "API",
    "SDK", "CLI", "GUI", "IDE", "CPU", "GPU", "RAM", "SSD", "OS", "VM", "AWS",
    "GCP", "SQLITE", "POSTGRES", "MYSQL", "REDIS", "NGINX", "LLM", "LLMS", "RAG",
    "GPT", "AI", "ML", "ETL", "CI", "CD", "TDD", "DDD", "MVC", "ORM", "UUID",
    "ASCII", "UTF", "REGEX", "WASM", "PDF", "OCR", "NPM", "PIP", "GIT", "AST",
    "IO", "FIFO", "LIFO", "RPC", "SSR", "SPA", "PWA", "DOM", "SEO", "MRR", "IDE",
    "NLP", "JS", "SVG", "RSS", "UI", "UX", "DB",
}


def _shouted_words(text: str) -> list[str]:
    """All-caps words that are not recognised acronyms."""
    return [
        word for word in re.findall(r"\b[A-Z]{2,}\b", text)
        if word.upper() not in _KNOWN_ACRONYMS
    ]


def _title_problems(title: str, cfg: dict | None = None) -> list[str]:
    """Reject titles that will not earn a click.

    Views are decided in the feed, before anyone sees the body, so the title
    gets a gate of its own. Deterministic -- costs no LLM call.
    """
    cfg = cfg or _config()
    text = str(title or "").strip()
    problems: list[str] = []
    if not text:
        return ["title is empty"]

    hi = int(cfg["title_max_chars"])
    lo = int(cfg["title_min_chars"])
    if len(text) > hi:
        problems.append(f"title too long ({len(text)} chars, max {hi})")
    if len(text) < lo:
        problems.append(f"title too short ({len(text)} chars, min {lo})")

    for pattern, label in _TITLE_BANNED:
        if pattern == "__SHOUTING__":
            if _shouted_words(text):
                problems.append(f"title has {label}")
            continue
        if re.search(pattern, text, re.IGNORECASE):
            problems.append(f"title has {label}")

    lowered = text.lower()
    vague = [phrase for phrase in _TITLE_VAGUE if phrase in lowered]
    if vague:
        problems.append(f"title uses vague filler: {vague[0]!r}")

    # Date-specific vague filler like "in 2026". Replaces the per-year
    # entries that used to live in _TITLE_VAGUE, which had to be updated
    # by hand each calendar year.
    if re.search(r"\bin\s+\d{4}\b", lowered):
        problems.append("title uses vague date filler")

    # A colon subtitle usually means the model padded a weak headline. Allow a
    # short prefix ("Postgres: ...") but reject two full clauses.
    if ":" in text:
        head, _, tail = text.partition(":")
        if len(head.split()) >= 3 and len(tail.split()) >= 4:
            problems.append("title padded with a colon subtitle; pick the sharper half")

    return problems


def _config() -> dict[str, Any]:
    """Return the articles strategy config."""
    from bot.config import get_config
    return get_config().get("articles", {})


def _get_existing_titles() -> set[str]:
    """Return titles already published to avoid duplicates."""
    from bot.earning.history import get_history
    return {entry["title"] for entry in get_history("articles")}


def _publish_article(draft: dict[str, Any]) -> dict[str, Any]:
    """Publish a single article draft via the DEV API."""
    from bot.devto import publish_article
    return publish_article(draft)


def run() -> dict[str, Any]:
    """Fetch or generate an article, validate its title, and publish it.

    Returns a dict summarising the cycle outcome.
    """
    cfg = _config()
    if not cfg.get("enabled", True):
        return {"status": "skipped", "reason": "articles earning is disabled"}

    from bot.llm import chat

    max_articles = int(cfg.get("max_articles_per_cycle", 1))
    min_words = int(cfg.get("min_words", 700))
    history_limit = int(cfg.get("history_limit", 200))
    existing_titles = _get_existing_titles()

    published: list[dict[str, Any]] = []
    skipped: list[str] = []

    for _ in range(max_articles):
        # Ask the LLM for a draft.
        prompt = (
            "Write a single technical article draft. "
            f"Minimum {min_words} words. "
            "Return JSON with keys: title, body, tags. "
            "The title must be compelling and specific -- no clickbait, "
            "no vague filler, no listicle framing. "
            "Focus on a concrete topic with real substance."
        )
        response = chat(prompt)

        try:
            import json
            draft = json.loads(response)
        except (json.JSONDecodeError, TypeError):
            skipped.append("LLM returned invalid JSON")
            continue

        title = draft.get("title", "")
        problems = _title_problems(title, cfg)
        if problems:
            skipped.append(f"title rejected: {problems}")
            continue

        if title in existing_titles:
            skipped.append(f"duplicate title: {title}")
            continue

        body = draft.get("body", "")
        word_count = len(body.split())
        if word_count < min_words:
            skipped.append(f"body too short ({word_count} < {min_words} words)")
            continue

        tags = draft.get("tags", [])
        result = _publish_article({"title": title, "body": body, "tags": tags})
        published.append(result)
        existing_titles.add(title)

    return {
        "status": "done",
        "published": len(published),
        "skipped": len(skipped),
        "details": {"published": published, "skipped": skipped},
    }