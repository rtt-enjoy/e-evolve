import unittest
import os
from datetime import datetime, timedelta, timezone

import bot.earnings as earnings_module
import bot.earning.newsletter as newsletter_module
from bot.earning.newsletter import (
	_digest_problems,
	_ensure_sources,
	_generate_issue,
	_hours_until_due,
	_pick_sources,
	_record_issue,
)
from bot.earning.articles import (
	_duplicate_reason,
	_ensure_attribution,
	_fabrication_problems,
	_format_problems,
	_generate_article,
	_normalize,
	_pick_source,
	_publish_to_devto,
	_record_publish,
	_strip_fabricated_tables,
	_tone_problems,
	_too_similar_to_source,
)
from bot.earning.code_techs import _online_ai_brief, _outreach_draft, _parse_reddit_rss, _rank, _reference_sources
from bot.earning.trending import (
	_dedupe,
	_extract_article_text,
	_parse_dt,
	is_paywalled,
	is_technical,
	needs_unlock,
	normalize_title,
	unlock_summary,
)
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


class TestFabricatedTableStripping(unittest.TestCase):
	"""The shipped bug: a fabricated table was detected, then published anyway."""

	_TABLE = (
		"## Pick a Service\n\n"
		"| Service | Latency | Size |\n|--|--|--|\n"
		"| OpenAI | 200-400 ms | 175 B |\n| Anthropic | 250-500 ms | 1.3 T |\n\n"
		"Cloud APIs scale easily but cost more.\n"
	)

	def test_fabricated_table_is_removed(self):
		cleaned, removed = _strip_fabricated_tables(self._TABLE)
		self.assertEqual(removed, 1)
		self.assertNotIn("Anthropic", cleaned)
		self.assertEqual(_fabrication_problems(cleaned), [])

	def test_surrounding_prose_survives(self):
		cleaned, _ = _strip_fabricated_tables(self._TABLE)
		self.assertIn("## Pick a Service", cleaned)
		self.assertIn("Cloud APIs scale easily", cleaned)

	def test_no_heading_collision_after_removal(self):
		cleaned, _ = _strip_fabricated_tables(self._TABLE)
		self.assertNotRegex(cleaned, r"## Pick a Service\nCloud APIs")

	def test_qualitative_table_is_kept(self):
		body = (
			"| Approach | Tradeoff | When to Use |\n|--|--|--|\n"
			"| Cloud API | Costs more | Fast iteration |\n"
			"| Local model | Needs a GPU | Private data |\n"
		)
		cleaned, removed = _strip_fabricated_tables(body)
		self.assertEqual(removed, 0)
		self.assertEqual(cleaned, body)

	def test_prose_containing_pipe_is_not_treated_as_table(self):
		body = "Run `a | b` in bash.\n\nThat pipes output.\n"
		cleaned, removed = _strip_fabricated_tables(body)
		self.assertEqual(removed, 0)
		self.assertIn("Run `a | b`", cleaned)

	def test_fabrication_in_prose_blocks_publishing(self):
		# Not fixable by deleting a table, so _generate_article must bail.
		class FakeLLM:
			def complete_json(self, prompt, system=None, max_tokens=None):
				return {
					"title": "A Totally Different Angle On Model Routing",
					"description": "d",
					"body_markdown": (
						"Intro paragraph here.\n\n## One\n\nThe model responds in "
						"200 ms on average.\n\n## Two\n\n```python\nx = 1\n```\n\n"
						"## Three\n\n```bash\nls\n```\n\n## Key Takeaways\n\n- a\n"
					),
					"tags": ["python"],
				}
		import bot.earning.articles as articles_module
		original = articles_module._pick_source
		try:
			articles_module._pick_source = lambda status: {
				"title": "Some Source Article About Things", "url": "https://ex.com/a",
				"source": "medium:python", "summary": "s",
			}
			self.assertIsNone(_generate_article(FakeLLM(), {}))
		finally:
			articles_module._pick_source = original


