import unittest
import os
from datetime import datetime, timezone

from bot.earning.articles import _fallback_article, _publish_to_devto
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
    def setUp(self):
        # Reset earnings file to avoid side effects
        self.log_path = "earnings-log.md"
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def test_week_reset(self):
        status = {"earnings": {"total_usd": 10.0, "this_week_usd": 2.0, "last_cycle_usd": 0.0, "week_started": None, "breakdown": {}}}
        # Simulate a Monday transition by mocking datetime
        original_dt = datetime
        class Mocked(datetime):
            @classmethod
            def now(cls, tz=None):
                # Return a date that is a Monday
                return original_dt(2026, 5, 20, tzinfo=timezone.utc)
        datetime_backup = datetime
        try:
            globals()["datetime"] = Mocked
            updated = update(status, [{"platform": "dev.to", "success": True, "estimated_usd": 0.08}])
            earnings = updated["earnings"]
            self.assertEqual(earnings["this_week_usd"], 0.08)  # reset then add current cycle
        finally:
            globals()["datetime"] = datetime_backup

if __name__ == "__main__":
    unittest.main()