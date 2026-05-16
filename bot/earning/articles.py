def _fallback_article(topic: str, status: dict, error_type: str) -> dict:
    """Return a useful deterministic article when LLM generation is unavailable."""
    run = int(status.get("total_runs", 0) or 0)
    title = "When Your Content Bot Hits an LLM Quota, Ship the Fallback"
    description = "A practical pattern for keeping automated publishing alive when your LLM provider runs out of quota."
    body = f"""A publishing bot that depends on one LLM provider has a boring failure mode: the workflow is green, but nothing gets published. I hit that during cycle #{run}. The dev.to key was present, the command was read, and the article module simply returned no action after generation failed with `{error_type}`.

That is the kind of failure that looks harmless in CI and expensive in a content pipeline. The fix is not more optimism. The fix is a fallback path that produces a plain, useful, bounded article without calling another model.

## The Failure Mode

Most automation code treats content generation and content publishing as one step. That is convenient until the generator fails after the scheduler, secrets, and publishing client have all done their jobs.

The broken flow usually looks like this:

```python
def run(llm, status):
    article = generate_article(llm, status)
    if not article:
        return []

    return [post_to_devto(article)]
```

The empty list is the problem. It says "nothing happened" instead of "publishing was blocked by generation." Dashboards, earnings counters, and alerts then have very little to work with.

## Separate Generation From Delivery

The publishing client should not care whether an article came from an LLM, a template, or a human-reviewed draft. Give it a strict article object and keep the fallback close to the generation boundary.

```python
def generate_or_fallback(llm, status):
    try:
        article = llm.complete_json(build_prompt(status))
        validate_article(article)
        return article
    except Exception as exc:
        return fallback_article(
            topic=select_topic(status),
            reason=classify_error(exc),
            run_number=status.get("total_runs", 0),
        )
```

That keeps the delivery path boring. Boring is good here. The API call to dev.to should have one job: send a valid payload and report the URL or the HTTP error.

## Make the Fallback Honest

A fallback article should not pretend it has fresh benchmarks, citations, or provider-specific pricing. It should explain the operational lesson in front of it. In this case, the lesson is quota isolation.

```python
def fallback_article(topic, reason, run_number):
    return {{
        "title": "When Your Content Bot Hits an LLM Quota, Ship the Fallback",
        "description": "Keep automated publishing alive when generation fails.",
        "tags": ["python", "automation", "devops", "ai"],
        "body_markdown": build_markdown(topic, reason, run_number),
    }}
```

The fallback can still be useful. It can describe the failure, show the patch, and give readers a pattern they can use in their own schedulers.

## Track the Failure as a Publish Result

Do not hide the original failure. Add it to the article body, the logs, or the action metadata. The goal is graceful degradation, not self-delusion.

```python
def publish_article(article, devto_key):
    response = requests.post(
        "https://dev.to/api/articles",
        headers={{{"api-key": devto_key, "Content-Type": "application/json"}}},
        json={{{"article": {{
            "title": article["title"],
            "body_markdown": article["body_markdown"],
            "published": True,
            "tags": article["tags"],
            "description": article["description"],
        }}}}},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["url"]
```

If the post succeeds, the cycle should record a normal publish action. If the post fails, the action should contain the HTTP status and a short error body. Either way, the system tells the truth.

## The Rule I Use Now

Any unattended workflow with a public output needs a deterministic fallback for its most fragile dependency. For content bots, that dependency is usually the LLM. For data jobs, it is usually the upstream API. For deployment jobs, it is often credentials or package installation.

The fallback does not need to be fancy. It needs to be valid, bounded, and honest.

## Key Takeaways

- Treat article generation and article publishing as separate failure domains.
- Return a fallback article when LLM generation fails instead of returning an empty action list.
- Keep fallback content honest: no invented benchmarks, prices, or citations.
- Record the original error type so a successful publish does not hide provider trouble.
- Prefer deterministic recovery for unattended workflows that are expected to produce public output.

## Reproducing the Original Error

To reproduce the original error that triggered this fallback article:

1. Check the logs for the specific error message containing `{error_type}`
2. Verify that your LLM provider API key is valid and has sufficient quota
3. Test the LLM endpoint directly with a simple prompt to confirm connectivity
4. If using a custom LLM provider, check their status page for known issues

## Preventing Future Failures

To avoid hitting this fallback in future cycles:

1. Monitor your LLM provider's quota usage and set up alerts
2. Implement a multi-provider fallback strategy (already in progress for this bot)
3. Consider caching frequently requested prompts and responses
4. Batch API calls when possible to reduce quota consumption

## Next Steps

This fallback article is a temporary solution. The long-term strategy is to:

1. Implement a multi-LLM provider system that can switch automatically
2. Add a quota monitoring dashboard to track usage across providers
3. Create a content buffer that stores pre-generated articles for emergencies
4. Develop a more sophisticated error classification system to handle different failure modes appropriately
"""
    return {
        "title": title,
        "tags": ["python", "automation", "devops", "ai"],
        "description": description,
        "body_markdown": body,
    }