class TestMarkdownNormalization(unittest.TestCase):
	def test_numbered_headings_are_unnumbered(self):
		out = _normalize({"body_markdown": "## 1. First\n\ntext\n\n### 2) Second\n\nmore"})
		self.assertIn("## First", out["body_markdown"])
		self.assertIn("### Second", out["body_markdown"])
		self.assertNotIn("1.", out["body_markdown"])

	def test_blank_line_inserted_after_heading(self):
		out = _normalize({"body_markdown": "## Heading\nParagraph right after."})
		self.assertIn("## Heading\n\nParagraph", out["body_markdown"])

	def test_ordered_list_numbering_preserved(self):
		# Only headings get unnumbered; real ordered lists must survive.
		out = _normalize({"body_markdown": "## Steps\n\n1. First step\n2. Second step"})
		self.assertIn("1. First step", out["body_markdown"])

	def test_top_level_heading_demoted(self):
		out = _normalize({"body_markdown": "# Title\n\ntext"})
		self.assertIn("## Title", out["body_markdown"])
		self.assertNotRegex(out["body_markdown"], r"^# ")


class TestToneChecks(unittest.TestCase):
	"""The owner asked for a clear, clean, friendly tone. Enforce it mechanically."""

	def test_hype_language_flagged(self):
		self.assertTrue(_tone_problems("This revolutionary tool changes everything."))

	def test_condescending_just_flagged(self):
		self.assertIn('condescending "simply/just"', _tone_problems("Simply run the script."))

	def test_corporate_jargon_flagged(self):
		self.assertIn("corporate jargon", _tone_problems("We utilize a cache here."))

	def test_cliche_opener_flagged(self):
		self.assertTrue(_tone_problems("In today's fast-paced world, speed matters."))

	def test_exclamation_flagged(self):
		self.assertIn("exclamation mark", _tone_problems("It works great!"))

	def test_long_sentences_flagged(self):
		long_one = " ".join(["word"] * 40) + ". " + " ".join(["word"] * 40) + "."
		self.assertTrue(any("too long" in p for p in _tone_problems(long_one)))

	def test_clean_friendly_prose_passes(self):
		body = (
			"You probably hit this when your cache grows past memory. "
			"I ran into it last month. The fix is small, and it holds up well.\n\n"
			"Here is what changed. The reader can follow each step."
		)
		self.assertEqual(_tone_problems(body), [])

	def test_code_blocks_exempt_from_tone_rules(self):
		self.assertEqual(_tone_problems("```python\nprint('just do it!')\n```"), [])

	def test_stacked_headings_flagged(self):
		problems = _format_problems("## One\n\n## Two\n\ntext")
		self.assertIn("stacked headings with no prose between them", problems)


class TestFreediumUnlock(unittest.TestCase):
	def test_medium_host_detected_as_paywalled(self):
		self.assertTrue(is_paywalled("https://medium.com/@a/post-123"))
		self.assertTrue(is_paywalled("https://towardsdatascience.com/x"))

	def test_open_host_not_paywalled(self):
		self.assertFalse(is_paywalled("https://dev.to/a/b"))
		self.assertFalse(is_paywalled("https://github.blog/x"))

	def test_lookalike_host_not_paywalled(self):
		# Guard against suffix spoofing: notmedium.com must not match medium.com.
		self.assertFalse(is_paywalled("https://notmedium.com/x"))

	def test_thin_paywalled_summary_needs_unlock(self):
		self.assertTrue(needs_unlock({"url": "https://medium.com/x", "summary": "Teaser."}))

	def test_rich_summary_needs_no_unlock(self):
		self.assertFalse(needs_unlock({"url": "https://medium.com/x", "summary": "x" * 900}))

	def test_extracts_paragraphs_with_breaks(self):
		html = "<article><p>First para.</p><p>Second para.</p></article>"
		self.assertEqual(_extract_article_text(html), "First para.\n\nSecond para.")

	def test_strips_scripts_and_nav(self):
		html = "<article><script>evil()</script><nav>Menu</nav><p>Real text.</p></article>"
		text = _extract_article_text(html)
		self.assertNotIn("evil", text)
		self.assertNotIn("Menu", text)
		self.assertIn("Real text.", text)

	def test_unlock_failure_returns_original_summary(self):
		import bot.earning.trending as trending_module
		original = trending_module.requests.get
		try:
			def boom(*args, **kwargs):
				raise RuntimeError("mirror down")
			trending_module.requests.get = boom
			item = {"url": "https://medium.com/x", "summary": "Teaser."}
			self.assertEqual(unlock_summary(item), "Teaser.")
		finally:
			trending_module.requests.get = original

	def test_unlock_rejects_body_thinner_than_existing(self):
		import bot.earning.trending as trending_module

		class FakeResp:
			status_code = 200
			text = "<article><p>tiny</p></article>"

		original = trending_module.requests.get
		try:
			trending_module.requests.get = lambda *a, **k: FakeResp()
			item = {"url": "https://medium.com/x", "summary": "Teaser."}
			self.assertEqual(unlock_summary(item), "Teaser.")
		finally:
			trending_module.requests.get = original


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

