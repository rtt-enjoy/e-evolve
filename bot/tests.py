import unittest
import os
from datetime import datetime, timezone

import bot.earnings as earnings_module
from bot.earning.articles import (
    _duplicate_reason,
    _ensure_attribution,
    _fabrication_problems,
    _generate_article,
    _pick_source,
    _publish_to_devto,
    _record_publish,
    _too_similar_to_source,
)
from bot.earning.code_techs import _online_ai_brief, _outreach_draft, _parse_reddit_rss, _rank, _reference_sources
from bot.earning.trending import _dedupe, _parse_dt, is_technical, normalize_title
from bot.earnings import update

class TestArticleDeduplication(unittest.TestCase):
    """The duplicate-post bug: identical titles published every cycle."""

    def test_exact_duplicate_title_rejected(self):
        status = {}
        article = {"title": "Cutting LLM Costs With Model Routing", "_source": {}}
        _record_publish(status, article)
        self.assertIn("duplicate title", _duplicate_reason(article, status))

    def test_singular_plural_variant_rejected(self):
        # Stemming collapses "Costs"/"Cost" to one key, so this is caught as an
        # exact duplicate. Assert it is rejected, not which branch caught it.
        status = {}
        _record_publish(status, {"title": "Cutting LLM Costs With Model Routing", "_source": {}})
        self.assertTrue(_duplicate_reason({"title": "Cutting LLM Cost With Model Routing"}, status))

    def test_preposition_swap_rejected(self):
        # Swapping "Under" for "During" must not disguise a repeat.
        status = {}
        _record_publish(status, {
            "title": "Debugging Kubernetes Pod Evictions Under Memory Pressure",
            "_source": {},
        })
        self.assertTrue(_duplicate_reason(
            {"title": "Debugging Kubernetes Pod Evictions During Memory Pressure"}, status))

    def test_near_duplicate_with_one_extra_word_rejected(self):
        # Mostly-overlapping topical words: caught by the similarity branch.
        status = {}
        _record_publish(status, {
            "title": "Debugging Kubernetes Pod Evictions Fast",
            "_source": {},
        })
        reason = _duplicate_reason(
            {"title": "Debugging Kubernetes Pod Evictions"}, status)
        self.assertIn("near-duplicate", reason)

    def test_distinct_title_allowed(self):
        status = {}
        _record_publish(status, {"title": "Cutting LLM Costs With Model Routing", "_source": {}})
        self.assertEqual(_duplicate_reason({"title": "Debugging Kubernetes Pod Evictions"}, status), "")

    def test_already_used_source_is_not_reselected(self):
        status = {}
        _record_publish(status, {
            "title": "Some Article",
            "_source": {"url": "https://example.com/post", "title": "Original Post"},
        })
        hist = status["article_history"]
        self.assertIn("example.com/post", hist["source_urls"])
        self.assertIn(normalize_title("Original Post"), hist["source_titles"])

    def test_history_is_bounded(self):
        status = {}
        for i in range(300):
            _record_publish(status, {"title": f"Unique Article Number {i}", "_source": {}})
        self.assertLessEqual(len(status["article_history"]["titles"]), 200)

    def test_no_llm_publishes_nothing(self):
        # Regression guard: this used to return a static fallback article.
        self.assertIsNone(_generate_article(None, {}))


class TestArticleAttribution(unittest.TestCase):
    def test_source_section_added_when_model_omits_it(self):
        article = {"title": "My Take", "body_markdown": "## Body\n\nText."}
        source = {"title": "Original", "url": "https://example.com/x"}
        out = _ensure_attribution(article, source)
        self.assertIn("## Source", out["body_markdown"])
        self.assertIn("https://example.com/x", out["body_markdown"])

    def test_existing_attribution_not_duplicated(self):
        body = "## Body\n\n## Source\n\nSee [Original](https://example.com/x)."
        out = _ensure_attribution({"body_markdown": body}, {"url": "https://example.com/x"})
        self.assertEqual(out["body_markdown"].count("## Source"), 1)

    def test_title_restating_source_is_rejected(self):
        source = {"title": "Beating GPT on Retrieval With Cheaper Open Models"}
        self.assertTrue(_too_similar_to_source(
            {"title": "Beating GPT on Retrieval With Cheaper Open Models"}, source))

    def test_distinct_angle_title_accepted(self):
        source = {"title": "Beating GPT on Retrieval With Cheaper Open Models"}
        self.assertFalse(_too_similar_to_source(
            {"title": "How I Cut Our Retrieval Bill 90% Without Losing Recall"}, source))


