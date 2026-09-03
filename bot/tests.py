import unittest

class TestReviseTitleAndFormat(unittest.TestCase):
    """Unit tests for the title and format revision helpers used inside _finalize."""

    def test_revise_title_returns_better_title(self):
        llm = unittest.mock.MagicMock()
        llm.complete_json.return_value = {"title": "A Better Title"}
        data = {"title": "A Bad Title", "body_markdown": "Some body text here."}
        result = _revise_title(llm, data, ["title too long"])
        self.assertEqual(result, "A Better Title")
        llm.complete_json.assert_called_once()

    def test_revise_title_returns_none_on_empty_response(self):
        llm = unittest.mock.MagicMock()
        llm.complete_json.return_value = {}
        data = {"title": "A Bad Title", "body_markdown": "Some body text here."}
        result = _revise_title(llm, data, ["title too long"])
        self.assertIsNone(result)

    def test_revise_title_returns_none_on_llm_failure(self):
        llm = unittest.mock.MagicMock()
        llm.complete_json.side_effect = Exception("LLM error")
        data = {"title": "A Bad Title", "body_markdown": "Some body text here."}
        result = _revise_title(llm, data, ["title too long"])
        self.assertIsNone(result)

    def test_revise_title_returns_none_when_still_weak(self):
        llm = unittest.mock.MagicMock()
        llm.complete_json.return_value = {"title": "A Bad Title"}
        data = {"title": "A Bad Title", "body_markdown": "Some body text here."}
        result = _revise_title(llm, data, ["title too long"])
        self.assertIsNone(result)

    def test_revise_format_returns_revised_article(self):
        llm = unittest.mock.MagicMock()
        llm.complete_json.return_value = {
            "body_markdown": "## Fixed section\n\nSome text.",
            "title": "Original Title",
            "description": "A description",
            "tags": ["python"],
        }
        data = {"title": "Original Title", "body_markdown": "old body", "description": "A description", "tags": ["python"]}
        result = _revise_format(llm, data, ["too short"])
        self.assertIsNotNone(result)
        self.assertEqual(result["body_markdown"], "## Fixed section\n\nSome text.")
        self.assertEqual(result["title"], "Original Title")

    def test_revise_format_returns_none_on_empty_body(self):
        llm = unittest.mock.MagicMock()
        llm.complete_json.return_value = {"body_markdown": ""}
        data = {"title": "Title", "body_markdown": "old body"}
        result = _revise_format(llm, data, ["too short"])
        self.assertIsNone(result)

    def test_revise_format_returns_none_on_no_improvement(self):
        llm = unittest.mock.MagicMock()
        llm.complete_json.return_value = {
            "body_markdown": "old body",
            "title": "Title",
            "description": "A description",
            "tags": ["python"],
        }
        data = {"title": "Title", "body_markdown": "old body", "description": "A description", "tags": ["python"]}
        result = _revise_format(llm, data, ["too short"])
        self.assertIsNone(result)

    def test_revise_format_returns_none_on_llm_failure(self):
        llm = unittest.mock.MagicMock()
        llm.complete_json.side_effect = Exception("LLM error")
        data = {"title": "Title", "body_markdown": "old body"}
        result = _revise_format(llm, data, ["too short"])
        self.assertIsNone(result)

    def test_revise_format_preserves_title_description_tags(self):
        llm = unittest.mock.MagicMock()
        llm.complete_json.return_value = {
            "body_markdown": "## New section\n\nContent.",
        }
        data = {"title": "Keep This Title", "body_markdown": "old", "description": "Keep Desc", "tags": ["python"]}
        result = _revise_format(llm, data, ["too short"])
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Keep This Title")
        self.assertEqual(result["description"], "Keep Desc")
        self.assertEqual(result["tags"], ["python"])