class TestNewsletterDigest(unittest.TestCase):
	"""The digest must never repeat a story or invent one."""

	def _cfg(self, **over):
		cfg = dict(newsletter_module._DEFAULTS)
		cfg.update(over)
		return cfg

	def _items(self, n, start=0):
		return [
			{"title": f"Some Real Tech Story Number {i}",
			 "url": f"https://example.com/post/{i}",
			 "source": "feed", "summary": "x" * 500}
			for i in range(start, start + n)
		]

	def test_no_llm_publishes_nothing(self):
		# Regression guard: never emit a fallback issue when the LLM is absent.
		self.assertIsNone(_generate_issue(None, {}, self._cfg()))

	def test_too_few_fresh_items_publishes_nothing(self):
		# The anti-duplicate-flood guard: a thin digest is worse than none.
		original = newsletter_module.trending.fetch_candidates
		try:
			newsletter_module.trending.fetch_candidates = lambda **kw: self._items(2)
			self.assertIsNone(_generate_issue(object(), {}, self._cfg(min_items=4)))
		finally:
			newsletter_module.trending.fetch_candidates = original

	def test_featured_item_not_reused(self):
		status = {}
		_record_issue(status, self._items(3), 200)
		original = newsletter_module.trending.fetch_candidates
		try:
			# Same three stories come back next week; none may be picked again.
			newsletter_module.trending.fetch_candidates = lambda **kw: self._items(3)
			self.assertEqual(_pick_sources(status, self._cfg()), [])
		finally:
			newsletter_module.trending.fetch_candidates = original

	def test_fresh_items_still_selected_after_history(self):
		status = {}
		_record_issue(status, self._items(3), 200)
		original = newsletter_module.trending.fetch_candidates
		try:
			newsletter_module.trending.fetch_candidates = lambda **kw: self._items(6)
			picked = _pick_sources(status, self._cfg())
			self.assertEqual(len(picked), 3)  # the 3 unseen ones
		finally:
			newsletter_module.trending.fetch_candidates = original

	def test_duplicate_within_one_fetch_picked_once(self):
		original = newsletter_module.trending.fetch_candidates
		try:
			dupes = self._items(1) * 3
			newsletter_module.trending.fetch_candidates = lambda **kw: dupes
			self.assertEqual(len(_pick_sources({}, self._cfg())), 1)
		finally:
			newsletter_module.trending.fetch_candidates = original

	def test_history_is_bounded(self):
		status = {}
		for i in range(300):
			_record_issue(status, self._items(1, start=i), 200)
		self.assertLessEqual(len(status["newsletter_history"]["source_urls"]), 200)

	def test_fetch_failure_survives(self):
		original = newsletter_module.trending.fetch_candidates
		try:
			def boom(**kwargs):
				raise RuntimeError("network down")
			newsletter_module.trending.fetch_candidates = boom
			self.assertEqual(_pick_sources({}, self._cfg()), [])
		finally:
			newsletter_module.trending.fetch_candidates = original

	def test_missing_source_link_flagged(self):
		items = self._items(4)
		body = "## One\n\ntext\n\n## Two\n\ntext\n\n## Three\n\ntext\n\n## Four\n\ntext"
		problems = _digest_problems(body, items, self._cfg(min_words=1))
		self.assertTrue(any("source link" in p for p in problems))

	def test_missing_source_link_is_repaired(self):
		items = self._items(2)
		repaired = _ensure_sources("## One\n\ntext", items)
		for item in items:
			self.assertIn(item["url"], repaired)

	def test_present_source_links_not_duplicated(self):
		items = self._items(1)
		body = f"## One\n\nSource: [t]({items[0]['url']})"
		self.assertEqual(_ensure_sources(body, items), body)

	def test_too_few_sections_flagged(self):
		problems = _digest_problems("## Only One\n\ntext", [], self._cfg(min_words=1))
		self.assertTrue(any("'##' sections" in p for p in problems))

	def test_fabricated_numbers_flagged(self):
		body = ("## One\n\nIt responds in 45ms.\n\n## Two\n\nt\n\n"
				"## Three\n\nt\n\n## Four\n\nt")
		problems = _digest_problems(body, [], self._cfg(min_words=1))
		self.assertTrue(any("latency" in p for p in problems))

	def test_cadence_blocks_early_republish(self):
		recent = datetime.now(timezone.utc).isoformat()
		self.assertGreater(_hours_until_due({"published_at": recent}, 168), 0)

	def test_cadence_allows_when_due(self):
		old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
		self.assertEqual(_hours_until_due({"published_at": old}, 168), 0.0)

	def test_unparseable_stamp_does_not_wedge_module(self):
		self.assertEqual(_hours_until_due({"published_at": "not-a-date"}, 168), 0.0)

	def test_first_run_is_due_immediately(self):
		self.assertEqual(_hours_until_due({}, 168), 0.0)

	def test_missing_devto_key_skips_silently(self):
		original = os.environ.pop("DEV_TO_API_KEY", None)
		try:
			self.assertEqual(newsletter_module.run(object(), {}), [])
		finally:
			if original is not None:
				os.environ["DEV_TO_API_KEY"] = original

	def test_newsletter_never_counts_as_revenue(self):
		# Mirrors the articles revenue guard: publishing is reach, not income.
		status = {"earnings": {"total_usd": 0.0, "this_week_usd": 0.0,
								"last_cycle_usd": 0.0, "week_started": None,
								"breakdown": {}}}
		updated = update(status, [{
			"platform": "dev.to-newsletter", "success": True,
			"title": "Weekly Digest", "url": "https://dev.to/x",
			"item_count": 7, "estimated_usd": 0.0,
		}])
		self.assertEqual(updated["earnings"]["total_usd"], 0.0)
		self.assertEqual(updated["earnings"]["confirmed_usd"], 0.0)


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

