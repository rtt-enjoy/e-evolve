import os, json, re, logging
from pathlib import Path
from typing import Dict, Any

from ._shared import load_config

log = logging.getLogger("generate_lead_articles")

CONFIG = load_config("code_techs", {})
PROMPT_TOP_N = int(CONFIG.get("prompt_top_n", 6))
SCORE_THRESHOLD = 70

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def generate_article(lead: Dict[str, Any], llm) -> Dict[str, Any]:
    prompt = (
        "Write a dev.to article draft based on the following lead.\n"
        f"Title: {lead['title']}\n"
        f"URL: {lead['url']}\n"
        f"Source: {lead['source']}\n"
        f"Score: {lead['score']}\n"
        "Write a concise article (max 800 words) with a catchy title, a one‑sentence description, and a body in markdown.\n"
        "Include at least two fenced code blocks and a ## Key Takeaways section.\n"
        "Do not mention the lead or the bot; write as a senior engineer.\n"
        "Return JSON with keys: title, description, body_markdown, tags."
    )
    try:
        if hasattr(llm, "complete_json_for_role"):
            data = llm.complete_json_for_role("post", prompt, max_tokens=2000)
        else:
            data = llm.complete_json(prompt, max_tokens=2000)
    except Exception as e:
        log.warning("LLM generation failed: %s", e)
        return {}
    try:
        article = json.loads(data)
    except json.JSONDecodeError:
        log.warning("Failed to parse LLM response")
        return {}
    if not article.get("title") or not article.get("body_markdown"):
        return {}
    tags = ["python", "ai", "automation"]
    for tag in lead.get("labels", []):
        tags.append(tag.lower())
    tags = list(dict.fromkeys(tags))[:4]
    article.update({
        "tags": tags,
        "url": lead["url"],
        "source": lead["source"],
    })
    return article

def write_article(article: Dict[str, Any], path: Path):
    path.write_text(article["body_markdown"], encoding="utf-8")
    log.info("Wrote article draft to %s", path)

def main():
    status_path = Path("status.json")
    if not status_path.is_file():
        log.error("status.json not found")
        return
    with status_path.open(encoding="utf-8") as f:
        status = json.load(f)
    opportunities = status.get("opportunities", [])
    if not opportunities:
        log.info("No opportunities")
        return
    from . import llm  # LLM client
    llm_client = llm
    for opp in opportunities:
        if opp.get("score", 0) < SCORE_THRESHOLD:
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", opp["title"].lower()).strip("-")
        article_path = Path("docs") / f"lead_{slug}.md"
        article = generate_article(opp, llm_client)
        if article:
            write_article(article, article_path)

if __name__ == "__main__":
    main()