class TestTrendingSourcing(unittest.TestCase):
    def test_non_technical_hn_story_filtered_out(self):
        self.assertFalse(is_technical(
            {"source": "hacker-news", "title": "Crime Pays but Botany Doesn't", "summary": ""}))

    def test_technical_hn_story_kept(self):
        self.assertTrue(is_technical(
            {"source": "hacker-news", "title": "Self-hosted distributed Durable Objects", "summary": ""}))

    def test_topic_scoped_feeds_bypass_keyword_filter(self):
        self.assertTrue(is_technical({"source": "medium:python", "title": "A Story", "summary": ""}))

    def test_dedupe_collapses_tracking_params_and_case(self):
        items = [
            {"title": "A Great Engineering Post", "url": "https://ex.com/a?utm_source=rss"},
            {"title": "A Great Engineering Post!", "url": "https://www.ex.com/a/"},
        ]
        self.assertEqual(len(_dedupe(items)), 1)

    def test_parses_rfc822_pubdate(self):
        self.assertIsNotNone(_parse_dt("Wed, 05 Aug 2026 10:00:00 GMT"))

    def test_parses_iso_date(self):
        self.assertIsNotNone(_parse_dt("2026-08-05T10:00:00Z"))

    def test_pick_source_survives_network_failure(self):
        import bot.earning.articles as articles_module
        original = articles_module.trending.fetch_candidates
        try:
            def boom(**kwargs):
                raise RuntimeError("network down")
            articles_module.trending.fetch_candidates = boom
            self.assertIsNone(_pick_source({}))
        finally:
            articles_module.trending.fetch_candidates = original


class TestFabricationDetection(unittest.TestCase):
    """The model invents spec tables; _SYSTEM forbids it, so catch it mechanically."""

    def test_invented_latency_and_param_table_flagged(self):
        body = "| Service | Latency | Size |\n|--|--|--|\n| OpenAI | 200-400 ms | 175 B |"
        self.assertTrue(_fabrication_problems(body))

    def test_invented_pricing_flagged(self):
        self.assertIn("invented pricing", _fabrication_problems("It costs $0.50 per million tokens."))

    def test_invented_throughput_flagged(self):
        self.assertIn("invented throughput", _fabrication_problems("It handles 1200 tokens/s."))

    def test_invented_benchmark_delta_flagged(self):
        self.assertIn("invented benchmark deltas", _fabrication_problems("It is 40% faster than before."))

    def test_qualitative_comparison_allowed(self):
        body = "Cloud APIs are noticeably faster; check the provider docs for current pricing."
        self.assertEqual(_fabrication_problems(body), [])

    def test_numbers_inside_code_blocks_allowed(self):
        body = "Set a timeout:\n\n```python\nrequests.get(url, timeout=30)\n```\n\nRetry 3 times."
        self.assertEqual(_fabrication_problems(body), [])

    def test_numbers_inside_inline_code_allowed(self):
        self.assertEqual(_fabrication_problems("Use `max_tokens=6000` and `timeout=30`."), [])

    def test_versions_and_years_allowed(self):
        self.assertEqual(_fabrication_problems("Python 3.14 shipped in 2025."), [])


class TestArticlePublishing(unittest.TestCase):
    def test_publish_to_devto_no_key(self):
        # Ensure graceful handling when API key is missing
        result = _publish_to_devto({"title": "x", "body_markdown": "y"}, "")
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_internal_source_key_never_sent_to_devto(self):
        import bot.earning.articles as articles_module
        captured = {}

        class FakeResp:
            status_code = 201
            def raise_for_status(self): pass
            def json(self): return {"url": "https://dev.to/x"}

        original = articles_module.requests.post
        try:
            def fake_post(url, headers=None, json=None, timeout=None):
                captured.update(json or {})
                return FakeResp()
            articles_module.requests.post = fake_post
            _publish_to_devto(
                {"title": "t", "body_markdown": "b", "_source": {"url": "https://ex.com"}},
                "key",
            )
        finally:
            articles_module.requests.post = original

        self.assertNotIn("_source", captured.get("article", {}))