class TestWalletEarnings(unittest.TestCase):
	"""Only confirmed on-chain USDT counts as earned money."""

	def _run(self, balances):
		import os
		import bot.status as status_module
		original_fetch = status_module._fetch_usdt_balance
		original_env = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
		queue = list(balances)
		status_module._fetch_usdt_balance = lambda addr: queue.pop(0)
		try:
			status = status_module._defaults()
			for _ in balances:
				status_module._snapshot_wallet(status)
				update(status, [])
			return status
		finally:
			status_module._fetch_usdt_balance = original_fetch
			if original_env is None:
				os.environ.pop("USDT_WALLET_ADDRESS", None)
			else:
				os.environ["USDT_WALLET_ADDRESS"] = original_env

	def test_articles_never_count_as_revenue(self):
		"""dev.to pays nothing, so publishing must not move the earned figure."""
		status = {"earnings": {}, "wallet": {"confirmed_usd": 0.0}}
		updated = update(status, [
			{"platform": "dev.to", "success": True, "estimated_usd": 0.0},
			{"platform": "dev.to", "success": True, "estimated_usd": 0.0},
		])
		self.assertEqual(updated["earnings"]["confirmed_usd"], 0.0)
		self.assertEqual(updated["earnings"]["received_total_usd"], 0.0)
		self.assertEqual(updated["earnings"]["history"], [])

	def test_deposit_is_counted_once(self):
		status = self._run([0.0, 5.0, 5.0, 5.0])
		self.assertEqual(status["wallet"]["received_total_usd"], 5.0)
		self.assertEqual(status["earnings"]["history"], [5.0])

	def test_manual_withdrawal_does_not_double_count(self):
		"""Balance 5 -> 2 (owner withdrew) -> 9 is $4 of new income, not $7."""
		status = self._run([0.0, 5.0, 2.0, 9.0])
		self.assertEqual(status["wallet"]["received_total_usd"], 9.0)
		self.assertEqual(status["wallet"]["last_received_usd"], 4.0)

	def test_failed_lookup_keeps_balance_and_adds_no_income(self):
		"""A chain outage must not invent a repeat receipt."""
		status = self._run([0.0, 5.0, None, None])
		wallet = status["wallet"]
		self.assertTrue(wallet["stale"])
		self.assertEqual(wallet["confirmed_usd"], 5.0)
		self.assertEqual(wallet["received_total_usd"], 5.0)
		self.assertEqual(wallet["last_received_usd"], 0.0)
		self.assertEqual(status["earnings"]["history"], [5.0])

	def test_raw_address_never_persisted(self):
		import json
		import bot.status as status_module
		status = self._run([0.0, 1.0])
		blob = json.dumps(status_module.sanitize_for_git(status))
		self.assertNotIn("TFTNsfyomKrnUutRjBTGVULp19ByW29KbY", blob)
		self.assertIn("TFTNsf", blob)  # masked form survives


