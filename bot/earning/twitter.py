"""
Earning Module — Twitter / X Threads
Generates and posts developer threads to build audience.

Activates with: TWITTER_API_KEY  TWITTER_API_SECRET
                TWITTER_ACCESS_TOKEN  TWITTER_ACCESS_SECRET
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)

def _load_strategy() -> dict:
    try:
        return json.loads(Path("config/strategy.json").read_text())
    except Exception:
        return {}

_strategy   = _load_strategy().get("twitter", {})
_MIN_TWEETS = int(_strategy.get("min_tweets", 5))
_MAX_TWEETS = int(_strategy.get("max_tweets", 7))
_BUYER_INTENT_TOPICS = [
    str(item).strip()
    for item in _strategy.get("buyer_intent_topics", [])
    if str(item).strip()
]

_REQUIRED = [
    "TWITTER_API_KEY", "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET",
]

_SYSTEM = (
    "You are a developer influencer writing high-value Twitter/X threads.\n"
    "Teach something genuinely useful in a concise, engaging way.\n\n"
    "Respond with ONLY a single JSON object.\n\n"
    'Schema:\n{\n  "topic": "one-line description",\n  "tweets": [\n'
    '    "Tweet 1 text (hook — bold claim or number, max 265 chars)",\n'
    '    "Tweet 2...",\n    ...\n  ]\n}\n\n'
    "Rules:\n"
    f"- {_MIN_TWEETS} to {_MAX_TWEETS} tweets total\n"
    "- Tweet 1: compelling hook\n"
    "- Last tweet: clear CTA (follow / share / reply)\n"
    "- Max 2 hashtags in the whole thread\n"
    "- Each tweet under 265 characters\n"
    "- Topics: Python, AI/LLMs, GitHub Actions, automation, SaaS affiliate content,"
    " digital products, newsletters, productized services, passive income via code\n"
    "- Keep monetization practical: show a useful workflow first, then invite a reply,"
    " follow, or CTA. No income guarantees."
)

_TOPICS = [
    "I built a bot that writes articles while I sleep — full setup",
    "GitHub Actions is a free cloud computer — 8 things you can run for $0",
    "How to make your Python scripts self-improve with free LLMs",
    "5 automation ideas that actually earn (with real numbers)",
    "The cheapest way to run an AI agent 24/7 in 2025",
    "Web3 Python: from zero to daily automated NFT mints",
    "Zero-server side projects — what's really possible on GitHub free tier",
    "AI automation tool comparisons that attract buyers instead of tourists",
    "How to turn one useful script into a tiny digital product",
    "A developer newsletter funnel that starts with GitHub Actions",
    "SaaS affiliate content for engineers who hate fake reviews",
    "How short-form automation demos become durable technical articles",
    "Productized automation services: from recurring bug to recurring revenue",
]


@dataclass
class Result:
    platform: str = "twitter"
    topic: str = ""
    thread_length: int = 0
    url: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    estimated_usd: float = 0.0


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    if not all(os.getenv(k, "").strip() for k in _REQUIRED):
        log.debug("[twitter] Missing keys — skipping")
        return []

    thread = _generate(llm, status)
    if not thread:
        return []

    result = _post(thread["tweets"], thread.get("topic", ""))
    if result.success:
        log.info("[twitter] Posted %d-tweet thread: %s",
                 result.thread_length, result.url)
    else:
        log.warning("[twitter] Failed: %s", result.error)
    return [vars(result)]


def _generate(llm: Any, status: dict) -> Optional[dict]:
    n     = status.get("total_runs", 1)
    topic = _select_topic(int(n or 1))
    try:
        prompt = (
            f'Write a Twitter/X thread about: "{topic}"\n'
            f"Context: bot cycle #{n}, active modules: {status.get('active_features', [])}.\n"
            "Repurpose one concrete lesson from the current bot workflow; avoid vague AI hype.\n"
            "JSON only."
        )
        if hasattr(llm, "complete_json_for_role"):
            data = llm.complete_json_for_role("post", prompt, system=_SYSTEM, max_tokens=1200)
        else:
            data = llm.complete_json(prompt, system=_SYSTEM, max_tokens=1200)
        tweets = data.get("tweets", [])
        if len(tweets) < _MIN_TWEETS:
            raise ValueError(f"Too few tweets: {len(tweets)}")
        data["tweets"] = [t[:268] for t in tweets[:_MAX_TWEETS]]
        return data
    except Exception as exc:
        log.error("[twitter] Thread generation failed: %s", exc)
        return None


def _select_topic(run_number: int) -> str:
    """Favor buyer-intent topics when configured, with evergreen topics as fallback."""
    import hashlib

    if _BUYER_INTENT_TOPICS:
        bucket = int(hashlib.md5(f"twitter:{run_number}".encode()).hexdigest(), 16) % 100
        if bucket < 80:
            idx = int(hashlib.md5(str(run_number).encode()).hexdigest(), 16) % len(_BUYER_INTENT_TOPICS)
            return _BUYER_INTENT_TOPICS[idx]
    return _TOPICS[run_number % len(_TOPICS)]


def _post(tweets: list[str], topic: str) -> Result:
    try:
        import tweepy  # lazy
    except ImportError:
        return Result(error="tweepy not installed — add to requirements.txt")

    try:
        client = tweepy.Client(
            consumer_key       = os.getenv("TWITTER_API_KEY"),
            consumer_secret    = os.getenv("TWITTER_API_SECRET"),
            access_token       = os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret= os.getenv("TWITTER_ACCESS_SECRET"),
            wait_on_rate_limit = True,
        )

        prev_id:  Optional[str] = None
        first_id: Optional[str] = None
        n = len(tweets)

        for i, text in enumerate(tweets):
            body   = (f"{i+1}/{n} {text}" if i > 0 else text)[:280]
            kwargs: dict = {"text": body}
            if prev_id:
                kwargs["in_reply_to_tweet_id"] = prev_id
            resp     = client.create_tweet(**kwargs)
            tweet_id = str(resp.data["id"])
            if i == 0:
                first_id = tweet_id
            prev_id = tweet_id
            if i < n - 1:
                time.sleep(1.5)

        username = "unknown"
        try:
            me       = client.get_me()
            username = me.data.username
        except Exception:
            pass

        return Result(
            topic         = topic,
            thread_length = n,
            url           = f"https://twitter.com/{username}/status/{first_id}",
            success       = True,
            estimated_usd = 0.01,
        )
    except Exception as exc:
        return Result(topic=topic, error=str(exc)[:300])
