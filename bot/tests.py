import unittest
import os
from datetime import datetime, timezone

import bot.earnings as earnings_module
from bot.earning.articles import _fallback_article, _publish_to_devto
from bot.earning.code_techs import _outreach_draft, _parse_reddit_rss, _rank
from bot.earnings import update

class TestArticleFallback(unittest.TestCase):
    def test_fallback_structure(self):
        status = {"total_runs": 5}
        article = _fallback_article("test topic", status, "LLM error")
        self.assertIn("title", article)
        self.assertIn("description", article)
        self.assertIn("body_markdown", article)
        self.assertIsInstance(article["tags"], list)
        self.assertTrue(article["title"].startswith("When Your Content Bot"))

    def test_publish_to_devto_no_key(self):
        # Ensure graceful handling when API key is missing
        result = _publish_to_devto({"title": "x", "body_markdown": "y"}, "")
        self.assertFalse(result["success"])
        self.assertIn("error", result)

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

if __name__ == "__main__":
    unittest.main()