class TestOpenRouterModelChains(unittest.TestCase):
	"""Free-model chains must be role-aware and fully walked on failure."""

	def _chains(self):
		import bot.llm as llm_module
		chains = dict(llm_module._OPENROUTER_MODELS_BY_ROLE)
		chains["_default"] = llm_module._OPENROUTER_MODELS
		return chains

	def test_ox_alpha_leads_every_chain(self):
		for role, chain in self._chains().items():
			self.assertEqual(chain[0], "stealth/ox-alpha", role)

	def test_every_role_has_a_multi_model_chain(self):
		"""A single-model chain has nothing to fall back to on a rate limit."""
		import bot.llm as llm_module
		for role in ("upgrade", "research", "post"):
			chain = llm_module._OPENROUTER_MODELS_BY_ROLE[role]
			self.assertGreaterEqual(len(chain), 3, role)
			self.assertEqual(len(chain), len(set(chain)), f"{role} has duplicates")
			# auto-router last: it always resolves to *some* free model
			self.assertEqual(chain[-1], "openrouter/free", role)

	def test_all_chain_models_are_free_tier(self):
		"""A paid model in the chain would fail outright without credits."""
		for role, chain in self._chains().items():
			for model in chain:
				self.assertTrue(
					model.endswith(":free")
					or model in ("openrouter/free", "stealth/ox-alpha"),
					f"{role}: {model} is not a free-tier slug",
				)

	def _walk(self, role, error):
		"""Run a role's chain with every call failing; return models attempted."""
		import bot.llm as llm_module
		tried: list[str] = []

		def fake(self, prompt, system, max_tokens, temperature, model):
			tried.append(model)
			raise RuntimeError(error)

		real_call, real_sleep = llm_module.LLMClient._call_openrouter, llm_module.time.sleep
		keys = ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "CEREBRAS_API_KEY")
		saved = {k: os.environ.pop(k, None) for k in keys}
		saved_or = os.environ.get("OPENROUTER_API_KEY")
		os.environ["OPENROUTER_API_KEY"] = "test-key"
		llm_module.LLMClient._call_openrouter = fake
		llm_module.time.sleep = lambda *a, **kw: None
		try:
			client = llm_module.LLMClient()
			with self.assertRaises(RuntimeError):
				client.complete_for_role(role, "hi")
		finally:
			llm_module.LLMClient._call_openrouter = real_call
			llm_module.time.sleep = real_sleep
			for k, v in saved.items():
				if v is not None:
					os.environ[k] = v
			if saved_or is None:
				os.environ.pop("OPENROUTER_API_KEY", None)
			else:
				os.environ["OPENROUTER_API_KEY"] = saved_or

		ordered: list[str] = []
		for model in tried:
			if not ordered or ordered[-1] != model:
				ordered.append(model)
		return ordered

	def test_rate_limit_steps_through_entire_chain(self):
		"""Regression: step-downs must not consume the per-model retry budget."""
		import bot.llm as llm_module
		for role in ("upgrade", "research", "post"):
			walked = self._walk(role, "429 rate_limit_exceeded from openrouter")
			self.assertEqual(walked, llm_module._OPENROUTER_MODELS_BY_ROLE[role], role)

	def test_withdrawn_model_falls_through_to_next(self):
		"""Stealth previews can vanish; a 404 must not strand the chain."""
		import bot.llm as llm_module
		walked = self._walk("post", "model_not_found on openrouter: stealth/ox-alpha")
		self.assertEqual(walked, llm_module._OPENROUTER_MODELS_BY_ROLE["post"])


if __name__ == "__main__":
	unittest.main()