class TestEarningsUpdate(unittest.TestCase):
    def test_week_reset(self):
        status = {"earnings": {"total_usd": 10.0, "this_week_usd": 2.0, "last_cycle_usd": 0.0, "week_started": "2026-05-11", "breakdown": {}}}
        # Simulate a Monday transition by mocking datetime
        original_dt = datetime
        class Mocked(datetime):
            @classmethod
            def now(cls, tz=None):
                # Return a date that is a Monday
                return original_dt(2026, 5, 20, tzinfo=timezone.utc)
        datetime_backup = earnings_module.datetime
        append_backup = earnings_module._append_weekly_history
        try:
            earnings_module.datetime = Mocked
            earnings_module._append_weekly_history = lambda *args, **kwargs: None
            updated = update(status, [{"platform": "dev.to", "success": True, "estimated_usd": 0.08}])
            earnings = updated["earnings"]
            self.assertEqual(earnings["this_week_usd"], 0.08)  # reset then add current cycle
        finally:
            earnings_module.datetime = datetime_backup
            earnings_module._append_weekly_history = append_backup

class TestCodeTechOpportunities(unittest.TestCase):
    def test_rank_builds_codex_prompt_and_outreach_draft(self):
        cfg = {
            "daily_target_usd": 10.0,
            "outreach": {
                "enabled": True,
                "default_price_usd": 12.0,
                "payment_label": "crypto",
                "crypto_address_env": "NO_SUCH_TEST_ADDRESS",
                "fallback_payment_note": "Add payment address before sending.",
            },
        }
        leads = [{
            "title": "Need a script to automate CSV export",
            "url": "https://example.com/request",
            "source": "community",
            "body": "Looking for a simple tool to export and convert a CSV every week.",
            "labels": ["community-request"],
        }]

        ranked = _rank(leads, cfg, max_items=1, min_score=0)

        self.assertEqual(len(ranked), 1)
        self.assertIn("Implement a small, verifiable solution", ranked[0].codex_prompt)
        self.assertIn("fixed price is $12.00", ranked[0].outreach_draft)
        self.assertIn("Do not post externally", ranked[0].codex_prompt)

    def test_outreach_uses_configured_public_payment_address(self):
        os.environ["TEST_PUBLIC_WALLET"] = "0xabc123"
        try:
            draft = _outreach_draft(
                "Small app request",
                {"url": "https://example.com", "source": "community"},
                15.0,
                {
                    "outreach": {
                        "enabled": True,
                        "payment_label": "crypto",
                        "crypto_address_env": "TEST_PUBLIC_WALLET",
                    }
                },
            )
        finally:
            os.environ.pop("TEST_PUBLIC_WALLET", None)

        self.assertIn("0xabc123", draft)
        self.assertIn("$15.00", draft)

    def test_parse_reddit_rss_builds_community_lead(self):
        feed = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <title>Need a script to automate invoices</title>
            <link href="https://www.reddit.com/r/smallbusiness/comments/abc/request/" />
            <content type="html">&lt;p&gt;Looking for a simple export tool.&lt;/p&gt;</content>
          </entry>
        </feed>"""

        leads = _parse_reddit_rss(feed, "smallbusiness")

        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["source"], "reddit:r/smallbusiness")
        self.assertIn("reddit", leads[0]["labels"])
        self.assertIn("simple export tool", leads[0]["body"])

    def test_online_ai_brief_has_local_fallback_without_llm(self):
        brief = _online_ai_brief(None, [], {"remote_service_niches": ["AI workflow consulting"]})

        self.assertIn("No LLM client", brief["summary"])
        self.assertTrue(brief["owner_actions"])

    def test_reference_sources_keeps_article_takeaway(self):
        refs = _reference_sources({
            "reference_sources": [{
                "title": "15 High-Paying Remote Jobs With a 4-Hour Work Week",
                "url": "https://example.com/article",
                "takeaway": "Use leverage instead of hourly labor.",
            }]
        })

        self.assertEqual(len(refs), 1)
        self.assertIn("leverage", refs[0]["takeaway"])

if __name__ == "__main__":
    unittest.main()
