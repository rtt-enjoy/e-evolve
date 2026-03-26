"""
Earning Module — Twitter / X Threads
Generates and posts developer threads to build audience.

Activates with: TWITTER_API_KEY  TWITTER_API_SECRET
                TWITTER_ACCESS_TOKEN  TWITTER_ACCESS_SECRET
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Optional

log = logging.getLogger(__name__)

_REQUIRED = [
    "TWITTER_API_KEY", "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET",
]

_SYSTEM = """\
You are a developer influencer writing high-value Twitter/X threads.
Teach something genuinely useful in a concise, engaging way.

Respond with ONLY a single JSON object.

Schema:
{
  "topic": "one-line description",
  "tweets": [
    "Tweet 1 text (hook — bold claim or number, max 265 chars)",
    "Tweet 2...",
    ...
  ]
}

Rules:
- 5 to 7 tweets total
- Tweet 1: compelling hook
- Last tweet: clear CTA (follow / share / reply)
- Max 2 hashtags in the whole thread
- Each tweet under 265 characters
- Topics: Python, AI/LLMs, GitHub Actions, automation, passive income via code"""

_TOPICS = [
    "I built a bot that writes articles while I sleep — full setup",
    "GitHub Actions is a free cloud computer — 8 things you can run for $0",
    "How to make your Python scripts self-improve with free LLMs",
    "5 automation ideas that actually earn (with real numbers)",
    "The cheapest way to run an AI agent 24/7 in 2025",
    "Web3 Python: from zero to daily automated NFT mints",
    "Zero-server side projects — what's really possible on GitHub free tier",
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
    topic = _TOPICS[n % len(_TOPICS)]
    try:
        data   = llm.complete_json(
            f'Write a Twitter/X thread about: "{topic}"\n'
            f"Context: bot cycle #{n}. JSON only.",
            system=_SYSTEM,
            max_tokens=1200,
        )
        tweets = data.get("tweets", [])
        if len(tweets) < 3:
            raise ValueError(f"Too few tweets: {len(tweets)}")
        data["tweets"] = [t[:268] for t in tweets[:7]]
        return data
    except Exception as exc:
        log.error("[twitter] Thread generation failed: %s", exc)
        return None


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
