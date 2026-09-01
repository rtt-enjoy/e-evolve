import unittest
import os
import time
import json
import bot.llm as llm_module
from datetime import datetime, timedelta, timezone

import bot.earnings as earnings_module
import bot.earning.newsletter as newsletter_module
from bot.earning.newsletter import (
	_digest_problems,
	_ensure_sources,
	_generate_issue,
	_pick_sources,
	_record_issue,
)
import bot.earning.devto as devto_module
import bot.earning._shared as shared
from bot.earning._shared import hours_until_due
from bot.earning.articles import (
	_boost_tags,
	_duplicate_reason,
	_ensure_attribution,
	_ensure_backlink,
	_format_problems,
	_followup_target,
	_generate_article,
	_pick_source,
	_record_publish,
	_title_problems,
	_titles_overlap,
	_too_similar_to_source,
)
from bot.earning.devto import (
	fabrication_problems as _fabrication_problems,
	normalize as _normalize,
	publish as _publish_to_devto,
	strip_fabricated_tables as _strip_fabricated_tables,
	tone_problems as _tone_problems,
)
import bot.earning.articles as articles_module
import bot.earning.trending as trending_module
import bot.earning.devto_stats as devto_stats
import bot.earning.mrr_ideas as mrr_module
import bot.evolution as evolution_module
from bot.evolution import (
	_apply_changes as _evo_apply_changes,
	_is_safe as _evo_is_safe,
)
from pathlib import Path
from bot.earning.mrr_ideas import (
	_record_refresh,
	_triage,
	_viability_brief,
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

	def test_curated_feeds_bypass_keyword_filter(self):
		# InfoQ, the Go blog and friends are edited, so their scoping is trusted.
		self.assertTrue(is_technical({"source": "infoq", "title": "A Story", "summary": ""}))

	def test_open_submission_feeds_are_screened(self):
		# Medium tags are open-submission: the feed name guarantees nothing, and
		# untechnical personal essays used to reach the candidate pool this way.
		self.assertFalse(is_technical(
			{"source": "medium:python", "title": "I Just Want to Grow Into This One", "summary": ""}))
		self.assertTrue(is_technical(
			{"source": "medium:python", "title": "Async Database Pooling in Python", "summary": ""}))

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


class TestSourceAuthorityRanking(unittest.TestCase):
	"""Feed items used to score a flat 20, which tied most of the pool together
    and let recency alone pick the source. Authority must break that tie."""

	def test_edited_publisher_outranks_medium_tag_feed(self):
		self.assertGreater(
			trending_module._feed_score("github-blog", True),
			trending_module._feed_score("medium:programming", True),
		)

	def test_authority_beats_recency(self):
		# A dated Medium post must still lose to a dated reputable publisher.
		self.assertGreater(
			trending_module._feed_score("infoq", True),
			trending_module._feed_score("medium:python", True),
		)

	def test_unknown_source_gets_default_not_zero(self):
		self.assertGreater(trending_module._feed_score("brand-new-feed", True), 0)

	def test_spam_titles_rejected(self):
		for title in (
			"13 Reliable Platforms to Buy Gmail Accounts",
			"Buy Verified Stripe Accounts Cheap",
			"Top 10 Sites to Learn Rust",
		):
			self.assertTrue(trending_module.is_spam({"title": title}), title)

	def test_legitimate_titles_not_flagged_as_spam(self):
		for title in (
			"Why Your In-Memory Cache Uses 10x More RAM Than It Should",
			"Buying Guide for Rust Crates",
			"Zig: Pointer Stability for ArrayLists",
		):
			self.assertFalse(trending_module.is_spam({"title": title}), title)


class TestReaderInterestAnalysis(unittest.TestCase):
	def _posts(self, spec):
		return [
			{"id": i, "title": t, "tags": [], "page_views": v,
			 "reactions": r, "comments": 0, "published_at": ""}
			for i, (t, v, r) in enumerate(spec)
		]

	def test_classifies_known_shapes(self):
		self.assertEqual(
			devto_stats.classify("Recover a Bricked Framework 13 with a DIY USB Flash"),
			"problem-workaround")
		self.assertEqual(
			devto_stats.classify("Deploying Meta's Llama 3 in a Production Python Service"),
			"build-tutorial")
		self.assertEqual(
			devto_stats.classify("Why Your In-Memory Cache Uses 10x More RAM"),
			"surprising-behavior")

	def test_report_ranks_archetype_by_average_not_volume(self):
		# One strong workaround post must beat three quiet tutorials.
		posts = self._posts([
			("Recover a Bricked Laptop", 600, 5),
			("Building a Thing", 5, 0),
			("Building Another Thing", 5, 0),
			("Deploying a Third Thing", 5, 0),
		])
		report = devto_stats.interest_report(posts)
		self.assertEqual(report["best_archetype"], "problem-workaround")

	def test_no_steering_until_sample_is_large_enough(self):
		posts = self._posts([("Recover a Bricked Laptop", 600, 5)])
		self.assertEqual(devto_stats.preferred_archetypes(devto_stats.interest_report(posts)), [])

	def test_no_steering_when_nothing_earned_engagement(self):
		posts = self._posts([(f"Building Thing {i}", 0, 0) for i in range(8)])
		self.assertEqual(devto_stats.preferred_archetypes(devto_stats.interest_report(posts)), [])

	def test_steers_once_evidence_exists(self):
		posts = self._posts(
			[("Recover a Bricked Laptop", 600, 5)] + [(f"Building Thing {i}", 0, 0) for i in range(7)]
		)
		self.assertIn(
			"problem-workaround",
			devto_stats.preferred_archetypes(devto_stats.interest_report(posts)),
		)

	def test_empty_input_is_safe(self):
		report = devto_stats.interest_report([])
		self.assertEqual(report["sample_size"], 0)
		self.assertEqual(devto_stats.preferred_archetypes(report), [])


class TestAudienceSteering(unittest.TestCase):
	_PROVEN = {
		"archetypes": [{"archetype": "problem-workaround", "count": 7,
						"avg_engagement": 90.0, "avg_views": 90.0, "best_title": "x"}],
		"best_archetype": "problem-workaround",
		"worst_archetype": "build-tutorial",
		"sample_size": 8,
	}

	def test_proven_archetype_wins_a_close_call(self):
		candidates = [
			{"title": "Building a Kubernetes Operator", "score": 63},
			{"title": "When Your Postgres Replica Gets Banned", "score": 55},
		]
		ordered = articles_module._prefer_proven_archetypes(candidates, {"article_interest": self._PROVEN})
		self.assertIn("Banned", ordered[0]["title"])

	def test_archetype_bonus_cannot_rescue_a_weak_source(self):
		# The whole point of authority ranking is that a low-credibility feed
		# does not get promoted just because its title matches a keyword.
		candidates = [
			{"title": "Cloudflare Workers Accept Inbound TCP", "score": 63},
			{"title": "Stop Typing Code. Start Building by Voice.", "score": 26},
		]
		ordered = articles_module._prefer_proven_archetypes(candidates, {"article_interest": self._PROVEN})
		self.assertIn("Cloudflare", ordered[0]["title"])

	def test_steering_preserves_all_candidates(self):
		candidates = [{"title": f"Building Thing {i}", "score": i} for i in range(5)]
		ordered = articles_module._prefer_proven_archetypes(candidates, {"article_interest": self._PROVEN})
		self.assertEqual(len(ordered), 5)

	def test_no_interest_data_leaves_order_untouched(self):
		candidates = [{"title": "B", "score": 2}, {"title": "A", "score": 1}]
		self.assertEqual(
			articles_module._prefer_proven_archetypes(candidates, {}), candidates)

	def test_guidance_empty_without_evidence(self):
		self.assertEqual(articles_module._audience_guidance({}), "")

	def test_guidance_mentions_proven_archetype(self):
		text = articles_module._audience_guidance({"article_interest": self._PROVEN})
		self.assertIn("problem-workaround", text)
		self.assertIn("AUDIENCE EVIDENCE", text)

	def test_guidance_does_not_leak_into_article(self):
		# The model must be told not to write about the account's own stats.
		text = articles_module._audience_guidance({"article_interest": self._PROVEN})
		self.assertIn("Do not mention this evidence", text)


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

		original = devto_module.requests.post
		try:
			def fake_post(url, headers=None, json=None, timeout=None):
				captured.update(json or {})
				return FakeResp()
			devto_module.requests.post = fake_post
			_publish_to_devto(
				{"title": "t", "body_markdown": "b", "_source": {"url": "https://ex.com"}},
				"key",
			)
		finally:
			devto_module.requests.post = original

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
		self.assertGreater(hours_until_due({"published_at": recent}, "published_at", 168), 0)

	def test_cadence_allows_when_due(self):
		old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
		self.assertEqual(hours_until_due({"published_at": old}, "published_at", 168), 0.0)

	def test_unparseable_stamp_does_not_wedge_module(self):
		self.assertEqual(hours_until_due({"published_at": "not-a-date"}, "published_at", 168), 0.0)

	def test_first_run_is_due_immediately(self):
		self.assertEqual(hours_until_due({}, "published_at", 168), 0.0)

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

	def test_niche_focus_absent_by_default(self):
		# Shipping a niche the owner did not choose would change every issue.
		self.assertEqual(newsletter_module._DEFAULTS["niche_focus"], "")

	def test_niche_focus_reaches_the_prompt(self):
		captured = {}

		class FakeLLM:
			def complete_json(self, prompt, system=None, max_tokens=None):
				captured["prompt"] = prompt
				return {}   # rejected downstream; we only care about the prompt

		original = newsletter_module.trending.fetch_candidates
		try:
			newsletter_module.trending.fetch_candidates = lambda **kw: self._items(5)
			_generate_issue(FakeLLM(), {}, self._cfg(niche_focus="platform engineers"))
			self.assertIn("platform engineers", captured["prompt"])
			# The niche angles the writing; it must not filter the sources.
			self.assertIn("STORY 5", captured["prompt"])
		finally:
			newsletter_module.trending.fetch_candidates = original


class TestMrrIdeaTriage(unittest.TestCase):
	"""Recurring-revenue triage must refuse blocked models and never invent MRR."""

	def _cfg(self, **over):
		cfg = dict(mrr_module._DEFAULTS)
		cfg.update(over)
		return cfg

	def _triaged(self, **over):
		return _triage(mrr_module._CATALOGUE, self._cfg(**over))

	def _refused_names(self, **over):
		return {r["name"]: r["reason"] for r in self._triaged(**over)[1]}

	# ── the policy guarantee: these are the tests that matter most ──────────

	def test_outreach_dependent_idea_is_refused(self):
		# An agency cannot acquire clients without cold outreach, which is blocked.
		reason = self._refused_names()["Local business AI automation agency"]
		self.assertIn("cold email", reason)

	def test_social_delivery_idea_is_refused(self):
		reason = self._refused_names()["Social media management retainer"]
		self.assertIn("social platforms", reason)

	def test_human_delivery_idea_is_refused(self):
		reason = self._refused_names()["Virtual assistant agency"]
		self.assertIn("human", reason)

	def test_inbound_http_idea_is_refused(self):
		# GitHub Actions is outbound-only: nothing can accept a request.
		reason = self._refused_names()["Niche job board / marketplace"]
		self.assertIn("outbound-only", reason)

	def test_every_refusal_carries_a_reason(self):
		# An unexplained refusal is useless to the owner.
		_, refused = self._triaged()
		self.assertTrue(refused)
		for entry in refused:
			self.assertTrue(entry["reason"].strip(), entry["name"])

	def test_no_refused_idea_leaks_into_viable(self):
		viable, refused = self._triaged()
		self.assertFalse({i["name"] for i in viable} & {r["name"] for r in refused})

	def test_every_catalogue_entry_is_accounted_for(self):
		# Nothing may be silently dropped: the owner read about all 20.
		viable, refused = self._triaged()
		self.assertEqual(
			{i["name"] for i in viable} | {r["name"] for r in refused},
			{i["name"] for i in mrr_module._CATALOGUE},
		)

	def test_payments_alone_does_not_refuse(self):
		# Every MRR model needs billing -- that is what MRR means. The owner can
		# open a Gumroad account by hand, so it is a prerequisite, not a blocker.
		viable, _ = self._triaged()
		names = {i["name"] for i in viable}
		self.assertIn("Paid newsletter", names)
		steps = next(i for i in viable if i["name"] == "Paid newsletter")["manual_steps"]
		self.assertTrue(any("payment" in s for s in steps))

	def test_something_survives_triage(self):
		# Guard against a blocker model so coarse that it refuses everything.
		viable, _ = self._triaged()
		self.assertTrue(viable)

	# ── cost discipline: every gate must precede the LLM call ───────────────

	def test_interval_blocks_early_refresh(self):
		recent = datetime.now(timezone.utc).isoformat()
		self.assertGreater(hours_until_due({"last_refresh_at": recent}, "last_refresh_at", 48), 0)

	def test_interval_allows_when_due(self):
		old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
		self.assertEqual(hours_until_due({"last_refresh_at": old}, "last_refresh_at", 48), 0.0)

	def test_unparseable_stamp_does_not_wedge_module(self):
		self.assertEqual(hours_until_due({"last_refresh_at": "not-a-date"}, "last_refresh_at", 48), 0.0)

	def test_first_run_is_due_immediately(self):
		self.assertEqual(hours_until_due({}, "last_refresh_at", 48), 0.0)

	def test_disabled_in_config_skips_without_llm_call(self):
		class ExplodingLLM:
			def complete_json_for_role(self, *a, **kw):
				raise AssertionError("disabled module must not call the LLM")

		original = mrr_module._config
		try:
			mrr_module._config = lambda: self._cfg(enabled=False)
			self.assertEqual(mrr_module.run(ExplodingLLM(), {}), [])
		finally:
			mrr_module._config = original

	def test_fresh_interval_skips_without_llm_call(self):
		class ExplodingLLM:
			def complete_json_for_role(self, *a, **kw):
				raise AssertionError("throttled module must not call the LLM")

		status = {"mrr_ideas": {"last_refresh_at": datetime.now(timezone.utc).isoformat()}}
		self.assertEqual(mrr_module.run(ExplodingLLM(), status), [])

	def test_force_override_bypasses_interval(self):
		status = {
			"mrr_ideas": {"last_refresh_at": datetime.now(timezone.utc).isoformat()},
			"_overrides": {"force_mrr": 1},
		}
		self.assertEqual(len(mrr_module.run(None, status)), 1)

	def test_no_llm_still_writes_deterministic_triage(self):
		# A dead LLM must still produce the refusal record, and raise nothing.
		status = {}
		actions = mrr_module.run(None, status)
		self.assertEqual(len(actions), 1)
		self.assertTrue(actions[0]["success"])
		self.assertFalse(actions[0]["llm"])
		self.assertTrue(status["mrr_ideas"]["refused"])

	def test_llm_failure_degrades_to_deterministic_triage(self):
		class BoomLLM:
			def complete_json_for_role(self, *a, **kw):
				raise RuntimeError("provider down")

		self.assertEqual(_viability_brief(BoomLLM(), [], self._cfg()), {})

	def test_non_dict_llm_output_is_rejected(self):
		class WeirdLLM:
			def complete_json_for_role(self, *a, **kw):
				return ["not", "an", "object"]

		self.assertEqual(_viability_brief(WeirdLLM(), [], self._cfg()), {})

	def test_brief_never_invents_fields(self):
		# Only whitelisted keys survive, so a chatty model cannot inject prose.
		class FakeLLM:
			def complete_json_for_role(self, *a, **kw):
				return {
					"summary": "one angle",
					"ranked_ideas": [{"name": "X", "who_pays": "devs", "junk": "drop me"}],
					"validation_steps": ["ask in a community you already belong to"],
					"owner_actions": ["do the thing"],
				}

		brief = _viability_brief(FakeLLM(), [], self._cfg())
		self.assertNotIn("junk", brief["ranked_ideas"][0])
		self.assertEqual(brief["ranked_ideas"][0]["who_pays"], "devs")

	# ── shared invariants ───────────────────────────────────────────────────

	def test_history_is_bounded(self):
		status = {}
		for i in range(300):
			_record_refresh(status, [{"name": f"Model {i}"}], 100)
		self.assertLessEqual(len(status["mrr_ideas_history"]["names"]), 100)

	def test_history_limit_zero_does_not_wipe_list(self):
		status = {}
		_record_refresh(status, [{"name": "Only One"}], 0)
		self.assertEqual(status["mrr_ideas_history"]["names"], ["Only One"])

	def test_triage_never_counts_as_revenue(self):
		# Mirrors the newsletter guard: research is not income.
		status = {"earnings": {"total_usd": 0.0, "this_week_usd": 0.0,
								"last_cycle_usd": 0.0, "week_started": None,
								"breakdown": {}}}
		updated = update(status, [{
			"platform": "mrr-ideas", "success": True,
			"title": "MRR idea triage refreshed", "url": "docs/mrr-ideas.md",
			"idea_count": 2, "refused_count": 18, "estimated_usd": 0.0,
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

	def test_main_engine_leads_every_chain(self):
		import bot.llm as llm_module
		for role, chain in self._chains().items():
			self.assertEqual(chain[0], llm_module._MAIN, role)

	def test_main_engine_is_a_live_free_model(self):
		"""stealth/ox-alpha led every chain until it was withdrawn from
		OpenRouter. The lead must be a real, free, non-stealth slug."""
		import bot.llm as llm_module
		self.assertTrue(llm_module._MAIN.endswith(":free"), llm_module._MAIN)
		self.assertFalse(llm_module._MAIN.startswith("stealth/"), llm_module._MAIN)

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
					model.endswith(":free") or model == "openrouter/free",
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
		"""A model can be withdrawn (as stealth/ox-alpha was); a 404 must not
		strand the chain."""
		import bot.llm as llm_module
		walked = self._walk("post", "model_not_found on openrouter: some/withdrawn-model")
		self.assertEqual(walked, llm_module._OPENROUTER_MODELS_BY_ROLE["post"])

	def test_dashboard_role_model_matches_live_chain(self):
		"""Regression: the dashboard named stealth/ox-alpha for weeks after the
		chains moved off it, because status.py hardcoded the model separately."""
		import bot.llm as llm_module
		from bot import status as status_module
		for role, cfg in status_module._role_workflow_spec().items():
			chain = llm_module._OPENROUTER_MODELS_BY_ROLE[role]
			self.assertEqual(cfg["provider"], llm_module.ROLE_PROVIDER[role], role)
			self.assertEqual(cfg["model"], chain[0], role)
			self.assertTrue(cfg["purpose"], role)


class TestTitleQualityGate(unittest.TestCase):
	"""Low view counts: flat or clickbait titles never earn a feed click."""

	def test_concrete_specific_title_passes(self):
		for title in (
			"The Postgres Index That Made Queries Slower",
			"I Was Wrong About Async Context Managers",
			"How Rate Limiters Actually Drop Your Requests",
			"Why Is Your Docker Build So Slow?",
		):
			self.assertEqual(_title_problems(title), [], title)

	def test_clickbait_words_rejected(self):
		self.assertTrue(any("ultimate" in p for p in _title_problems(
			"Ultimate Guide to Docker Networking Basics")))
		self.assertTrue(any("you need to know" in p for p in _title_problems(
			"Ten Python Features You Need to Know About")))

	def test_exclamation_and_shouting_rejected(self):
		self.assertTrue(any("exclamation" in p for p in _title_problems(
			"This Postgres Trick Changed My Whole Workflow!")))
		self.assertTrue(any("ALL-CAPS" in p for p in _title_problems(
			"This Postgres Trick Is INSANELY Useful For You")))

	def test_real_acronyms_are_not_treated_as_shouting(self):
		"""Regression: blocking all-caps rejected legitimate technical titles."""
		for title in (
			"Why Your JSON Parser Is Slower Than It Looks",
			"The HTTPS Redirect That Broke Our Login Flow",
			"How SQLite Handles Concurrent Writes Under Load",
		):
			self.assertEqual(_title_problems(title), [], title)

	def test_listicle_framing_rejected(self):
		self.assertTrue(_title_problems("Top 10 Python Libraries For Data Work"))
		self.assertTrue(_title_problems("7 Ways You Can Speed Up Your Builds"))

	def test_vague_title_rejected(self):
		self.assertTrue(any("vague" in p for p in _title_problems(
			"An Introduction To Writing Better Code In Python")))

	def test_length_bounds_enforced(self):
		self.assertTrue(any("too short" in p for p in _title_problems("Docker Tips")))
		self.assertTrue(any("too long" in p for p in _title_problems(
			"How To Configure A Production Ready Postgres Replica With Streaming "
			"Replication And Automatic Failover")))

	def test_colon_padding_rejected(self):
		self.assertTrue(any("colon" in p for p in _title_problems(
			"Retry Logic In Python: A Practical Guide To Exponential Backoff")))

	def test_short_prefix_colon_allowed(self):
		"""A short scoping prefix is fine; two full clauses are not."""
		self.assertEqual(_title_problems("Postgres: The Index That Slowed Us Down"), [])

	def test_empty_title_rejected(self):
		self.assertEqual(_title_problems(""), ["title is empty"])


class TestTagReach(unittest.TestCase):
	"""dev.to distributes by tag; niche-only tags reach nobody."""

	def test_high_traffic_tag_added_when_all_tags_are_niche(self):
		tags = _boost_tags(["pgbouncer", "wal"], [])
		self.assertIn("programming", tags)

	def test_account_proven_tag_preferred_over_default(self):
		tags = _boost_tags(["pgbouncer"], ["python", "webdev"])
		self.assertIn("python", tags)
		self.assertNotIn("programming", tags)

	def test_existing_high_traffic_tag_left_alone(self):
		tags = _boost_tags(["python", "pgbouncer"], [])
		self.assertEqual(tags, ["python", "pgbouncer"])

	def test_devto_four_tag_limit_respected(self):
		tags = _boost_tags(["pgbouncer", "wal", "vacuum", "toast", "mvcc"], [])
		self.assertLessEqual(len(tags), 4)

	def test_tags_are_slugified(self):
		self.assertEqual(_boost_tags(["Machine Learning!", "Python"], []),
						 ["machinelearning", "python"])

	def test_empty_tags_get_a_usable_default(self):
		self.assertTrue(_boost_tags([], []))


class TestFollowUpSelection(unittest.TestCase):
	"""Improve the post readers actually showed up for."""

	def _article(self, **kw):
		base = {
			"id": 1, "title": "A Postgres Index That Slowed Us Down", "url": "u",
			"page_views": 500, "reactions": 10, "comments": 2,
			"published_at": datetime.now(timezone.utc).isoformat(), "tags": ["python"],
		}
		base.update(kw)
		return base

	def test_highest_engagement_wins(self):
		low = self._article(id=1, page_views=300, reactions=0, comments=0)
		high = self._article(id=2, page_views=200, reactions=20, comments=3)
		best = devto_stats.top_performer([low, high], min_views=1)
		self.assertEqual(best["id"], 2, "reactions and comments must outweigh raw views")

	def test_stale_posts_excluded(self):
		old = self._article(
			published_at=(datetime.now(timezone.utc) - timedelta(hours=200)).isoformat())
		self.assertIsNone(devto_stats.top_performer([old], within_hours=48, min_views=1))

	def test_already_followed_up_post_skipped(self):
		art = self._article(id=7)
		self.assertIsNone(devto_stats.top_performer([art], min_views=1, exclude_ids={7}))

	def test_below_min_views_skipped(self):
		self.assertIsNone(devto_stats.top_performer(
			[self._article(page_views=3)], min_views=40))

	def test_missing_timestamp_is_not_followed_up(self):
		"""A post with no date must not be treated as recent."""
		self.assertIsNone(devto_stats.top_performer(
			[self._article(published_at="")], min_views=1))

	def test_empty_list_returns_none(self):
		self.assertIsNone(devto_stats.top_performer([], min_views=1))

	def test_winning_tags_average_rather_than_sum(self):
		arts = [
			{"tags": ["hit"], "page_views": 1000, "reactions": 0, "comments": 0},
			{"tags": ["meh"], "page_views": 10, "reactions": 0, "comments": 0},
			{"tags": ["meh"], "page_views": 10, "reactions": 0, "comments": 0},
			{"tags": ["meh"], "page_views": 10, "reactions": 0, "comments": 0},
		]
		self.assertEqual(devto_stats.winning_tags(arts)[0], "hit")

	def test_followup_records_parent_so_it_is_not_mined_twice(self):
		status = {}
		_record_publish(status, {
			"title": "Deeper Into Postgres Index Bloat",
			"_source": {}, "_followup_of": 42, "_followup_title": "old",
		})
		self.assertIn(42, status["article_history"]["followed_up_ids"])

	def test_stats_failure_does_not_break_the_cycle(self):
		"""A dev.to outage must fall through to the normal trending path."""
		original = devto_stats.fetch_published
		devto_stats.fetch_published = lambda *a, **k: []
		try:
			self.assertIsNone(_followup_target({}, "key"))
		finally:
			devto_stats.fetch_published = original

	def test_followup_disabled_by_config(self):
		original = articles_module._FOLLOWUP_OVERRIDE
		articles_module._FOLLOWUP_OVERRIDE = False
		try:
			self.assertIsNone(_followup_target({}, "key"))
		finally:
			articles_module._FOLLOWUP_OVERRIDE = original


class TestFollowUpContent(unittest.TestCase):
	"""A sequel must be distinguishable from its parent and link back to it."""

	def test_repeated_parent_title_detected(self):
		self.assertTrue(_titles_overlap(
			"The Postgres Index That Made Queries Slower",
			"The Postgres Index That Made Queries Slower"))

	def test_deeper_angle_on_same_subject_allowed(self):
		self.assertFalse(_titles_overlap(
			"What Index Bloat Does To Your Autovacuum Budget",
			"The Postgres Index That Made Queries Slower"))

	def test_backlink_added_when_model_omits_it(self):
		article = {"body_markdown": "Opening paragraph.\n\n## First Section\n\nBody."}
		out = _ensure_backlink(article, {"title": "Earlier Post", "url": "https://x.dev/1"})
		self.assertIn("https://x.dev/1", out["body_markdown"])
		# It must read as context near the top, not as a trailing footnote.
		self.assertLess(out["body_markdown"].index("https://x.dev/1"),
						out["body_markdown"].index("## First Section"))

	def test_existing_backlink_not_duplicated(self):
		body = "Intro linking [earlier](https://x.dev/1) already.\n\n## S\n\nBody."
		out = _ensure_backlink({"body_markdown": body},
							   {"title": "Earlier", "url": "https://x.dev/1"})
		self.assertEqual(out["body_markdown"].count("https://x.dev/1"), 1)

	def test_backlink_skipped_without_url(self):
		body = "Intro.\n\n## S\n\nBody."
		out = _ensure_backlink({"body_markdown": body}, {"title": "t", "url": ""})
		self.assertEqual(out["body_markdown"], body)


class TestFollowUpOverrides(unittest.TestCase):
	"""Owner commands must be able to force or skip a follow-up."""

	def setUp(self):
		self._orig = devto_stats.fetch_published
		self._recent = datetime.now(timezone.utc).isoformat()

	def tearDown(self):
		devto_stats.fetch_published = self._orig

	def _stub(self, views):
		devto_stats.fetch_published = lambda *a, **k: [{
			"id": 9, "title": "A Quiet Post About Postgres Vacuum", "url": "u",
			"tags": ["python"], "page_views": views, "reactions": 0, "comments": 0,
			"published_at": self._recent, "description": "d",
		}]

	def test_skip_followup_command_forces_fresh_source(self):
		self._stub(9999)
		status = {"_overrides": {"skip_followup": 1}}
		self.assertIsNone(_followup_target(status, "key"))

	def test_force_followup_bypasses_view_threshold(self):
		"""A post below followup_min_views is eligible when forced."""
		self._stub(3)
		self.assertIsNone(_followup_target({}, "key"), "unforced: below threshold")
		target = _followup_target({"_overrides": {"force_followup": 1}}, "key")
		self.assertIsNotNone(target, "forced: threshold must be bypassed")
		self.assertEqual(target["id"], 9)

	def test_force_followup_still_respects_already_followed_up(self):
		"""Forcing must not produce the same sequel twice."""
		self._stub(3)
		status = {
			"_overrides": {"force_followup": 1},
			"article_history": {"followed_up_ids": [9]},
		}
		self.assertIsNone(_followup_target(status, "key"))

	def test_stats_recorded_even_when_no_followup_is_written(self):
		"""Reach numbers are the point of the loop; record them regardless."""
		self._stub(3)
		status = {}
		_followup_target(status, "key")
		self.assertEqual(status["article_stats"]["best_views"], 3)


class TestEvolutionSandbox(unittest.TestCase):
	"""The sandbox is the only thing between an LLM and this repo's source."""

	def test_workflow_directory_is_never_writable(self):
		self.assertFalse(_evo_is_safe(".github/workflows/evolve.yml"))

	def test_git_directory_is_never_writable(self):
		self.assertFalse(_evo_is_safe(".git/config"))

	def test_path_traversal_rejected(self):
		self.assertFalse(_evo_is_safe("bot/../../../etc/passwd"))

	def test_unlisted_toplevel_path_rejected(self):
		self.assertFalse(_evo_is_safe("setup.py"))

	def test_allowed_module_path_accepted(self):
		self.assertTrue(_evo_is_safe("bot/earning/articles.py"))

	def test_protected_orchestrator_files_are_not_written(self):
		"""A model that proposes rewriting llm.py or main.py must be ignored."""
		for target in ("bot/main.py", "bot/llm.py", "bot/status.py",
					   "bot/commands.py", "bot/evolution.py", "bot/git_utils.py"):
			applied = _evo_apply_changes(
				[{"file": target, "content": "x = 1", "reason": "test"}]
			)
			self.assertEqual(applied, [], f"{target} must be protected")

	def test_syntactically_invalid_python_is_not_written(self):
		applied = _evo_apply_changes(
			[{"file": "bot/earning/_sandbox_probe.py",
			  "content": "def broken( syntax error", "reason": "test"}]
		)
		self.assertEqual(applied, [])
		self.assertFalse(Path("bot/earning/_sandbox_probe.py").exists())

	def test_change_count_is_capped_by_config(self):
		changes = [
			{"file": f"docs/_probe_{i}.md", "content": "x", "reason": "r"}
			for i in range(5)
		]
		try:
			applied = _evo_apply_changes(changes, max_changes=2)
			self.assertEqual(len(applied), 2)
		finally:
			for i in range(5):
				Path(f"docs/_probe_{i}.md").unlink(missing_ok=True)

	def test_config_cannot_raise_the_hard_ceiling(self):
		"""max_changes may lower MAX_CHANGES but never exceed it."""
		changes = [
			{"file": f"docs/_probe_{i}.md", "content": "x", "reason": "r"}
			for i in range(10)
		]
		try:
			applied = _evo_apply_changes(changes, max_changes=99)
			self.assertLessEqual(len(applied), evolution_module.MAX_CHANGES)
		finally:
			for i in range(10):
				Path(f"docs/_probe_{i}.md").unlink(missing_ok=True)


class TestEvolutionRestore(unittest.TestCase):
	"""
	Regression: a failed repair used to leave a truncated module on disk.

	Every fix attempt took its own backup, so the newest .bak was a broken
	fix, and _restore_backup restored that instead of the pre-cycle original.
	One real cycle shrank articles.py from 42KB to 1.6KB and code_techs.py to
	427 bytes; all four earning modules then crashed on import.
	"""

	def setUp(self):
		self.target = Path("bot/earning/_restore_probe.py")
		self.target.write_text("ORIGINAL = 1\n", encoding="utf-8")
		self.addCleanup(self.target.unlink)

	def test_restore_prefers_the_recorded_pre_cycle_backup(self):
		original = evolution_module._backup(str(self.target))
		self.assertIsNotNone(original)
		self.addCleanup(Path(original).unlink, True)

		# A later, broken "fix" snapshot -- newer on disk than the original.
		broken = evolution_module._backup(str(self.target))
		Path(broken).write_text("TRUNCATED = 1\n", encoding="utf-8")
		self.addCleanup(Path(broken).unlink, True)
		os.utime(broken, (time.time() + 10, time.time() + 10))

		self.target.write_text("TRUNCATED = 1\n", encoding="utf-8")
		evolution_module._restore_backup(str(self.target), original)
		self.assertEqual(self.target.read_text(encoding="utf-8"), "ORIGINAL = 1\n")

	def test_apply_changes_records_the_backup_it_took(self):
		applied = _evo_apply_changes(
			[{"file": "bot/earning/_restore_probe.py",
			  "content": "REPLACED = 1", "reason": "probe"}]
		)
		self.assertEqual(len(applied), 1)
		backup = applied[0].get("_backup")
		self.assertTrue(backup and Path(backup).exists())
		self.addCleanup(Path(backup).unlink, True)
		self.assertEqual(Path(backup).read_text(encoding="utf-8"), "ORIGINAL = 1\n")


class TestEvolutionGate(unittest.TestCase):
	"""Evolution is opt-in: absence of config must mean off, never on."""

	def test_disabled_by_default_when_config_missing(self):
		self.assertFalse(evolution_module.enabled({}))

	def test_explicit_false_disables(self):
		self.assertFalse(evolution_module.enabled({"enabled": False}))

	def test_explicit_true_enables(self):
		self.assertTrue(evolution_module.enabled({"enabled": True}))

	def test_branch_name_is_unique_and_git_legal(self):
		name = evolution_module._branch_name("1.2.3", "evolve")
		self.assertTrue(name.startswith("evolve/1.2.3-"))
		self.assertNotIn(" ", name)
		self.assertNotIn("~", name)

	def test_branch_name_sanitizes_hostile_version(self):
		name = evolution_module._branch_name("1.0 ../evil~", "evolve")
		for bad in (" ", "..", "~"):
			self.assertNotIn(bad, name.split("/", 1)[1])


class TestJsonParsing(unittest.TestCase):
	"""Truncated-plan recovery: the model hitting max_tokens must not cost a cycle."""

	def _plan(self):
		return {
			"version": "1.35.1",
			"summary": "fix the parse failure",
			"suggestions": [{"title": "a"}, {"title": "b"}],
			"changes": [
				{"file": "bot/earning/x.py", "content": "print('hi')", "reason": "r1"},
				{"file": "bot/earning/y.py", "content": "z" * 400, "reason": "r2"},
			],
		}

	def test_parses_plain_and_fenced(self):
		plan = self._plan()
		raw  = json.dumps(plan)
		self.assertEqual(llm_module.parse_json(raw), plan)
		self.assertEqual(llm_module.parse_json("```json" + chr(10) + raw + chr(10) + "```"), plan)

	def test_parses_object_wrapped_in_prose(self):
		raw = "Here is the plan:" + chr(10) + json.dumps(self._plan())
		self.assertEqual(llm_module.parse_json(raw)["version"], "1.35.1")

	def test_recovers_complete_changes_from_truncated_response(self):
		plan = self._plan()
		raw  = json.dumps(plan)
		# Cut mid-string inside the SECOND change's content.
		cut  = raw.index("z" * 20) + 100
		got  = llm_module.parse_json(raw[:cut])
		# The complete first change survives; the half-written one is dropped.
		self.assertEqual(got["changes"], [plan["changes"][0]])
		self.assertEqual(got["suggestions"], plan["suggestions"])
		self.assertEqual(got["version"], "1.35.1")

	def test_recovers_scalars_when_first_change_is_cut(self):
		plan = self._plan()
		raw  = json.dumps(plan)
		got  = llm_module.parse_json(raw[:raw.index("print(") + 3])
		self.assertEqual(got.get("changes", []), [])
		self.assertEqual(got["summary"], "fix the parse failure")

	def test_recovers_complete_suggestions_only(self):
		plan = self._plan()
		raw  = json.dumps(plan)
		got  = llm_module.parse_json(raw[:raw.index('"title": "b"') + 8])
		self.assertEqual(got["suggestions"], [plan["suggestions"][0]])

	def test_rejects_non_dict_and_garbage(self):
		for bad in ("[1,2,3]", "not json at all", "", "{", '{"a":'):
			with self.assertRaises(ValueError):
				llm_module.parse_json(bad)

	def test_recovers_leading_scalar_before_cut(self):
		# Cut inside the second value: the first complete pair still survives.
		got = llm_module.parse_json('{"version": "1.0.0", "summary": "cut off here')
		self.assertEqual(got["version"], "1.0.0")

	def test_truncation_error_names_max_tokens(self):
		# Cut before any pair completes -- nothing to salvage, so it must raise,
		# and the message must point at max_tokens rather than a bad prompt.
		with self.assertRaises(ValueError) as ctx:
			llm_module.parse_json('{"version": "1.0.0')
		self.assertIn("max_tokens", str(ctx.exception))

	def test_evolution_plan_budget_exceeds_legacy_6k(self):
		# The schema asks for COMPLETE contents of up to MAX_CHANGES files;
		# 6k tokens could not hold that, which is what caused the cut-off.
		self.assertGreaterEqual(evolution_module._MAX_PLAN_TOKENS, 32_000)
		self.assertGreaterEqual(evolution_module._MAX_FIX_TOKENS, 16_000)


if __name__ == "__main__":
	unittest.main()


class TestSharedPrimitives(unittest.TestCase):
	"""The consolidated helpers every earning module now shares.

    Each module used to carry its own copy and the copies had drifted. These
    lock in the stronger behaviour so a future edit cannot quietly regress the
    module that previously had the weaker version.
    """

	def test_parses_rfc822_rss_dates(self):
		# code_techs' old _parse_dt returned None here, so Reddit/HN RSS
		# pubDates were silently unparseable in that module.
		parsed = shared.parse_dt("Wed, 27 Aug 2026 10:30:00 GMT")
		self.assertIsNotNone(parsed)
		self.assertEqual(parsed.year, 2026)
		self.assertIsNotNone(parsed.tzinfo)

	def test_parses_iso_and_assumes_utc_when_naive(self):
		self.assertEqual(shared.parse_dt("2026-08-27T10:30:00Z").hour, 10)
		self.assertEqual(shared.parse_dt("2026-08-27T10:30:00").tzinfo, timezone.utc)

	def test_parse_dt_returns_none_on_junk(self):
		for junk in ("", None, "not-a-date", 0):
			self.assertIsNone(shared.parse_dt(junk), junk)

	def test_strip_html_drops_script_bodies(self):
		# code_techs' old _strip_html removed the tags but kept the JS source,
		# so script text reached the LLM as if it were post prose.
		out = shared.strip_html("<p>real</p><script>var x = 1;</script><p>text</p>")
		self.assertIn("real", out)
		self.assertIn("text", out)
		self.assertNotIn("var x", out)

	def test_load_config_fills_defaults_and_survives_missing_file(self):
		original = shared.CONFIG_FILE
		shared.CONFIG_FILE = Path("does/not/exist.json")
		try:
			cfg = shared.load_config("articles", {"min_words": 700})
			self.assertEqual(cfg["min_words"], 700)
		finally:
			shared.CONFIG_FILE = original

	def test_load_config_reads_live_file_not_import_time_snapshot(self):
		cfg = shared.load_config("articles", {"min_words": 1})
		self.assertEqual(cfg["min_words"], 700)

	def test_hours_until_due_respects_the_named_key(self):
		recent = datetime.now(timezone.utc).isoformat()
		self.assertGreater(shared.hours_until_due({"a": recent}, "a", 168), 0)
		# A stamp under a different key must not block this cadence.
		self.assertEqual(shared.hours_until_due({"b": recent}, "a", 168), 0.0)

	def test_bounded_append_dedupes_and_trims_to_newest(self):
		entries = []
		for value in ("a", "b", "a", "c"):
			shared.bounded_append(entries, value, limit=2)
		self.assertEqual(entries, ["b", "c"])

	def test_bounded_append_ignores_empty_values(self):
		entries = ["a"]
		shared.bounded_append(entries, "", limit=5)
		self.assertEqual(entries, ["a"])


class TestArticleConfigIsReadAtCallTime(unittest.TestCase):
	"""Config edits must take effect without reimporting the module."""

	def test_title_gate_honours_injected_config(self):
		title = "Postgres: The Index That Slowed Us Down"
		self.assertEqual(_title_problems(title), [])
		tight = dict(articles_module._DEFAULTS, title_max_chars=10)
		self.assertTrue(any("too long" in p for p in _title_problems(title, tight)))

	def test_format_gate_honours_injected_config(self):
		body = "## One\n\n" + ("word " * 50)
		self.assertTrue(any("too short" in p for p in _format_problems(body)))
		loose = dict(articles_module._DEFAULTS, min_words=10)
		self.assertFalse(any("too short" in p for p in _format_problems(body, loose)))


class TestDevtoModuleIsThePublicSeam(unittest.TestCase):
	"""articles and newsletter must share one dev.to gate, via a public API."""

	def test_both_modules_use_the_same_gate_objects(self):
		self.assertIs(articles_module.devto, devto_module)
		self.assertIs(newsletter_module.devto, devto_module)

	def test_shared_gates_are_public_names(self):
		for name in ("publish", "normalize", "tone_problems",
					 "fabrication_problems", "strip_fabricated_tables"):
			self.assertTrue(hasattr(devto_module, name), name)

	def test_articles_no_longer_owns_the_moved_gates(self):
		# They live in devto now; a stale copy left behind is exactly the drift
		# this split exists to prevent.
		for name in ("_publish_to_devto", "_normalize", "_tone_problems"):
			self.assertFalse(hasattr(articles_module, name), name)
