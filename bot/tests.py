import unittest
import os
import re
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
import bot.earning.payout as payout
import bot.earning.backfill as backfill
import bot.earning.receipt_check as receipt_check
import bot.earning.attribution as attribution
import bot.status as status_mod
from unittest import mock
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
from bot.earning import code_techs as code_techs_module
from bot.earning.code_techs import (
	_fetch_github_leads,
	_fetch_hn_hiring_leads,
	_fetch_reddit_leads,
	_is_free_ai_lead,
	_lead_value,
	_online_ai_brief,
	_parse_reddit_rss,
	_rank,
	_reference_sources,
)
from bot.earning.trending import (
	_dedupe,
	_extract_article_text,
	_parse_dt,
	is_own_post,
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


class TestSelfSourceExclusion(unittest.TestCase):
	"""The bot reads dev.to's programming tag and publishes into it, so its own
    posts came back as "trending news". It wrote a take on its own top article
    and credited itself in a ## Source section as if it were someone else's
    reporting. Following up on our own work is a real feature (_generate_followup);
    this path must not counterfeit it."""

	OWN = "https://dev.to/robust_true_try/reading-twitter-without-x-1gig"

	def test_own_post_detected_from_published_url(self):
		keys = trending_module._author_keys([self.OWN])
		self.assertTrue(is_own_post({"url": self.OWN}, keys))

	def test_other_devto_authors_are_not_excluded(self):
		keys = trending_module._author_keys([self.OWN])
		self.assertFalse(is_own_post(
			{"url": "https://dev.to/someone_else/a-real-story-abc"}, keys))

	def test_bare_handle_and_profile_url_both_accepted(self):
		for spelling in ("robust_true_try", "dev.to/robust_true_try",
						 "https://dev.to/robust_true_try"):
			keys = trending_module._author_keys([spelling])
			self.assertTrue(is_own_post({"url": self.OWN}, keys), spelling)

	def test_no_authors_excludes_nothing(self):
		self.assertFalse(is_own_post({"url": self.OWN}, set()))

	def test_fetch_candidates_drops_own_posts(self):
		original = trending_module._fetch_feed
		hn = trending_module._fetch_hn_front_page
		try:
			def fake_feed(source, url, cutoff):
				if source != "devto-top":
					return []
				return [
					{"title": "Reading Twitter Without X", "url": self.OWN,
					 "source": "devto-top", "summary": "nitter python docker",
					 "published_at": "2026-09-01T00:00:00+00:00", "score": 34},
					{"title": "A Postgres Index Story", "source": "devto-top",
					 "url": "https://dev.to/other_dev/a-postgres-index-story-x1",
					 "summary": "postgres database index", "score": 34,
					 "published_at": "2026-09-01T00:00:00+00:00"},
				]
			trending_module._fetch_feed = fake_feed
			trending_module._fetch_hn_front_page = lambda cutoff: []

			urls = [i["url"] for i in trending_module.fetch_candidates(
				exclude_authors=[self.OWN])]
			self.assertNotIn(self.OWN, urls)
			self.assertEqual(len(urls), 1)

			# Without the exclusion the own post is still a candidate, which is
			# what shipped the self-sourced article.
			self.assertIn(self.OWN,
						  [i["url"] for i in trending_module.fetch_candidates()])
		finally:
			trending_module._fetch_feed = original
			trending_module._fetch_hn_front_page = hn

	def test_own_urls_shared_between_products(self):
		status = {"article_history": {"own_urls": [self.OWN]}}
		self.assertEqual(devto_module.own_post_urls(status), [self.OWN])
		self.assertEqual(devto_module.own_post_urls({}), [])

	def test_account_urls_derived_from_published(self):
		posts = [{"url": self.OWN, "title": "x"}, {"url": "", "title": "y"}]
		self.assertEqual(devto_stats.account_urls(posts), [self.OWN])


class TestNonTechnicalTitleScreening(unittest.TestCase):
	"""Two ways junk reached the candidate pool, both of which shipped.

    is_technical poured title and summary into one bag of words and accepted a
    single hit anywhere, so a dev.to clothing advert whose blurb said "build"
    and "data" was published as a story in a weekly developer digest. And
    vocabulary cannot catch promotional content at all -- "MATLAB Online
    Training | MATLAB Training Courses Online" is full of real technical words
    -- so intent is screened separately by is_spam. fetch_candidates applies
    both, so these assert both.
    """

	@staticmethod
	def accepted(item):
		"""The screen as fetch_candidates actually applies it."""
		return (is_technical(item)
				and not trending_module.is_spam(item)
				and not trending_module.is_off_topic(item))

	def test_clothing_advert_rejected_despite_stray_summary_keywords(self):
		self.assertFalse(self.accepted({
			"source": "devto-top",
			"title": ("Family Matching Outfits: How to Create Stylish Looks "
					  "for Every Family Member"),
			"summary": "Find the best data on family style. Build your look."}))

	def test_technical_title_alone_is_enough(self):
		self.assertTrue(self.accepted({
			"source": "devto-top", "title": "Debugging a Postgres deadlock",
			"summary": ""}))

	def test_untechnical_title_needs_a_technical_summary(self):
		item = {"source": "hacker-news", "title": "What we learned the hard way"}
		self.assertFalse(self.accepted({**item, "summary": "It was a long year."}))
		self.assertTrue(self.accepted(
			{**item, "summary": "Our kubernetes deploy pipeline kept timing out."}))

	def test_real_devto_posts_survive_the_screen(self):
		# The dev.to feed ships no summaries, so the title carries the whole
		# decision. Tightening this must not cost genuine articles -- an empty
		# candidate pool is a worse failure than a mediocre source.
		for title in ("What Boot adds over plain Spring",
					  "Production Multi-Agent Systems: The Silent Failures",
					  "Building a 200M parameter LLM from scratch in PyTorch"):
			self.assertTrue(self.accepted(
				{"source": "devto-top", "title": title, "summary": ""}), title)

	def test_marketing_and_listicles_rejected_on_title_alone(self):
		# Every one of these was live on dev.to's programming tag.
		for title in ("Content Marketing Services in Noida",
					  "Best PPC and SEO Company in Noida",
					  "MATLAB Online Training | MATLAB Training Courses Online",
					  "100+ ChatGPT Prompts for Developers - The Ultimate Collection",
					  "MeetGeek vs MeetingMinutes vs Otter.ai: Collaboration Apps"):
			self.assertFalse(self.accepted(
				{"source": "devto-top", "title": title, "summary": ""}), title)

	def test_real_ai_news_still_passes_hacker_news(self):
		# Demoting "ai"/"model"/"release" to weak signals was tried and reverted:
		# it dropped exactly the stories this bot exists to write about.
		for title in ("Quasar 438B: Europe's Leading AI Model",
					  "WebLLM: high-performance in-browser LLM inference engine"):
			self.assertTrue(self.accepted(
				{"source": "hacker-news", "title": title, "summary": ""}), title)
		# A title can carry no listed term at all ("Gemini 3.8 Flash and 3.8
		# Flash Cyber") and still be the story of the day. That is what the
		# summary fallback is for -- it is the reason the rule is >= 1 word and
		# not stricter, and why off-topic subjects are screened by name instead.
		self.assertTrue(self.accepted({
			"source": "hacker-news", "title": "Gemini 3.8 Flash and 3.8 Flash Cyber",
			"summary": "Google's new model for cybersecurity inference."}))

	def test_gambling_front_rejected_despite_a_technical_word(self):
		# Pure ad copy that mentioned "security" once, which was enough to clear
		# the summary rule. Subject screening is what stops it.
		self.assertFalse(self.accepted({
			"source": "devto-top",
			"title": "Shree Win Game Online - How the Platform Works.",
			"summary": ("Online gaming has become a popular form of digital "
						"entertainment. Account access and security matter.")}))

	def test_game_development_is_not_gambling(self):
		# The gambling patterns must not swallow real game-engine work.
		for title in ("Building a multiplayer game server in Rust",
					  "Writing a chess engine in Go",
					  "Deterministic physics in a game loop with fixed timesteps"):
			self.assertTrue(self.accepted(
				{"source": "devto-top", "title": title, "summary": ""}), title)

	def test_non_software_hacker_news_stories_still_dropped(self):
		for title in ("Biggest dark matter detector spots a single weird particle",
					  "Wendell Berry has died",
					  "A Selection of Los Alamos Rolodex Business Cards"):
			self.assertFalse(self.accepted(
				{"source": "hacker-news", "title": title, "summary": ""}), title)


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

	def test_model_size_notation_allowed(self):
		"""Regression: a rule on bare sizes blocked correct prose and stopped a day's article.

        "7B"/"70B" quotes a published model's size -- it is standard notation,
        not an invented spec. Rejecting it killed two of three drafts on an
        LLM-hardware source on 2026-09-01 while their prose was accurate.
        """
		body = (
			"A 7B parameter model in 4-bit quantization sits around 4 GB. "
			"A 13B model in 4-bit is closer to 8 GB, and a 70B model needs more. "
			"We ran Llama 3 70B on the box."
		)
		self.assertEqual(_fabrication_problems(body), [])

	def test_plain_uppercase_units_allowed(self):
		"""The old rule ran case-insensitively and swallowed ordinary measurements."""
		for body in ("it took 3 m to run", "we copied 2 T of data", "the drive holds 4 T"):
			self.assertEqual(_fabrication_problems(body), [], body)

	def test_other_fabrication_rules_still_fire(self):
		"""Removing the size rule must not weaken the four that remain."""
		self.assertIn("invented latency figures (ms)",
					  _fabrication_problems("It replies in 45 ms."))
		self.assertIn("invented pricing",
					  _fabrication_problems("It costs $5 per million requests."))
		self.assertIn("invented throughput",
					  _fabrication_problems("It sustains 120 tokens/s."))
		self.assertIn("invented benchmark deltas",
					  _fabrication_problems("It is 40% faster than the alternative."))


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

	def test_daily_counter_resets_on_a_new_day(self):
		"""The counter is per-day, not a lifetime tally.

        It carried yesterday's total forward, so it read 26 against 8 real
        posts -- meaningless on the dashboard, and it would cap the day the
        moment max_articles_per_cycle rose above 1.
        """
		import bot.earning.articles as articles_module
		from datetime import datetime, timezone

		today = datetime.now(timezone.utc).date().isoformat()

		class FakeResp:
			status_code = 201
			def raise_for_status(self): pass
			def json(self): return {"url": "https://dev.to/x", "id": 1}

		status = {"article_daily": {"date": "1999-01-01", "published": 26}}
		original_post = devto_module.requests.post
		original_gen = articles_module._generate_article
		original_key = os.environ.get("DEV_TO_API_KEY")
		try:
			devto_module.requests.post = lambda *a, **k: FakeResp()
			articles_module._generate_article = lambda llm, st: {
				"title": "t", "body_markdown": "b", "tags": ["python"], "_source": {},
			}
			os.environ["DEV_TO_API_KEY"] = "key"
			articles_module.run(object(), status)
		finally:
			devto_module.requests.post = original_post
			articles_module._generate_article = original_gen
			if original_key is None:
				os.environ.pop("DEV_TO_API_KEY", None)
			else:
				os.environ["DEV_TO_API_KEY"] = original_key

		self.assertEqual(status["article_daily"]["date"], today)
		self.assertEqual(status["article_daily"]["published"], 1)


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
	def test_rank_builds_a_market_specific_codex_prompt(self):
		cfg = {"daily_target_usd": 10.0, "prompt_top_n": 5}
		leads = [{
			"title": "Need a script to automate CSV export",
			"url": "https://example.com/request",
			"source": "community",
			"kind": "demand",
			"buyer": "Acme Books",
			"body": "Looking for a simple tool to export and convert a CSV every week.",
			"labels": ["community-request"],
			"posted_at": _hours_ago_iso(3),
		}]

		ranked = _rank(leads, cfg, max_items=1, min_score=0)

		self.assertEqual(len(ranked), 1)
		prompt = ranked[0].codex_prompt
		self.assertIn("Acme Books", prompt)
		self.assertIn("Need a script to automate CSV export", prompt)
		self.assertIn("Do not contact anyone", prompt)

	def test_parse_reddit_rss_builds_community_lead(self):
		feed = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <title>Need a script to automate invoices</title>
            <link href="https://www.reddit.com/r/smallbusiness/comments/abc/request/" />
            <updated>2026-09-07T10:00:00+00:00</updated>
            <content type="html">&lt;p&gt;Looking for a simple export tool.&lt;/p&gt;</content>
          </entry>
        </feed>"""

		leads = _parse_reddit_rss(feed, "smallbusiness")

		self.assertEqual(len(leads), 1)
		self.assertEqual(leads[0]["source"], "reddit:r/smallbusiness")
		self.assertIn("reddit", leads[0]["labels"])
		self.assertIn("simple export tool", leads[0]["body"])
		# Without a timestamp the UI cannot show or sort by age, which is the
		# whole reason stale leads went unnoticed.
		self.assertEqual(leads[0]["posted_at"], "2026-09-07T10:00:00+00:00")

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

def _hours_ago_iso(hours: float) -> str:
	"""ISO stamp `hours` in the past, for lead-freshness fixtures."""
	from datetime import datetime, timedelta, timezone
	return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


class _StubResp:
	"""Minimal stand-in for a requests Response."""

	def __init__(self, payload=None, status_code=200, text=""):
		self._payload = payload if payload is not None else {}
		self.status_code = status_code
		self.text = text

	def json(self):
		return self._payload

	def raise_for_status(self):
		if self.status_code >= 400:
			raise AssertionError(f"HTTP {self.status_code}")


class TestLeadValueIsNeverFabricated(unittest.TestCase):
	"""A lead may only show a price its source actually published.

    `_extract_value` used to take max() of every "$N" in the lead text, so the
    live queue's top lead read $4,500 -- a figure lifted from an unrelated
    repository roadmap -- and the dashboard summed those into a "$5.6k
    pipeline value" displayed beside a real on-chain balance of $0.00.
    """

	def test_a_dollar_figure_in_body_text_is_not_a_value(self):
		value, basis, note = _lead_value({
			"title": "Map: the foundation for Demido Studio v3",
			"body": "the budget was $4,500 for the redesign",
		})

		self.assertIsNone(value)
		self.assertEqual(basis, "none")
		self.assertEqual(note, "")

	def test_posted_salary_survives_and_records_its_period(self):
		value, basis, note = _lead_value({
			"min_salary": 40, "max_salary": 40,
			"currency": "USD", "salary_period": "hourly",
		})

		self.assertEqual(value, 40.0)
		self.assertEqual(basis, "posted_salary")
		# The period has to travel with the figure. An hourly rate reported as
		# a bare number reads as an annual salary.
		self.assertIn("/hr", note)

	def test_non_usd_salary_is_refused(self):
		# Real: Himalayas serves CAD ranges. Rendering one with a "$" is not
		# an approximation, it is a different number.
		value, basis, _ = _lead_value({
			"min_salary": 100000, "max_salary": 115000,
			"currency": "CAD", "salary_period": "annual",
		})

		self.assertIsNone(value)
		self.assertEqual(basis, "none")

	def test_a_rate_the_poster_typed_is_kept(self):
		value, basis, note = _lead_value({
			"allow_rate_extraction": True,
			"body": "Noricum | Senior Backend Engineer | REMOTE | Contract | $120-160/hr",
		})

		self.assertEqual(value, 120.0)
		self.assertEqual(basis, "stated_rate")
		self.assertIn("$120-160/hr", note)

	def test_funding_and_valuation_figures_are_not_rates(self):
		# Same thread carries "~$37M raised" and "$2.7M" of runway. Requiring
		# an explicit /hr unit is what keeps those out.
		for body in ("we raised $4,500 in funding", "~$37M raised", "Comp: $215K-$260K + equity"):
			value, basis, _ = _lead_value({"allow_rate_extraction": True, "body": body})
			self.assertIsNone(value, body)
			self.assertEqual(basis, "none", body)

	def test_unknown_value_is_none_not_zero(self):
		leads = [{
			"title": "Someone wants a CSV cleanup script",
			"source": "community", "kind": "demand", "body": "no price mentioned",
			"labels": [], "posted_at": _hours_ago_iso(2),
		}]

		ranked = _rank(leads, {"prompt_top_n": 1}, max_items=5, min_score=0)

		self.assertEqual(ranked[0].value_usd, None)
		# 0.0 would sum into a total and sort as the cheapest lead. None
		# forces the UI to admit it does not know.
		self.assertFalse(any(op.value_usd == 0.0 for op in ranked))


class TestLeadScoreDiscriminates(unittest.TestCase):
	"""Scores have to separate leads, not pile up on the clamp.

    The live queue scored 100, 100, 100, 100, 100, 98, 96, 96 because the old
    function started at 30 and added ~140 of overlapping bonuses before
    clamping to 100 -- so `min_score: 55` filtered nothing at all.
    """

	def _varied_leads(self):
		leads = []
		for index in range(10):
			leads.append({
				"title": f"Contract data pipeline work {index}",
				"url": f"https://example.com/{index}",
				"source": "himalayas" if index % 2 else "github",
				"kind": "demand" if index % 2 else "supply",
				"body": ("freelance contract to transcribe and extract data" if index % 3
				         else "a free llm api with a generous free tier"),
				"labels": [],
				"posted_at": _hours_ago_iso(index * 9),
				"min_salary": 50 + index if index % 4 == 0 else None,
				"currency": "USD",
				"salary_period": "hourly",
			})
		return leads

	def test_scores_spread_out_instead_of_saturating(self):
		ranked = _rank(self._varied_leads(), {"deliverable_terms": ["transcri", "extract", "data"]},
		               max_items=20, min_score=0)
		scores = [op.score for op in ranked]

		self.assertGreaterEqual(len(set(scores)), 6, scores)
		self.assertGreaterEqual(max(scores) - min(scores), 30, scores)
		# The specific live symptom: five leads tied at the ceiling.
		self.assertLessEqual(scores.count(100), 1, scores)

	def test_score_parts_explain_the_rank(self):
		ranked = _rank(self._varied_leads(), {}, max_items=3, min_score=0)

		parts = ranked[0].score_parts
		self.assertIn("recency", parts)
		self.assertIn("demand_intent", parts)
		self.assertIn("value_clarity", parts)


class TestLeadRecencyIsEnforced(unittest.TestCase):
	"""Stale leads must not reach the page, and age must be visible."""

	def _lead(self, hours, source="himalayas"):
		return {
			"title": "Contract data cleanup", "url": f"https://example.com/{hours}",
			"source": source, "kind": "demand", "body": "freelance contract work",
			"labels": [], "posted_at": _hours_ago_iso(hours),
		}

	def test_age_hours_is_recorded(self):
		ranked = _rank([self._lead(2)], {}, max_items=5, min_score=0)

		self.assertAlmostEqual(ranked[0].age_hours, 2.0, delta=0.5)
		self.assertIsNotNone(ranked[0].posted_at)

	def test_fresher_leads_outrank_older_twins(self):
		ranked = _rank([self._lead(1), self._lead(60)], {}, max_items=5, min_score=0)

		self.assertGreater(ranked[0].score, ranked[-1].score)
		self.assertLess(ranked[0].age_hours, ranked[-1].age_hours)

	def test_unknown_age_scores_below_a_confirmed_fresh_lead(self):
		undated = dict(self._lead(1))
		undated["posted_at"] = None
		undated["url"] = "https://example.com/undated"

		ranked = _rank([self._lead(1), undated], {}, max_items=5, min_score=0)
		by_url = {op.url: op for op in ranked}

		self.assertIsNone(by_url["https://example.com/undated"].age_hours)
		self.assertGreater(
			by_url["https://example.com/1"].score,
			by_url["https://example.com/undated"].score,
		)

	def test_the_monthly_hn_thread_is_not_judged_as_stale(self):
		# HN's hiring thread is monthly, so its best replies are days old by
		# design. Judging them on a 72h job-feed window would drop the only
		# leads that quote a real hourly rate.
		cfg = {"demand_max_age_hours": 72, "hn_hiring_max_age_hours": 744}
		hn = self._lead(150, source="hn-hiring")
		feed = self._lead(150, source="himalayas")

		ranked = _rank([hn, feed], cfg, max_items=5, min_score=0)
		by_source = {op.source: op for op in ranked}

		self.assertGreater(by_source["hn-hiring"].score, by_source["himalayas"].score)


class TestGithubSearchHitsTheRepositoryEndpoint(unittest.TestCase):
	"""The GitHub queries are repository queries and must be sent as such.

    They were sent to search/issues, which silently ignores `in:readme` and
    `stars:`. The identical query string returns 12 junk issues there and 511
    real repositories on search/repositories -- which is why the live page
    listed a studio roadmap and a bot's own trend digest as earning leads.
    """

	def test_it_queries_repositories_not_issues(self):
		seen = []

		def fake_get(url, **kwargs):
			seen.append(url)
			return _StubResp({"items": []})

		original = code_techs_module.requests.get
		try:
			code_techs_module.requests.get = fake_get
			_fetch_github_leads({"github_searches": ["free AI API stars:>200"]})
		finally:
			code_techs_module.requests.get = original

		self.assertTrue(seen)
		self.assertTrue(all("search/repositories" in url for url in seen), seen)
		self.assertFalse(any("search/issues" in url for url in seen), seen)

	def test_repositories_are_labelled_supply_not_demand(self):
		payload = {"items": [{
			"full_name": "public-apis/public-apis",
			"html_url": "https://github.com/public-apis/public-apis",
			"description": "A collective list of free APIs",
			"pushed_at": _hours_ago_iso(24),
			"stargazers_count": 477220,
			"topics": ["api", "free"],
		}]}

		original = code_techs_module.requests.get
		try:
			code_techs_module.requests.get = lambda *a, **k: _StubResp(payload)
			leads = _fetch_github_leads({"github_searches": ["free api"]})
		finally:
			code_techs_module.requests.get = original

		self.assertEqual(len(leads), 1)
		# GitHub answers "what can I build with", never "who is paying".
		self.assertEqual(leads[0]["kind"], "supply")

	def test_long_abandoned_repositories_are_dropped(self):
		payload = {"items": [{
			"full_name": "someone/abandoned",
			"html_url": "https://github.com/someone/abandoned",
			"description": "free ai api wrapper",
			"pushed_at": "2019-01-01T00:00:00Z",
			"stargazers_count": 900,
			"topics": [],
		}]}

		original = code_techs_module.requests.get
		try:
			code_techs_module.requests.get = lambda *a, **k: _StubResp(payload)
			leads = _fetch_github_leads({"github_searches": ["free api"], "supply_max_age_days": 120})
		finally:
			code_techs_module.requests.get = original

		self.assertEqual(leads, [])


class TestRedditRateLimitIsNotAFailure(unittest.TestCase):
	"""Reddit answers 429 to almost everything, and that must stay harmless.

    Measured: 10 sequential search.rss calls returned 1x200 and 9x429, and 2s
    spacing returned 0/5. Reddit throttles the IP, not the query, so the old
    `continue` spent the whole budget on certain failures -- which is why only
    r/SideProject ever appeared on the page.
    """

	def test_it_stops_asking_after_a_429(self):
		calls = []

		def fake_get(url, **kwargs):
			calls.append(url)
			if len(calls) == 1:
				return _StubResp(text=_REDDIT_FEED)
			return _StubResp(status_code=429)

		original = code_techs_module.requests.get
		try:
			code_techs_module.requests.get = fake_get
			leads = _fetch_reddit_leads({
				"reddit_subreddits": ["SideProject", "Entrepreneur", "smallbusiness"],
				"reddit_searches": ["free AI API"],
				"max_reddit_requests": 3,
				"reddit_backoff_seconds": 0,
			})
		finally:
			code_techs_module.requests.get = original

		self.assertEqual(len(calls), 2, calls)
		# The successful page still counts; a throttle is not a lost cycle.
		self.assertEqual(len(leads), 1)

	def test_one_query_per_subreddit_so_a_small_budget_spans_several(self):
		seen = []

		def fake_get(url, **kwargs):
			seen.append(url)
			return _StubResp(text=_REDDIT_FEED)

		original = code_techs_module.requests.get
		try:
			code_techs_module.requests.get = fake_get
			_fetch_reddit_leads({
				"reddit_subreddits": ["SideProject", "Entrepreneur", "freelance"],
				"reddit_searches": ["a", "b", "c", "d"],
				"max_reddit_requests": 3,
				"reddit_backoff_seconds": 0,
			})
		finally:
			code_techs_module.requests.get = original

		subreddits = {url.split("/r/")[1].split("/")[0] for url in seen}
		self.assertEqual(len(subreddits), 3, seen)


class TestHnHiringThreadYieldsContractLeads(unittest.TestCase):
	"""The monthly HN hiring thread is the highest-intent free source."""

	_THREAD = {"hits": [{"objectID": "49522897", "title": "Ask HN: Who is hiring? (September 2026)"}]}
	_CHILDREN = {"children": [
		{
			"id": 1,
			"created_at": _hours_ago_iso(20),
			"text": "Noricum | Senior Backend Engineer | REMOTE | Contract | $120-160&#x2F;hr",
		},
		{
			"id": 2,
			"created_at": _hours_ago_iso(20),
			"text": "BigCo | Staff Engineer | ONSITE | Full-time only | $250k",
		},
	]}

	def _fetch(self):
		def fake_get(url, **kwargs):
			return _StubResp(self._CHILDREN if "items/" in url else self._THREAD)

		original = code_techs_module.requests.get
		try:
			code_techs_module.requests.get = fake_get
			return _fetch_hn_hiring_leads({
				"hn_contract_terms": ["contract", "freelance", "part-time"],
				"hn_hiring_max_age_hours": 744,
			})
		finally:
			code_techs_module.requests.get = original

	def test_only_contract_replies_become_leads(self):
		leads = self._fetch()

		self.assertEqual(len(leads), 1)
		self.assertEqual(leads[0]["kind"], "demand")
		self.assertIn("Noricum", leads[0]["buyer"])

	def test_the_stated_rate_survives_html_entities(self):
		# HN serves "$120-160/hr" as "$120-160&#x2F;hr". strip_html used to
		# replace entities with a space, so the rate a human typed came out as
		# "$120-160 hr" and no reader could recognise it as a price.
		lead = self._fetch()[0]
		value, basis, note = _lead_value(lead)

		self.assertEqual(basis, "stated_rate")
		self.assertEqual(value, 120.0)
		self.assertIn("$120-160/hr", note)


class TestLeadsNeedNoNewSecret(unittest.TestCase):
	"""Every lead source is keyless. GITHUB_TOKEN only raises a rate limit."""

	def test_github_search_works_and_sends_no_auth_without_a_token(self):
		headers_seen = []

		def fake_get(url, **kwargs):
			headers_seen.append(kwargs.get("headers") or {})
			return _StubResp({"items": []})

		saved = os.environ.pop("GITHUB_TOKEN", None)
		original = code_techs_module.requests.get
		try:
			code_techs_module.requests.get = fake_get
			_fetch_github_leads({"github_searches": ["free api"]})
		finally:
			code_techs_module.requests.get = original
			if saved is not None:
				os.environ["GITHUB_TOKEN"] = saved

		self.assertTrue(headers_seen)
		self.assertFalse(any("Authorization" in h for h in headers_seen))

	def test_the_hn_hiring_thread_needs_no_key(self):
		headers_seen = []

		def fake_get(url, **kwargs):
			headers_seen.append(kwargs.get("headers") or {})
			return _StubResp({"hits": []})

		original = code_techs_module.requests.get
		try:
			code_techs_module.requests.get = fake_get
			_fetch_hn_hiring_leads({"hn_contract_terms": ["contract"]})
		finally:
			code_techs_module.requests.get = original

		self.assertFalse(any("Authorization" in h for h in headers_seen))


class TestCodexPromptIsMarketSpecific(unittest.TestCase):
	"""The prompt is the field the owner acts on, so it must not invent a price."""

	def _rank_one(self, lead):
		return _rank([lead], {"prompt_top_n": 5, "free_ai_focus": ["free OCR APIs"]},
		             max_items=1, min_score=0)[0]

	def test_it_names_the_real_buyer_and_signal(self):
		op = self._rank_one({
			"title": "Senior Python Data Scraping Engineer (Freelance)",
			"url": "https://example.com/job", "source": "himalayas", "kind": "demand",
			"buyer": "Mindrift", "body": "freelance contract, scraping and data extraction",
			"labels": [], "posted_at": _hours_ago_iso(4),
			"min_salary": 40, "currency": "USD", "salary_period": "hourly",
		})

		self.assertIn("Mindrift", op.codex_prompt)
		self.assertIn("Senior Python Data Scraping Engineer", op.codex_prompt)
		self.assertIn("$40/hr posted", op.codex_prompt)

	def test_with_no_stated_price_it_quotes_no_figure(self):
		op = self._rank_one({
			"title": "Anyone know a tool to convert scanned invoices?",
			"url": "https://example.com/thread", "source": "hacker-news", "kind": "demand",
			"buyer": "", "body": "looking for something to extract invoice data",
			"labels": [], "posted_at": _hours_ago_iso(6),
		})

		self.assertEqual(op.value_basis, "none")
		self.assertIn("no stated price", op.codex_prompt)
		# A prompt that merely omits the price invites the reading model to
		# invent one, rebuilding the fabrication this module just removed.
		self.assertNotIn("$", op.codex_prompt)


class TestDemandLeadsKeepTheirShare(unittest.TestCase):
	"""Tooling must not crowd out the postings where somebody is paying."""

	def test_demand_survives_a_flood_of_higher_scoring_supply(self):
		supply = [{
			"title": f"awesome/free-ai-list-{i}", "url": f"https://github.com/x/{i}",
			"source": "github", "kind": "supply",
			"body": "a free llm api list with a generous free tier, ocr and transcription",
			"labels": [], "posted_at": _hours_ago_iso(1),
		} for i in range(30)]
		demand = [{
			"title": f"Freelance contract role {i}", "url": f"https://example.com/{i}",
			"source": "himalayas", "kind": "demand", "body": "contract work",
			"labels": [], "posted_at": _hours_ago_iso(70),
		} for i in range(5)]

		ranked = _rank(supply + demand, {"min_demand_share": 0.5}, max_items=10, min_score=0)
		kept_demand = [op for op in ranked if op.kind == "demand"]

		self.assertEqual(len(kept_demand), 5)


class TestOutreachDraftIsGone(unittest.TestCase):
	"""Cold outreach is refused in code, so the generator for it must not exist.

    Every live draft quoted a fabricated price ("the fixed price is $4500.00")
    and ended "Payment address (USDT_WALLET_ADDRESS): [redacted]", because
    status.py redacts any env name containing WALLET. Repairing it would mean
    widening that exemption to publish the receive address inside research
    notes for a channel the bot may not use.
    """

	def test_no_lead_carries_an_outreach_draft(self):
		ranked = _rank([{
			"title": "Need a CSV cleanup script", "url": "https://example.com/r",
			"source": "community", "kind": "demand", "body": "looking for help",
			"labels": [], "posted_at": _hours_ago_iso(2),
		}], {"prompt_top_n": 1}, max_items=1, min_score=0)

		self.assertNotIn("outreach_draft", ranked[0].__dict__)

	def test_the_module_exposes_no_draft_builder(self):
		self.assertFalse(hasattr(code_techs_module, "_outreach_draft"))
		self.assertFalse(hasattr(code_techs_module, "_payment_note"))
		# The config block that fed it is gone too, so a later cycle cannot
		# read it back and rebuild the generator around it.
		self.assertNotIn("outreach", code_techs_module._DEFAULT_CONFIG)


class TestLeadStatusPayloadStaysBounded(unittest.TestCase):
	"""status.json is committed hourly, so the lead slice has a size budget.

    Leads were already 36 KB of a 63 KB file (57%) for only 8 leads, because
    each carried a 1.7 KB prompt and a 470 B outreach draft.
    """

	def test_forty_leads_stay_under_thirty_kilobytes(self):
		leads = [{
			"title": f"Freelance contract data engineering role number {i}",
			"url": f"https://example.com/some/reasonably/long/job/url/{i}",
			"source": "himalayas", "kind": "demand", "buyer": f"Company {i}",
			"body": "contract work to transcribe, extract and convert data " * 20,
			"labels": ["data", "contract"], "posted_at": _hours_ago_iso(i),
			"min_salary": 40 + i, "currency": "USD", "salary_period": "hourly",
		} for i in range(40)]

		ranked = _rank(leads, {"prompt_top_n": 10}, max_items=22, min_score=0)
		payload = len(json.dumps([op.__dict__ for op in ranked]))

		self.assertLess(payload, 30_000, f"{payload} bytes")
		# Only the leads worth acting on pay for a prompt.
		self.assertEqual(sum(1 for op in ranked if op.codex_prompt), 10)


class TestFreeAiClassifierNeedsProximity(unittest.TestCase):
	"""An AI word and a "free" word in the same document prove nothing.

    Both halves were substring checks over the whole blob, so bare "ai"
    matched *contain*, *available* and *email*. That is how "I spent a year
    making a Markdown editor for Windows" became a free-AI earning lead.
    """

	def test_an_unrelated_free_product_is_not_a_free_ai_lead(self):
		self.assertFalse(_is_free_ai_lead(
			"i spent a year making a markdown editor for windows and it is free"
		))

	def test_incidental_substrings_do_not_count_as_ai(self):
		self.assertFalse(_is_free_ai_lead(
			"free chair repair available by email in the domain of retail"
		))

	def test_a_real_free_ai_service_still_matches(self):
		self.assertTrue(_is_free_ai_lead("a free llm api with a generous free tier"))
		self.assertTrue(_is_free_ai_lead("free ocr api, no credit card required"))


_REDDIT_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Looking for a free AI API to convert invoices</title>
    <link href="https://www.reddit.com/r/SideProject/comments/abc/x/" />
    <updated>2026-09-08T06:00:00+00:00</updated>
    <content type="html">&lt;p&gt;Need to extract data from scans.&lt;/p&gt;</content>
  </entry>
</feed>"""


class TestWalletEarnings(unittest.TestCase):
	"""Only confirmed on-chain stablecoin holdings count as earned money.

    These cover the *accounting* -- count a deposit once, survive a manual
    withdrawal, hold the last figure through an outage -- so the stub sits at
    the chain read and everything above it is the real code path.
    """

	def _run(self, balances):
		import os
		import bot.status as status_module
		from bot.earning import wallet_assets
		original_fetch = wallet_assets.read_balances
		original_env = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
		queue = list(balances)

		def stub(addr, timeout=20):
			usd = queue.pop(0)
			# None stays None: an unreadable chain, not a balance of zero.
			if usd is None:
				return None
			return {"usd": usd, "stablecoins": {"USDT": usd}, "other_assets": {}}

		wallet_assets.read_balances = stub
		try:
			status = status_module._defaults()
			for _ in balances:
				status_module._snapshot_wallet(status)
				update(status, [])
			return status
		finally:
			wallet_assets.read_balances = original_fetch
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

	def test_main_engine_is_the_free_auto_router(self):
		"""The lead is the free auto-router, so model choice tracks the live
		catalogue instead of a hand-maintained slug that can be withdrawn
		(as stealth/ox-alpha was)."""
		import bot.llm as llm_module
		self.assertEqual(llm_module._MAIN, "openrouter/free")

	def test_paid_auto_router_is_never_used(self):
		"""openrouter/auto bills at the routed model's rate and can select paid
		models. A cycle must never be able to spend credits."""
		import bot.llm as llm_module
		for role, chain in self._chains().items():
			self.assertNotIn("openrouter/auto", chain, role)
			self.assertNotIn("openrouter/auto-beta", chain, role)

	def test_named_fallback_follows_the_router(self):
		"""The router is one upstream service; if it degrades the cycle still
		needs a concrete model to fall back to."""
		import bot.llm as llm_module
		for role, chain in self._chains().items():
			self.assertEqual(chain[1], llm_module._MAIN_NAMED, role)
			self.assertTrue(llm_module._MAIN_NAMED.endswith(":free"))

	def test_every_role_has_a_multi_model_chain(self):
		"""A single-model chain has nothing to fall back to on a rate limit."""
		import bot.llm as llm_module
		for role in ("upgrade", "research", "post"):
			chain = llm_module._OPENROUTER_MODELS_BY_ROLE[role]
			self.assertGreaterEqual(len(chain), 3, role)
			self.assertEqual(len(chain), len(set(chain)), f"{role} has duplicates")
			# free auto-router first: it picks the best zero-cost model per
			# request, and the named models behind it cover it being down.
			self.assertEqual(chain[0], "openrouter/free", role)

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

	def test_empty_response_steps_through_entire_chain(self):
		"""Regression (cycle #1751): a model answering HTTP 200 with an empty
		body used to be returned as a *valid* completion. `complete()` then
		returned on the first model, so the chain never stepped down, and
		`complete_json*` re-sent the same prompt to the same dead model three
		times before failing with `First 200 chars: ''`."""
		import bot.llm as llm_module
		for role in ("upgrade", "research", "post"):
			walked = self._walk(
				role,
				f"{llm_module._EMPTY_RESPONSE_MARKER}: openrouter model x returned no content",
			)
			self.assertEqual(walked, llm_module._OPENROUTER_MODELS_BY_ROLE[role], role)

	def test_empty_completion_is_not_a_valid_response(self):
		"""No caller has a use for "" -- every provider must raise instead of
		coercing a missing completion into a successful empty answer."""
		import bot.llm as llm_module
		for blank in ("", "   ", chr(10) + chr(9), None):
			with self.assertRaises(RuntimeError):
				llm_module._require_text(blank, "openrouter", "some/model")
		self.assertEqual(
			llm_module._require_text("hello", "openrouter", "some/model"), "hello"
		)

	def test_empty_response_recovers_on_the_next_model(self):
		"""The point of the fix: a degraded lead model must cost one request and
		then succeed, not fail the cycle."""
		import bot.llm as llm_module
		tried: list[str] = []

		def fake(self, prompt, system, max_tokens, temperature, model):
			tried.append(model)
			if model == llm_module._MAIN:
				return llm_module._require_text("", "openrouter", model)
			return llm_module.LLMResponse(
				text='{"ok": true}', provider="openrouter", model=model, latency_s=0.0
			)

		real_call, real_sleep = llm_module.LLMClient._call_openrouter, llm_module.time.sleep
		keys = ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "CEREBRAS_API_KEY")
		saved = {k: os.environ.pop(k, None) for k in keys}
		saved_or = os.environ.get("OPENROUTER_API_KEY")
		os.environ["OPENROUTER_API_KEY"] = "test-key"
		llm_module.LLMClient._call_openrouter = fake
		llm_module.time.sleep = lambda *a, **kw: None
		try:
			result = llm_module.LLMClient().complete_json_for_role("upgrade", "hi")
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

		self.assertEqual(result, {"ok": True})
		self.assertEqual(tried, [llm_module._MAIN, llm_module._MAIN_NAMED])

	def test_exhausted_chain_is_not_reprompted(self):
		"""Reprompting only helps unparseable output. Once every provider is
		exhausted there is nothing left to ask, and on the free tier two more
		full chain walks cost 2x the chain against a 50/day ceiling."""
		import bot.llm as llm_module
		tried: list[str] = []

		def fake(self, prompt, system, max_tokens, temperature, model):
			tried.append(model)
			return llm_module._require_text("", "openrouter", model)

		real_call, real_sleep = llm_module.LLMClient._call_openrouter, llm_module.time.sleep
		keys = ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "CEREBRAS_API_KEY")
		saved = {k: os.environ.pop(k, None) for k in keys}
		saved_or = os.environ.get("OPENROUTER_API_KEY")
		os.environ["OPENROUTER_API_KEY"] = "test-key"
		llm_module.LLMClient._call_openrouter = fake
		llm_module.time.sleep = lambda *a, **kw: None
		try:
			with self.assertRaises(ValueError):
				llm_module.LLMClient().complete_json_for_role("upgrade", "hi")
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

		chain = llm_module._OPENROUTER_MODELS_BY_ROLE["upgrade"]
		self.assertEqual(len(tried), len(chain), tried)

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


class TestRejectReasonIsRecorded(unittest.TestCase):
	"""A cycle that publishes nothing must say which gate stopped it.

	Every rejection path used to return a bare None, and run() reported them all
	as "no fresh trending source or LLM available" -- which named sourcing even
	when the source pool was full and the real cause was a gate or the LLM.
	"""

	def setUp(self):
		import bot.earning.articles as A
		self.A = A
		self._picked = A._pick_source
		self._target = A._followup_target
		A._followup_target = lambda status, key: None
		os.environ["DEV_TO_API_KEY"] = "test-key"

	def tearDown(self):
		self.A._pick_source = self._picked
		self.A._followup_target = self._target
		os.environ.pop("DEV_TO_API_KEY", None)

	def test_missing_llm_is_not_reported_as_a_sourcing_failure(self):
		status = {}
		result = self.A.run(None, status)[0]
		self.assertEqual(result["reject_code"], "no_llm")
		self.assertNotIn("trending", result["error"])

	def test_empty_source_pool_reports_no_source(self):
		self.A._pick_source = lambda status: None

		class LLM:
			def complete_json_for_role(self, *a, **k):
				return {"title": "t", "body_markdown": "b"}

		result = self.A.run(LLM(), {})[0]
		self.assertEqual(result["reject_code"], "no_source")

	def test_llm_failure_is_distinguished_from_an_empty_draft(self):
		self.A._pick_source = lambda status: {
			"url": "https://ex.com/a", "title": "T", "summary": "s", "source": "hn"}

		class Boom:
			def complete_json_for_role(self, *a, **k):
				raise RuntimeError("429 rate limited")

		class Empty:
			def complete_json_for_role(self, *a, **k):
				return {}

		self.assertEqual(self.A.run(Boom(), {})[0]["reject_code"], "llm_error")
		self.assertEqual(self.A.run(Empty(), {})[0]["reject_code"], "empty_draft")

	def test_rejects_accumulate_so_a_costly_gate_becomes_visible(self):
		self.A._pick_source = lambda status: None

		class LLM:
			def complete_json_for_role(self, *a, **k):
				return {"title": "t", "body_markdown": "b"}

		status = {}
		for _ in range(3):
			self.A.run(LLM(), status)
		rec = status["article_rejects"]
		self.assertEqual(rec["total"], 3)
		self.assertEqual(rec["counts"]["no_source"], 3)
		self.assertEqual(rec["last_reason"], "no_source")

	def test_every_reject_code_has_human_readable_text(self):
		for code in self.A._REJECTS:
			self.assertTrue(self.A._REJECTS[code].strip())


class TestForceArticlesHonoursItsCount(unittest.TestCase):
	"""`force articles N` must publish N, not silently publish one.

	commands.py parses and clamps N to 1-5 and logs the number, but run() read
	the override only as a truthy cap-bypass flag and always published a single
	article. The owner's count was accepted, logged, and then discarded.
	"""

	def setUp(self):
		import bot.earning.articles as A
		self.A = A
		self._saved = (A._generate_article, A._record_publish, A._refresh_stats,
					   A.devto.publish)
		os.environ["DEV_TO_API_KEY"] = "test-key"
		self.published = []

		def fake_generate(llm, status):
			return {"title": f"T{len(self.published)}",
					"body_markdown": "b", "tags": [], "_source": {}}

		def fake_publish(article, key):
			self.published.append(article["title"])
			return {"platform": "dev.to", "success": True, "estimated_usd": 0.0}

		A._generate_article = fake_generate
		A._record_publish = lambda status, article: None
		A._refresh_stats = lambda status, key: None
		A.devto.publish = fake_publish

	def tearDown(self):
		(self.A._generate_article, self.A._record_publish,
		 self.A._refresh_stats, self.A.devto.publish) = self._saved
		os.environ.pop("DEV_TO_API_KEY", None)

	def test_force_three_publishes_three(self):
		status = {"_overrides": {"force_articles": 3}}
		results = self.A.run(None, status)
		self.assertEqual(len(self.published), 3)
		self.assertEqual(sum(1 for r in results if r.get("success")), 3)

	def test_unforced_cycle_still_publishes_one(self):
		status = {}
		self.A.run(None, status)
		self.assertEqual(len(self.published), 1)

	def test_a_failure_partway_stops_the_forced_batch(self):
		"""A dead source mid-batch must not spin the remaining attempts."""
		calls = {"n": 0}

		def flaky(llm, status):
			calls["n"] += 1
			if calls["n"] >= 2:
				return self.A._reject("no_source")
			return {"title": "T", "body_markdown": "b", "tags": [], "_source": {}}

		self.A._generate_article = flaky
		status = {"_overrides": {"force_articles": 4}}
		results = self.A.run(None, status)
		self.assertEqual(len(self.published), 1)
		self.assertTrue(any(r.get("reject_code") == "no_source" for r in results))
		self.assertEqual(calls["n"], 2)


class TestFailedActionsLogTheirReason(unittest.TestCase):
	"""earnings-log.md must not flatten a failure into 'action recorded'."""

	def test_error_text_reaches_the_log(self):
		import tempfile, pathlib
		from bot import dashboard
		original = dashboard._LOG_FILE
		tmp = pathlib.Path(tempfile.mkdtemp()) / "log.md"
		try:
			dashboard._LOG_FILE = tmp
			dashboard.write_log([{
				"platform": "dev.to", "success": False,
				"error": "unverifiable figures in prose",
			}])
			written = tmp.read_text(encoding="utf-8")
		finally:
			dashboard._LOG_FILE = original
		self.assertIn("unverifiable figures in prose", written)
		self.assertNotIn("action recorded", written)

	def test_successful_action_without_detail_still_logs(self):
		import tempfile, pathlib
		from bot import dashboard
		original = dashboard._LOG_FILE
		tmp = pathlib.Path(tempfile.mkdtemp()) / "log.md"
		try:
			dashboard._LOG_FILE = tmp
			dashboard.write_log([{"platform": "x", "success": True}])
			written = tmp.read_text(encoding="utf-8")
		finally:
			dashboard._LOG_FILE = original
		self.assertIn("action recorded", written)


class TestPayoutAddressValidation(unittest.TestCase):
	"""The address is the one irreversible thing this project publishes.

    USDT sent to a mistyped address is burned -- there is no support desk and no
    reversal. So validation is not a shape check: a regex on
    ``^T[1-9A-HJ-NP-Za-km-z]{33}$`` happily accepts an address with two
    characters transposed, and that address belongs to nobody. These tests pin
    the checksum behaviour that makes a typo detectable.
    """

	# The project's own configured receive address. Public by nature -- it is a
	# receive address, and it already appears masked in status.json.
	REAL = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"

	def test_real_configured_address_is_accepted(self):
		self.assertTrue(payout.valid_tron_address(self.REAL))

	def test_transposed_characters_are_rejected(self):
		swapped = self.REAL[:10] + self.REAL[11] + self.REAL[10] + self.REAL[12:]
		self.assertNotEqual(swapped, self.REAL)
		# Correct length, correct alphabet, correct prefix -- only the checksum
		# catches this one, which is exactly the point.
		self.assertEqual(len(swapped), 34)
		self.assertTrue(swapped.startswith("T"))
		self.assertFalse(payout.valid_tron_address(swapped))

	def test_truncated_address_is_rejected(self):
		self.assertFalse(payout.valid_tron_address(self.REAL[:-1]))

	def test_non_base58_characters_are_rejected(self):
		# 0, O, I and l are excluded from base58 precisely to stop this.
		self.assertFalse(payout.valid_tron_address("T0OIl" + self.REAL[5:]))

	def test_empty_and_garbage_rejected(self):
		for bad in ["", "   ", "not-an-address", "0x1234", "T" * 34]:
			self.assertFalse(payout.valid_tron_address(bad), bad)


class TestKeccakAndEip55(unittest.TestCase):
	"""EIP-55 needs original Keccak-256, not hashlib's SHA3-256.

    NIST changed the padding byte between Keccak's submission and the SHA-3
    standard, so ``hashlib.sha3_256`` produces a different digest and an
    EIP-55 check built on it rejects *every* valid checksummed address. That
    bug was written here first and caught by these vectors before it shipped.
    """

	def test_keccak_matches_known_vectors(self):
		self.assertEqual(
			payout.keccak256(b"").hex(),
			"c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470")
		self.assertEqual(
			payout.keccak256(b"abc").hex(),
			"4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45")

	def test_keccak_differs_from_stdlib_sha3(self):
		# The whole reason this function exists. If these ever match, the
		# implementation has been "simplified" back into the original bug.
		import hashlib as _h
		self.assertNotEqual(payout.keccak256(b"abc"), _h.sha3_256(b"abc").digest())

	def test_keccak_spans_multiple_blocks(self):
		# One absorb block is 136 bytes; a rate-boundary bug only shows above it.
		self.assertEqual(len(payout.keccak256(b"a" * 200)), 32)
		self.assertEqual(
			payout.keccak256(b"a" * 200),
			payout.keccak256(b"a" * 200))

	def test_official_eip55_vectors_accepted(self):
		for address in [
			"0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
			"0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359",
			"0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB",
			"0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb",
		]:
			self.assertTrue(payout.valid_eth_address(address), address)

	def test_broken_eip55_case_rejected(self):
		self.assertFalse(
			payout.valid_eth_address("0x5aAeb6053F3E94C9b9A09f33669435E7Ef1Beaed"))

	def test_uniform_case_address_accepted_without_checksum(self):
		# All-lower carries no checksum, so shape is all there is to check.
		self.assertTrue(
			payout.valid_eth_address("0xdac17f958d2ee523a2206206994597c13d831ec7"))
		self.assertFalse(payout.valid_eth_address("0xdac17f958d2ee523a220"))


class TestPayoutFooter(unittest.TestCase):
	"""The footer is the only automated path from a reader to the wallet."""

	REAL = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"

	def _cfg(self, **over):
		cfg = dict(payout.DEFAULTS)
		cfg.update(over)
		return cfg

	def setUp(self):
		self._saved = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = self.REAL

	def tearDown(self):
		if self._saved is None:
			os.environ.pop("USDT_WALLET_ADDRESS", None)
		else:
			os.environ["USDT_WALLET_ADDRESS"] = self._saved

	def test_disabled_by_default_publishes_nothing(self):
		# Ships off: the footer goes out under the owner's byline, so they opt in.
		self.assertFalse(payout.DEFAULTS["enabled"])
		self.assertEqual(payout.footer(self._cfg()), "")

	def test_enabled_footer_carries_the_exact_address(self):
		block = payout.footer(self._cfg(enabled=True))
		self.assertIn(self.REAL, block)
		self.assertIn("## Support this work", block)
		# Fenced, not inline: a renderer that line-wraps inline text turns an
		# address into a mistyped address.
		self.assertIn("\n" + self.REAL + "\n", block)
		self.assertIn("TRC-20", block)

	def test_invalid_address_omits_footer_entirely(self):
		# Publishing a broken address costs a reader real money, so a bad env
		# value must produce no footer -- never a partial or "best effort" one.
		os.environ["USDT_WALLET_ADDRESS"] = self.REAL[:-2] + "xy"
		self.assertEqual(payout.footer(self._cfg(enabled=True)), "")

	def test_unset_address_omits_footer(self):
		os.environ.pop("USDT_WALLET_ADDRESS", None)
		self.assertEqual(payout.footer(self._cfg(enabled=True)), "")

	def test_add_footer_appends_once_not_twice(self):
		article = {"body_markdown": "## Intro\n\nBody text.\n"}
		cfg = self._cfg(enabled=True)
		once = payout.add_footer(dict(article), cfg)
		twice = payout.add_footer(dict(once), cfg)
		self.assertEqual(once["body_markdown"], twice["body_markdown"])
		self.assertEqual(twice["body_markdown"].count("Support this work"), 1)

	def test_add_footer_never_raises(self):
		# A footer is an enhancement. Losing the day's article over it would
		# trade real reach for nothing.
		self.assertIsInstance(payout.add_footer({}, self._cfg(enabled=True)), dict)
		self.assertIsInstance(
			payout.add_footer({"body_markdown": None}, self._cfg(enabled=True)), dict)

	def test_status_snapshot_distinguishes_off_from_unconfigured(self):
		off = payout.status_snapshot(self._cfg(enabled=False))
		self.assertFalse(off["live"])
		self.assertIn("disabled", off["blocked_reason"])

		os.environ.pop("USDT_WALLET_ADDRESS", None)
		unset = payout.status_snapshot(self._cfg(enabled=True))
		self.assertFalse(unset["live"])
		self.assertIn("not set", unset["blocked_reason"])

		os.environ["USDT_WALLET_ADDRESS"] = "T" + "x" * 33
		bad = payout.status_snapshot(self._cfg(enabled=True))
		self.assertFalse(bad["live"])
		self.assertIn("checksum-valid", bad["blocked_reason"])

		os.environ["USDT_WALLET_ADDRESS"] = self.REAL
		live = payout.status_snapshot(self._cfg(enabled=True))
		self.assertTrue(live["live"])
		self.assertIsNone(live["blocked_reason"])
		# Masked only. status.json is committed and the dashboard is public.
		self.assertNotIn(self.REAL, str(live))

	def test_snapshot_never_leaks_the_full_address(self):
		live = payout.status_snapshot(self._cfg(enabled=True))
		self.assertEqual(live["address_masked"], "TFTNsf…9KbY")


class TestPayoutRunsAfterQualityGates(unittest.TestCase):
	"""The footer must not be able to help an article pass its own gates.

    It adds a heading and an untagged fence. Attached before the gates, it
    would pad the word count and satisfy structural checks the model's own
    draft failed -- so a too-thin article would publish on boilerplate. This is
    why it is appended inside ``devto.publish`` and not in ``_finalize``.
    """

	REAL = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"

	def setUp(self):
		self._saved = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = self.REAL
		self._cfg_on = dict(payout.DEFAULTS)
		self._cfg_on["enabled"] = True

	def tearDown(self):
		if self._saved is None:
			os.environ.pop("USDT_WALLET_ADDRESS", None)
		else:
			os.environ["USDT_WALLET_ADDRESS"] = self._saved

	def test_gates_judge_the_draft_not_the_footer(self):
		thin = {"body_markdown": "## One\n\n" + "word " * 20}
		before = len(thin["body_markdown"].split())
		withfooter = payout.add_footer(dict(thin), self._cfg_on)
		# The footer does add words...
		self.assertGreater(len(withfooter["body_markdown"].split()), before)
		# ...which is exactly why the gate has to run on the draft. If a future
		# refactor moves the footer into _finalize, this article gets padded
		# toward min_words by boilerplate instead of being rejected.
		problems = articles_module._format_problems(thin["body_markdown"])
		self.assertTrue(any("too short" in p for p in problems))

	def test_publish_attaches_footer_without_mutating_caller(self):
		# devto.publish copies the article before appending, so a failed publish
		# cannot leave a footer on the dict a retry re-sends.
		sent = {}

		class _Resp:
			@staticmethod
			def raise_for_status():
				return None

			@staticmethod
			def json():
				return {"url": "https://dev.to/x/y"}

		def fake_post(url, headers=None, json=None, timeout=None):
			sent["body"] = json["article"]["body_markdown"]
			return _Resp()

		original_post = devto_module.requests.post
		original_config = payout.config
		try:
			devto_module.requests.post = fake_post
			payout.config = lambda: self._cfg_on
			article = {"title": "T", "body_markdown": "## A\n\nprose\n", "tags": ["python"]}
			result = devto_module.publish(article, "key")
			self.assertTrue(result["success"])
			self.assertIn(self.REAL, sent["body"])
			# The caller's dict is untouched.
			self.assertNotIn(self.REAL, article["body_markdown"])
			# Publishing a post still reports no revenue: money is on-chain only.
			self.assertEqual(result["estimated_usd"], 0.0)
		finally:
			devto_module.requests.post = original_post
			payout.config = original_config


class TestPayoutPublicSnapshot(unittest.TestCase):
	"""The dashboard tip box needs the whole address, not the masked one.

    ``status_snapshot`` is a diagnostic and stays masked -- the owner only needs
    to recognise which wallet is configured. The tip box is not a diagnostic:
    a reader cannot pay ``TFTNsf…9KbY``, so publishing the masked form there
    would rebuild the exact structural zero this module closed -- a receive
    path that looks present and cannot receive, failing silently because the
    page still looks finished.
    """

	REAL = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"

	def _cfg(self, **over):
		cfg = {"enabled": True, "address_env": "TEST_PAYOUT_ADDR",
			   "heading": "Support this work", "note": "note", "show_network": True}
		cfg.update(over)
		return cfg

	def test_exposes_full_address_when_footer_is_shipping(self):
		with mock.patch.dict(os.environ, {"TEST_PAYOUT_ADDR": self.REAL}):
			snap = payout.public_snapshot(self._cfg())
		self.assertEqual(snap["address"], self.REAL)
		self.assertNotIn("…", snap["address"])
		# The asset label is derived from the balance reader's table, so the tip
		# box cannot name a token the wallet would report as $0.00. Asserted
		# against that table rather than a frozen string.
		self.assertEqual(snap["asset"], payout.accepted_assets(snap["network"]))
		self.assertIn("USDT", snap["asset"])
		self.assertIn("Tron", snap["network"])

	def test_empty_when_disabled(self):
		"""Never advertise a path the articles are not publishing."""
		with mock.patch.dict(os.environ, {"TEST_PAYOUT_ADDR": self.REAL}):
			self.assertEqual(payout.public_snapshot(self._cfg(enabled=False)), {})

	def test_empty_when_address_invalid(self):
		"""A broken address omits the tip box for the same reason it omits the
        footer: a post with no ask earns nothing, but a bad address costs a
        reader real money.
        """
		with mock.patch.dict(os.environ, {"TEST_PAYOUT_ADDR": self.REAL[:-1] + "X"}):
			self.assertEqual(payout.public_snapshot(self._cfg()), {})

	def test_empty_when_address_unset(self):
		with mock.patch.dict(os.environ, {"TEST_PAYOUT_ADDR": ""}):
			self.assertEqual(payout.public_snapshot(self._cfg()), {})

	def test_agrees_with_footer_on_whether_path_is_live(self):
		"""The two surfaces must never disagree. If one publishes the address,
        so does the other; if one omits it, so does the other.
        """
		for env, enabled in ((self.REAL, True), (self.REAL, False),
							 ("", True), ("garbage", True)):
			with mock.patch.dict(os.environ, {"TEST_PAYOUT_ADDR": env}):
				cfg = self._cfg(enabled=enabled)
				self.assertEqual(
					bool(payout.footer(cfg)), bool(payout.public_snapshot(cfg)),
					f"footer and tip box disagree for env={env!r} enabled={enabled}")


class TestPublicAddressSurvivesRedaction(unittest.TestCase):
	"""``_secret_names`` matches any env var containing "WALLET".

    That is right everywhere else -- a receive address has no business in a log
    line or a research note -- but it also catches ``USDT_WALLET_ADDRESS``, so
    the tip box would publish ``[redacted]``. This was a real bug found before
    shipping: the dashboard renders a finished-looking tip box that cannot take
    a tip. These tests pin the narrow exemption and, more importantly, that it
    stays narrow.
    """

	REAL = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
	FAKE_KEY = "sk-ant-secretkeyvalue0123456789"

	def _sanitize(self, status):
		env = {"USDT_WALLET_ADDRESS": self.REAL, "ANTHROPIC_API_KEY": self.FAKE_KEY}
		with mock.patch.dict(os.environ, env):
			return status_mod.sanitize_for_git(status)

	def test_tip_address_is_published_whole(self):
		out = self._sanitize({"payout_public": {"address": self.REAL,
												"network": "TRC-20 (Tron)"}})
		self.assertEqual(out["payout_public"]["address"], self.REAL)

	def test_address_elsewhere_is_still_redacted(self):
		"""The exemption is one field, not the address globally."""
		out = self._sanitize({
			"payout_public": {"address": self.REAL},
			"errors": [f"failed for {self.REAL}"],
			"suggestions": [{"text": f"send to {self.REAL}"}],
		})
		self.assertEqual(out["payout_public"]["address"], self.REAL)
		self.assertNotIn(self.REAL, out["errors"][0])
		self.assertNotIn(self.REAL, out["suggestions"][0]["text"])

	def test_api_keys_are_still_redacted(self):
		out = self._sanitize({
			"payout_public": {"address": self.REAL},
			"note": f"key={self.FAKE_KEY}",
		})
		self.assertNotIn(self.FAKE_KEY, out["note"])

	def test_no_tip_field_means_nothing_restored(self):
		"""With no tip box, the address gets no special treatment anywhere."""
		out = self._sanitize({"note": f"addr {self.REAL}"})
		self.assertNotIn("payout_public", out)
		self.assertNotIn(self.REAL, out["note"])

	def test_masked_diagnostic_is_left_alone(self):
		out = self._sanitize({"payout": {"address_masked": "TFTNsf…9KbY",
										 "live": True}})
		self.assertEqual(out["payout"]["address_masked"], "TFTNsf…9KbY")


class TestAttribution(unittest.TestCase):
	"""Attribution must never invent revenue.

    The wallet decides whether money arrived; this module only writes down what
    was published when it did. A TRC-20 transfer carries no memo, so the record
    is correlation and is labelled as such -- claiming per-post attribution
    would be the fabrication this project has already deleted twice.
    """

	def _status(self, received=0.0):
		return {
			"wallet": {"last_received_usd": received,
					   "last_received_at": "2026-09-04T10:00:00+00:00",
					   "network": "TRC-20"},
			"article_stats": {"count": 10, "total_views": 1838,
							  "best_title": "Nitter alternatives",
							  "best_url": "https://dev.to/x", "best_views": 1562,
							  "winning_tags": ["twitter", "privacy"]},
			"article_interest": {"best_archetype": "problem-workaround"},
			"payout": {"network": "TRC-20 (Tron)"},
		}

	def test_no_record_without_money(self):
		"""The common case: nothing arrived, so nothing is claimed."""
		status = self._status(received=0.0)
		self.assertIsNone(attribution.record_receipt(status))
		self.assertNotIn("attribution", status)

	def test_negative_or_missing_amount_records_nothing(self):
		for amount in (0.0, -5.0, None):
			status = self._status()
			status["wallet"]["last_received_usd"] = amount
			self.assertIsNone(attribution.record_receipt(status))

	def test_records_context_on_real_receipt(self):
		status = self._status(received=2.5)
		rec = attribution.record_receipt(status)
		self.assertEqual(rec["amount_usd"], 2.5)
		self.assertEqual(rec["context"]["best_archetype"], "problem-workaround")
		self.assertEqual(rec["context"]["posts_live"], 10)

	def test_confidence_is_never_better_than_correlated(self):
		"""No memo exists on-chain, so nothing here may claim proof."""
		status = self._status(received=1.0)
		rec = attribution.record_receipt(status)
		self.assertEqual(rec["confidence"], "correlated")
		self.assertIn("not proof", status["attribution"]["note"])

	def test_amount_comes_from_the_wallet_not_a_guess(self):
		status = self._status(received=7.125)
		attribution.record_receipt(status)
		self.assertEqual(status["attribution"]["total_attributed_usd"], 7.125)

	def test_totals_accumulate_across_receipts(self):
		status = self._status(received=1.0)
		attribution.record_receipt(status)
		status["wallet"]["last_received_usd"] = 3.0
		attribution.record_receipt(status)
		book = status["attribution"]
		self.assertEqual(book["receipt_count"], 2)
		self.assertEqual(book["total_attributed_usd"], 4.0)
		self.assertEqual(book["by_archetype"][0]["count"], 2)
		self.assertEqual(book["by_archetype"][0]["usd"], 4.0)

	def test_sample_size_travels_with_every_total(self):
		"""One receipt is not a trend; count is the only thing that says so."""
		status = self._status(received=5.0)
		attribution.record_receipt(status)
		for row in status["attribution"]["by_archetype"]:
			self.assertIn("count", row)
		for row in status["attribution"]["by_tag"]:
			self.assertIn("count", row)

	def test_history_is_bounded(self):
		status = self._status(received=1.0)
		with mock.patch.object(attribution, "config",
							   lambda: {"enabled": True, "history_limit": 3}):
			for _ in range(6):
				attribution.record_receipt(status)
		self.assertEqual(len(status["attribution"]["receipts"]), 3)

	def test_survives_missing_reach_data(self):
		"""A receipt during a dev.to outage is still recorded, with less around it."""
		status = {"wallet": {"last_received_usd": 1.0}}
		rec = attribution.record_receipt(status)
		self.assertIsNotNone(rec)
		self.assertEqual(rec["context"]["posts_live"], 0)
		self.assertIsNone(rec["context"]["best_archetype"])

	def test_never_raises_on_malformed_status(self):
		"""Bookkeeping must not be able to take down a cycle."""
		self.assertIsNone(attribution.record_receipt({"wallet": "not-a-dict"}))

	def test_disabled_records_nothing(self):
		status = self._status(received=1.0)
		with mock.patch.object(attribution, "config", lambda: {"enabled": False}):
			self.assertIsNone(attribution.record_receipt(status))

	def test_summary_reports_the_empty_case(self):
		summary = attribution.summary({})
		self.assertEqual(summary["receipt_count"], 0)
		self.assertEqual(summary["total_attributed_usd"], 0.0)
		self.assertIsNone(summary["top_archetype"])


class TestPublishedStatsCarryTheBody(unittest.TestCase):
	"""The backfill can only see an ask it is given the body to look for.

    ``fetch_published`` builds each post dict from an explicit field list, and
    ``body_markdown`` was not on it. Nothing raised: ``needs_footer`` read the
    missing body as "", hit its own empty-body guard, and answered False for
    every post on the account. So the backfill filtered its entire candidate
    list to nothing and reported ``remaining: 0`` and ``nothing_to_do`` -- the
    exact reading the doctrine tells the owner means "every reader can pay" --
    while not one published post carried a footer.

    Every other backfill test builds its post dicts by hand with a body, so
    they all passed throughout. This one pins the seam between the two modules.
    """

	BODY = "# T\n\nreal prose, no ask anywhere.\n"

	def _fetch(self, payload):
		class _Resp:
			status_code = 200
			content = b"[]"

			@staticmethod
			def raise_for_status():
				return None

			@staticmethod
			def json():
				return payload

		original = devto_stats.requests.get
		try:
			devto_stats.requests.get = lambda *a, **k: _Resp()
			return devto_stats.fetch_published("key")
		finally:
			devto_stats.requests.get = original

	def test_body_markdown_survives_the_fetch(self):
		posts = self._fetch([{
			"id": 1, "title": "T", "url": "https://dev.to/a/b",
			"page_views_count": 10, "body_markdown": self.BODY,
		}])
		self.assertEqual(posts[0]["body_markdown"], self.BODY)

	def test_a_footerless_post_reaches_the_backfill_as_one(self):
		"""End to end across the seam: fetched post -> needs_footer -> True."""
		saved = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
		cfg = dict(payout.DEFAULTS)
		cfg["enabled"] = True
		try:
			posts = self._fetch([{
				"id": 1, "title": "T", "url": "https://dev.to/a/b",
				"page_views_count": 1722, "body_markdown": self.BODY,
			}])
			self.assertTrue(backfill.needs_footer(posts[0], cfg))
		finally:
			if saved is None:
				os.environ.pop("USDT_WALLET_ADDRESS", None)
			else:
				os.environ["USDT_WALLET_ADDRESS"] = saved

	def test_missing_body_still_degrades_safely(self):
		"""A response genuinely lacking the field must not crash the loop."""
		posts = self._fetch([{"id": 1, "title": "T", "page_views_count": 3}])
		self.assertEqual(posts[0]["body_markdown"], "")


class TestBackfillPutsTheAskWhereTheReadersAre(unittest.TestCase):
	"""The footer only ever ran on POST, so it missed every existing post.

    At the time this was written that was 85% of the audience: 1,949 lifetime
    views across 11 posts, 1,652 of them on one evergreen article, none of them
    carrying any way to pay. This suite pins the behaviour that makes editing
    live posts safe enough to do unattended.
    """

	REAL = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"

	def setUp(self):
		self._saved = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = self.REAL
		self._cfg_on = dict(payout.DEFAULTS)
		self._cfg_on["enabled"] = True

	def tearDown(self):
		if self._saved is None:
			os.environ.pop("USDT_WALLET_ADDRESS", None)
		else:
			os.environ["USDT_WALLET_ADDRESS"] = self._saved

	def _post(self, **over):
		post = {"id": 1, "title": "T", "page_views": 100,
				"body_markdown": "# T\n\nreal prose here.\n"}
		post.update(over)
		return post

	# ── what to touch ───────────────────────────────────────────────────────

	def test_post_without_footer_needs_one(self):
		self.assertTrue(backfill.needs_footer(self._post(), self._cfg_on))

	def test_post_that_already_has_the_footer_is_left_alone(self):
		body = payout.add_footer(
			{"body_markdown": "# T\n\nprose\n"}, self._cfg_on)["body_markdown"]
		self.assertFalse(
			backfill.needs_footer(self._post(body_markdown=body), self._cfg_on))

	def test_front_matter_post_is_never_touched(self):
		"""Forem re-reads title and tags from front matter on save, and clears
        the tag list first. Editing such a post can rewrite the title and wipe
        the tags of the account's best article, so it is skipped instead.
        """
		body = "---\ntitle: Real Title\ntags: python, linux\n---\n\n# T\n\nprose\n"
		self.assertFalse(
			backfill.needs_footer(self._post(body_markdown=body), self._cfg_on))

	def test_empty_body_is_skipped(self):
		"""``me/published`` returning no body must never blank a live post."""
		self.assertFalse(
			backfill.needs_footer(self._post(body_markdown=""), self._cfg_on))
		self.assertFalse(
			backfill.needs_footer(self._post(body_markdown=None), self._cfg_on))

	# ── what it sends ───────────────────────────────────────────────────────

	def _run_with(self, posts, put=None, cfg=None):
		sent = []

		class _Resp:
			status_code = 200
			content = b"{}"

			@staticmethod
			def raise_for_status():
				return None

			@staticmethod
			def json():
				return {"url": "https://dev.to/x/y"}

		def fake_put(url, headers=None, json=None, timeout=None):
			sent.append({"url": url, "headers": headers, "json": json})
			return (put or _Resp)()

		status = {}
		original = devto_module.requests.put
		try:
			devto_module.requests.put = fake_put
			with mock.patch.object(payout, "config", lambda: self._cfg_on), \
					mock.patch.object(backfill, "config",
									  lambda: cfg or dict(backfill.DEFAULTS)):
				action = backfill._run(status, "key", published=posts)
		finally:
			devto_module.requests.put = original
		return action, sent, status

	def test_appends_the_same_footer_and_keeps_the_original_prose(self):
		action, sent, _ = self._run_with([self._post()])
		self.assertTrue(action["success"])
		self.assertEqual(action["updated"], 1)
		body = sent[0]["json"]["article"]["body_markdown"]
		self.assertIn(self.REAL, body)
		# The post's own words survive untouched -- this never rewrites prose.
		self.assertIn("real prose here.", body)

	def test_sends_only_the_body_so_title_and_tags_are_not_re_asserted(self):
		_, sent, _ = self._run_with([self._post()])
		self.assertEqual(list(sent[0]["json"]["article"].keys()), ["body_markdown"])

	def test_targets_the_right_article_with_the_existing_key(self):
		_, sent, _ = self._run_with([self._post(id=4242)])
		self.assertEqual(sent[0]["url"], "https://dev.to/api/articles/4242")
		self.assertEqual(sent[0]["headers"]["api-key"], "key")

	def test_highest_traffic_post_is_fixed_first(self):
		"""The distribution is top-heavy, so the order is the whole value."""
		posts = [self._post(id=1, page_views=10),
				 self._post(id=2, page_views=1652),
				 self._post(id=3, page_views=100)]
		_, sent, _ = self._run_with(posts)
		self.assertEqual([s["url"].rsplit("/", 1)[-1] for s in sent],
						 ["2", "3", "1"])

	def test_respects_max_per_cycle(self):
		cfg = dict(backfill.DEFAULTS)
		cfg["max_per_cycle"] = 1
		_, sent, _ = self._run_with(
			[self._post(id=1), self._post(id=2)], cfg=cfg)
		self.assertEqual(len(sent), 1)

	# ── idempotency: it must be safe to run every hour, forever ─────────────

	def test_never_footers_the_same_post_twice(self):
		"""The cycle is hourly and this runs on every one of them. A second
        footer on a live post would be visible to every reader.
        """
		post = self._post()
		_, sent, status = self._run_with([post])
		self.assertEqual(len(sent), 1)
		# The post now carries a footer, as dev.to would report it back.
		updated = self._post(body_markdown=sent[0]["json"]["article"]["body_markdown"])
		_, sent2, _ = self._run_with([updated])
		self.assertEqual(sent2, [])
		self.assertFalse(backfill.needs_footer(updated, self._cfg_on))

	def test_completed_backlog_reports_success_and_writes_no_action(self):
		body = payout.add_footer(
			{"body_markdown": "# T\n\nprose\n"}, self._cfg_on)["body_markdown"]
		with mock.patch.object(payout, "config", lambda: self._cfg_on), \
				mock.patch.dict(os.environ, {"DEV_TO_API_KEY": "key"}), \
				mock.patch.object(backfill.devto_stats, "fetch_published",
								  lambda k: [self._post(body_markdown=body)]):
			self.assertEqual(backfill.run(None, {}), [])

	# ── failure must cost nothing ───────────────────────────────────────────

	def test_a_failed_update_stops_rather_than_hammering_the_api(self):
		class _Boom:
			status_code = 429
			content = b""

			@staticmethod
			def raise_for_status():
				raise RuntimeError("429 rate limited")

			@staticmethod
			def json():
				return {}

		action, sent, status = self._run_with(
			[self._post(id=1), self._post(id=2), self._post(id=3)], put=_Boom)
		self.assertEqual(len(sent), 1)
		self.assertFalse(action["success"])
		self.assertEqual(action["updated"], 0)
		self.assertIn("1", status["backfill"]["skipped"])

	def test_unparseable_response_after_a_landed_write_is_not_a_failure(self):
		"""``raise_for_status`` passed, so the edit is already live. Calling
        that a failure would abort the rest of the run over a post that was in
        fact fixed, and mark it for a pointless retry.
        """
		class _Weird:
			status_code = 200
			content = b"<html>not json</html>"

			@staticmethod
			def raise_for_status():
				return None

			@staticmethod
			def json():
				raise ValueError("no json")

		action, sent, _ = self._run_with(
			[self._post(id=1), self._post(id=2)], put=_Weird)
		self.assertEqual(len(sent), 2)
		self.assertTrue(action["success"])
		self.assertEqual(action["updated"], 2)

	def test_publishes_nothing_when_the_footer_is_not_live(self):
		"""Gated on the same switch as the footer. If no ask is shipping to new
        readers, this must not invent one for old ones.
        """
		off = dict(payout.DEFAULTS)
		off["enabled"] = False
		with mock.patch.object(payout, "config", lambda: off):
			action = backfill._run({}, "key", published=[self._post()])
		self.assertFalse(action["success"])
		self.assertEqual(action["updated"], 0)

	def test_never_raises(self):
		self.assertIsInstance(backfill._run({}, "key", published="not-a-list"), dict)
		self.assertIsInstance(backfill.run(None, None), list)

	def test_reports_no_revenue_because_money_is_on_chain_only(self):
		"""An ask is not a receipt, here exactly as on a fresh publish."""
		action, _, _ = self._run_with([self._post()])
		self.assertEqual(action["estimated_usd"], 0.0)

	def test_makes_no_llm_call(self):
		"""A model rewriting a post that already earns traffic can degrade it,
        and no gate downstream runs on live posts.
        """
		source = Path("bot/earning/backfill.py").read_text(encoding="utf-8")
		for banned in ("complete_json", "llm.complete", ".complete("):
			self.assertNotIn(banned, source)

	def test_matches_the_product_contract_the_orchestrator_calls(self):
		"""``bot.main._module`` imports by name and calls ``run(llm, status)``,
        returning a list. A signature mismatch would surface only in a live
        cycle, and ``bot/main.py`` is protected from evolution -- so the
        product has to fit the orchestrator, not the other way round.
        """
		import importlib
		import inspect

		mod = importlib.import_module("bot.earning.backfill")
		params = list(inspect.signature(mod.run).parameters)
		self.assertEqual(params[:2], ["llm", "status"])
		# Callable positionally, exactly as _module does it, and list-returning.
		with mock.patch.dict(os.environ, {"DEV_TO_API_KEY": ""}):
			self.assertIsInstance(mod.run(None, {}), list)

	def test_is_registered_in_phase_4(self):
		"""A product the orchestrator never calls is dead code, and this one
        looks identical to a working feature from the outside: the footer is
        live, the module exists, and the back catalogue silently stays unasked.
        """
		main_src = Path("bot/main.py").read_text(encoding="utf-8")
		self.assertIn('_module("backfill"', main_src)


class TestReceiptCheckObservesFromOutside(unittest.TestCase):
	"""The verifier must not share the writer's view of the world.

    Every other signal about the receive path is produced by the same code
    whose work it reports. ``backfill`` derives ``remaining`` from the same
    ``fetch_published`` call it acts on, so when that call dropped
    ``body_markdown`` the work and the claim about the work were wrong together
    and agreed with each other -- ``remaining: 0`` while no post on the account
    carried a footer, for fourteen cycles.

    These pin the property that makes this module worth having: it re-reads the
    published article through the unauthenticated endpoint, so it cannot
    inherit the writer's blind spot.
    """

	FOOTERED = "# T\n\nprose\n\n## Support this work\n\n```\nTADDR\n```\n"
	BARE = "# T\n\nprose, no ask anywhere.\n"

	def _patched(self, bodies):
		"""Patch the public GET so each id returns the body mapped to it."""
		class _Resp:
			def __init__(self, payload, code=200):
				self._payload = payload
				self.status_code = code

			def raise_for_status(self):
				if self.status_code >= 400:
					raise RuntimeError("http %d" % self.status_code)

			def json(self):
				return self._payload

		def _get(url, **kwargs):
			art_id = int(str(url).rstrip("/").split("/")[-1])
			if art_id not in bodies:
				return _Resp({}, 404)
			return _Resp({"body_markdown": bodies[art_id]})

		return mock.patch.object(receipt_check.requests, "get", _get)

	def test_it_never_reads_the_body_it_was_handed(self):
		"""The caller's body is ignored; only the published one counts.

        This is the whole design. If the module trusted the post dict it was
        given, it would be reading the same possibly-wrong data the backfill
        already read, and would confirm the backfill's mistakes rather than
        catch them.
        """
		# The handed-in post claims a footer. The live article has none.
		posts = [{"id": 7, "title": "T", "page_views": 999,
				  "body_markdown": self.FOOTERED}]
		with self._patched({7: self.BARE}):
			found = receipt_check.verify(posts, payout.config(), 5)
		self.assertEqual(found["without_footer"], 1)
		self.assertEqual(found["with_footer"], 0)

	def test_it_sends_no_api_key(self):
		"""Authenticating would read through the serializer that caused the bug.

        ``GET /api/articles/{id}`` is public and returns ``body_markdown``.
        Sending the key would route the read through the account's own
        authenticated view -- the one the backfill already trusts.
        """
		seen = {}

		class _Resp:
			status_code = 200

			@staticmethod
			def raise_for_status():
				return None

			@staticmethod
			def json():
				return {"body_markdown": "x"}

		def _get(url, **kwargs):
			seen.update(kwargs.get("headers") or {})
			return _Resp()

		with mock.patch.object(receipt_check.requests, "get", _get):
			receipt_check.fetch_live_body(1)
		joined = " ".join(k.lower() for k in seen)
		self.assertNotIn("api-key", joined)
		self.assertNotIn("authorization", joined)

	def test_unreachable_is_not_reported_as_missing(self):
		"""An unobservable post is not a post without a footer.

        Collapsing "could not read" into "has no ask" is the mirror image of
        the original bug, which collapsed "could not read" into "is fine". Both
        directions produce a confident wrong answer; the honest third state is
        ``unreachable``.
        """
		posts = [{"id": 404, "title": "gone", "page_views": 5}]
		with self._patched({}):
			found = receipt_check.verify(posts, payout.config(), 5)
		self.assertEqual(found["unreachable"], 1)
		self.assertEqual(found["without_footer"], 0)
		self.assertEqual(found["missing"], [])

	def test_absent_body_field_is_unreachable_not_footerless(self):
		"""A serializer that stops returning the field must not raise a false
        alarm on every post -- exactly the failure mode that hid the real bug,
        pointed the other way.
        """
		class _Resp:
			status_code = 200

			@staticmethod
			def raise_for_status():
				return None

			@staticmethod
			def json():
				return {"title": "no body field here"}

		with mock.patch.object(receipt_check.requests, "get",
							   lambda *a, **k: _Resp()):
			self.assertIsNone(receipt_check.fetch_live_body(1))

	def test_highest_traffic_first(self):
		"""The view distribution is top-heavy, so the busiest post is most of
        the answer and must be inside the per-cycle cap.
        """
		posts = [
			{"id": 1, "title": "quiet", "page_views": 3},
			{"id": 2, "title": "evergreen", "page_views": 1722},
		]
		with self._patched({1: self.BARE, 2: self.BARE}):
			found = receipt_check.verify(posts, payout.config(), 1)
		self.assertEqual(found["checked"], 1)
		self.assertEqual(found["missing"][0]["title"], "evergreen")


class TestReceiptCheckContradictsABadClaim(unittest.TestCase):
	"""The comparison that would have caught the fourteen-cycle outage."""

	BARE = "# T\n\nprose, no ask.\n"

	def _run(self, status, bodies):
		class _Resp:
			def __init__(self, payload):
				self._payload = payload

			@staticmethod
			def raise_for_status():
				return None

			def json(self):
				return self._payload

		def _get(url, **kwargs):
			art_id = int(str(url).rstrip("/").split("/")[-1])
			return _Resp({"body_markdown": bodies[art_id]})

		posts = [{"id": i, "title": "t%d" % i, "page_views": 100}
				 for i in bodies]
		with mock.patch.object(receipt_check.requests, "get", _get):
			return receipt_check._run(status, "key", published=posts)

	def test_it_disagrees_when_the_backfill_claims_completion(self):
		"""``remaining: 0`` beside a footerless published post is the exact
        state that read as "every reader can pay" for cycles #1760-#1773.
        """
		status = {"backfill": {"remaining": 0, "updated_total": 0}}
		self._run(status, {1: self.BARE})
		state = status["receipt_check"]
		self.assertEqual(state["without_footer"], 1)
		self.assertIs(state["agrees_with_backfill"], False)
		self.assertEqual(state["last_reason"], "footer_missing")

	def test_a_missing_ask_is_surfaced_as_an_action(self):
		"""Silence on this path is what made the outage invisible; the owner
        has to see it in the cycle log.
        """
		status = {"backfill": {"remaining": 0}}
		action = self._run(status, {1: self.BARE})
		self.assertFalse(action.get("_quiet"))
		self.assertIn("no way to pay", action.get("error", ""))

	def test_a_verified_path_stays_quiet(self):
		"""The ordinary good state must not pad last_earning with noise every
        hour, or the warning above stops standing out.
        """
		footered = "# T\n\nprose\n\n## Support this work\n\n```\nTADDR\n```\n"
		status = {"backfill": {"remaining": 0}}
		action = self._run(status, {1: footered})
		self.assertTrue(action.get("_quiet"))
		self.assertEqual(status["receipt_check"]["last_reason"], "all_verified")

	def test_it_never_reports_revenue(self):
		"""Observing an ask is not receiving money. On-chain or nothing."""
		status = {}
		action = self._run(status, {1: self.BARE})
		self.assertEqual(action["estimated_usd"], 0.0)

	def test_it_never_raises(self):
		"""Measurement must not be able to take down a cycle."""
		def _boom(*a, **k):
			raise RuntimeError("dev.to is down")

		with mock.patch.object(receipt_check.requests, "get", _boom):
			action = receipt_check._run(
				{}, "key",
				published=[{"id": 1, "title": "t", "page_views": 1}])
		self.assertIsInstance(action, dict)
		self.assertEqual(action["estimated_usd"], 0.0)


class TestReceiptCheckIsWiredIn(unittest.TestCase):
	"""A verifier the orchestrator never calls verifies nothing -- and looks
    identical from the outside to one that passes every cycle.
    """

	def test_run_matches_the_product_signature(self):
		import importlib
		import inspect

		mod = importlib.import_module("bot.earning.receipt_check")
		params = list(inspect.signature(mod.run).parameters)
		self.assertEqual(params[:2], ["llm", "status"])
		with mock.patch.dict(os.environ, {"DEV_TO_API_KEY": ""}):
			self.assertIsInstance(mod.run(None, {}), list)

	def test_is_registered_in_phase_4(self):
		main_src = Path("bot/main.py").read_text(encoding="utf-8")
		self.assertIn('_module("receipt_check"', main_src)

	def test_it_runs_after_the_backfill(self):
		"""It must observe the repairs this cycle made, not the state before
        them, or it reports a stale gap the backfill just closed.
        """
		main_src = Path("bot/main.py").read_text(encoding="utf-8")
		self.assertLess(main_src.index('_module("backfill"'),
						main_src.index('_module("receipt_check"'))

	def test_it_makes_no_llm_call(self):
		"""Asking a model whether a footer is present would make the check
        itself unreliable, and the comparison is exact.
        """
		src = Path("bot/earning/receipt_check.py").read_text(encoding="utf-8")
		for banned in ("complete_json", "llm.complete", ".complete("):
			self.assertNotIn(banned, src)

	def test_it_never_writes_to_devto(self):
		"""Repair belongs to the backfill. A verifier that also fixes things is
        once again reporting on its own work.
        """
		src = Path("bot/earning/receipt_check.py").read_text(encoding="utf-8")
		self.assertNotIn("requests.put", src)
		self.assertNotIn("requests.post", src)
		self.assertNotIn("update_body", src)


class TestWalletReadsEveryStablecoin(unittest.TestCase):
	"""The footer publishes a Tron *address*, which accepts any TRC-20.

    Reading only the USDT contract reported a USDC or USDD tip as $0.00 --
    Principle 1's structural zero rebuilt at the measurement stage, and failing
    in the dangerous direction: with `received_total_usd` stuck at zero,
    `attribution.record_receipt` never fires and the doctrine's checklist says
    "the problem is reach" while money is actually sitting in the wallet.
    """

	def _account(self, trc20, trx_sun=0):
		return {"balance": trx_sun, "trc20": trc20}

	def _read(self, account):
		from bot.earning import wallet_assets
		original = wallet_assets._fetch_account
		wallet_assets._fetch_account = lambda addr, timeout=20: account
		try:
			return wallet_assets.read_balances("TFTNsfyomKrnUutRjBTGVULp19ByW29KbY")
		finally:
			wallet_assets._fetch_account = original

	def test_usdc_tip_is_counted(self):
		"""The exact loss this module was written for: a non-USDT stablecoin."""
		result = self._read(self._account([
			{"TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8": "5000000"},   # 5 USDC
		]))
		self.assertEqual(result["usd"], 5.0)
		self.assertEqual(result["stablecoins"], {"USDC": 5.0})

	def test_stablecoins_are_summed_together(self):
		result = self._read(self._account([
			{"TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t": "2000000"},   # 2 USDT
			{"TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8": "3000000"},   # 3 USDC
		]))
		self.assertEqual(result["usd"], 5.0)

	def test_usdd_uses_its_own_18_decimals(self):
		"""USDD has 18 decimals, USDT and USDC have 6. The single-asset reader
        divided everything by 1e6, which would report a 1 USDD tip as one
        trillion dollars.
        """
		result = self._read(self._account([
			{"TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn": "1" + "0" * 18},  # 1 USDD
		]))
		self.assertEqual(result["usd"], 1.0)
		self.assertEqual(result["stablecoins"], {"USDD": 1.0})

	def test_trx_is_reported_but_never_valued(self):
		"""Pricing TRX needs a feed, and a feed is an estimate -- Principle 4.
        A priced TRX balance would also drift every cycle while no money moved.
        """
		result = self._read(self._account([], trx_sun=100_000_000))  # 100 TRX
		self.assertEqual(result["usd"], 0.0)
		self.assertEqual(result["other_assets"], {"TRX": 100.0})

	def test_unknown_token_is_never_valued(self):
		"""An unpriced TRC-20 must not be counted as a dollar."""
		result = self._read(self._account([
			{"TXYZunknowncontractaddressthatisnotastable": "9000000"},
		]))
		self.assertEqual(result["usd"], 0.0)

	def test_unreadable_chain_is_none_not_zero(self):
		"""A chain outage reported as $0.00 would look like a withdrawal."""
		self.assertIsNone(self._read(None))

	def test_never_activated_address_is_zero_not_unreadable(self):
		"""An address nobody has ever paid is a real zero, not an outage."""
		from bot.earning import wallet_assets
		original = wallet_assets._fetch_account
		wallet_assets._fetch_account = lambda addr, timeout=20: {}
		try:
			result = wallet_assets.read_balances("TFTNsfyomKrnUutRjBTGVULp19ByW29KbY")
		finally:
			wallet_assets._fetch_account = original
		self.assertEqual(result["usd"], 0.0)

	def test_it_uses_no_price_feed_and_no_llm(self):
		"""Both would turn a measured balance into an estimate.

        Asserted on the code's reachable hosts and calls rather than on prose,
        because the docstring legitimately discusses prices at length in order
        to explain why none is fetched.
        """
		src = Path("bot/earning/wallet_assets.py").read_text(encoding="utf-8")
		urls = re.findall(r"https?://([^/\"\s]+)", src)
		self.assertEqual(set(urls), {"api.trongrid.io"})
		for banned in ("coingecko", "binance", "complete_json", "llm.", "cmc"):
			self.assertNotIn(banned, src.lower())

	def test_it_needs_no_new_secret(self):
		"""Principle 2 row 1: TronGrid's account endpoint is keyless."""
		src = Path("bot/earning/wallet_assets.py").read_text(encoding="utf-8")
		self.assertNotIn("API_KEY", src)
		self.assertNotIn("getenv", src)

	def test_stablecoin_decimals_are_per_token(self):
		"""Pins that no future edit collapses these back to a shared constant."""
		from bot.earning import wallet_assets
		decimals = {t["symbol"]: t["decimals"]
					for t in wallet_assets.STABLECOINS.values()}
		self.assertEqual(decimals["USDT"], 6)
		self.assertEqual(decimals["USDC"], 6)
		self.assertEqual(decimals["USDD"], 18)


class TestStablecoinTipReachesEarnings(unittest.TestCase):
	"""The seam, not the modules (Principle 3d).

    Every unit above can pass while the wallet snapshot still calls the old
    single-asset reader -- which is precisely the class of bug that hid for
    fourteen cycles. This drives the real `_snapshot_wallet` and asserts a USDC
    tip arrives as revenue *and* triggers attribution.
    """

	def _cycle(self, accounts):
		import bot.status as status_module
		from bot.earning import wallet_assets
		original = wallet_assets._fetch_account
		original_env = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
		queue = list(accounts)
		wallet_assets._fetch_account = lambda addr, timeout=20: queue.pop(0)
		try:
			status = status_module._defaults()
			for _ in accounts:
				status_module._snapshot_wallet(status)
			return status
		finally:
			wallet_assets._fetch_account = original
			if original_env is None:
				os.environ.pop("USDT_WALLET_ADDRESS", None)
			else:
				os.environ["USDT_WALLET_ADDRESS"] = original_env

	def test_usdc_tip_becomes_recorded_revenue(self):
		"""Before this change the same tip left received_total_usd at 0.0."""
		empty = {"balance": 0, "trc20": []}
		paid = {"balance": 0,
				"trc20": [{"TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8": "7000000"}]}
		status = self._cycle([empty, paid])
		wallet = status["wallet"]
		self.assertEqual(wallet["confirmed_usd"], 7.0)
		self.assertEqual(wallet["received_total_usd"], 7.0)
		self.assertEqual(wallet["last_received_usd"], 7.0)

	def test_a_recorded_receipt_triggers_attribution(self):
		"""attribution fires on wallet.last_received_usd, so a tip invisible to
        the balance reader was also invisible to the funnel measurement.
        """
		from bot.earning import attribution
		empty = {"balance": 0, "trc20": []}
		paid = {"balance": 0,
				"trc20": [{"TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8": "4000000"}]}
		status = self._cycle([empty, paid])
		record = attribution.record_receipt(status)
		self.assertIsNotNone(record)
		self.assertEqual(record["amount_usd"], 4.0)
		self.assertEqual(record["confidence"], "correlated")

	def test_trx_only_tip_does_not_invent_revenue(self):
		"""A TRX tip is visible, but never as a dollar figure."""
		empty = {"balance": 0, "trc20": []}
		trx = {"balance": 100_000_000, "trc20": []}
		status = self._cycle([empty, trx])
		wallet = status["wallet"]
		self.assertEqual(wallet["received_total_usd"], 0.0)
		self.assertEqual(wallet["other_assets"], {"TRX": 100.0})

	def test_asset_breakdown_reaches_status(self):
		paid = {"balance": 0,
				"trc20": [{"TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t": "3000000"}]}
		status = self._cycle([paid])
		self.assertEqual(status["wallet"]["stablecoins"], {"USDT": 3.0})

	def test_address_still_never_persisted(self):
		"""The receive address must stay masked in the committed status.json."""
		import bot.status as status_module
		paid = {"balance": 0,
				"trc20": [{"TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t": "1000000"}]}
		status = self._cycle([paid])
		blob = json.dumps(status_module.sanitize_for_git(status))
		self.assertNotIn("TFTNsfyomKrnUutRjBTGVULp19ByW29KbY", blob)

	def test_one_chain_read_per_cycle(self):
		"""Balance and breakdown come from a single fetch.

        Two fetches would send identical hourly requests to TronGrid, and could
        report a balance and a breakdown taken from different reads.
        """
		import bot.status as status_module
		from bot.earning import wallet_assets
		calls = []
		original = wallet_assets._fetch_account
		original_env = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"

		def counted(addr, timeout=20):
			calls.append(addr)
			return {"balance": 0, "trc20": []}

		wallet_assets._fetch_account = counted
		try:
			status_module._snapshot_wallet(status_module._defaults())
		finally:
			wallet_assets._fetch_account = original
			if original_env is None:
				os.environ.pop("USDT_WALLET_ADDRESS", None)
			else:
				os.environ["USDT_WALLET_ADDRESS"] = original_env
		self.assertEqual(len(calls), 1)


class TestAskMatchesWhatTheWalletCounts(unittest.TestCase):
	"""The footer must name exactly the assets the balance reader counts.

    Naming too few turns away money the address would have accepted -- the
    footer said "USDT" while sitting on a Tron address that takes any TRC-20,
    so a reader holding USDC read it as "wrong token" and left.

    Naming too many is worse: the tip arrives and is reported as $0.00, which
    is the silent loss this whole change exists to close. So the two are
    derived from one table rather than maintained in two places.
    """

	def _footer(self):
		import os
		from bot.earning import payout
		original = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
		try:
			return payout.footer({"enabled": True,
								  "address_env": "USDT_WALLET_ADDRESS",
								  "heading": "Support this work",
								  "note": "n", "show_network": True})
		finally:
			if original is None:
				os.environ.pop("USDT_WALLET_ADDRESS", None)
			else:
				os.environ["USDT_WALLET_ADDRESS"] = original

	def test_every_counted_asset_is_named_in_the_ask(self):
		from bot.earning import wallet_assets
		footer = self._footer()
		for token in wallet_assets.STABLECOINS.values():
			self.assertIn(token["symbol"], footer)

	def test_the_ask_names_no_asset_the_wallet_ignores(self):
		"""A named-but-uncounted token would arrive and read as $0.00."""
		from bot.earning import payout, wallet_assets
		counted = {t["symbol"] for t in wallet_assets.STABLECOINS.values()}
		label = payout.accepted_assets("TRC-20 (Tron)")
		named = {p.strip() for p in label.replace(" or ", ",").split(",")}
		self.assertEqual(named, counted)

	def test_erc20_ask_stays_usdt_only(self):
		"""_fetch_erc20_usdt reads only the USDT contract on that chain, so the
        ask must not promise more than the meter reads.
        """
		from bot.earning import payout
		self.assertEqual(payout.accepted_assets("ERC-20 (Ethereum)"), "USDT")

	def test_note_names_no_single_asset(self):
		"""The label states the tokens; a second mention only goes stale."""
		from bot.earning import payout
		self.assertNotIn("USDT", payout.DEFAULTS["note"])

	def test_address_is_still_the_only_thing_in_the_fence(self):
		"""A wrapped or annotated address is a mistyped address."""
		footer = self._footer()
		fenced = footer.split("```")[1].strip()
		self.assertEqual(fenced, "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY")

	def test_dashboard_tip_box_names_the_same_assets(self):
		"""The tip card and the published footer must not disagree."""
		import os
		from bot.earning import payout
		original = os.environ.get("USDT_WALLET_ADDRESS")
		os.environ["USDT_WALLET_ADDRESS"] = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
		try:
			public = payout.public_snapshot({
				"enabled": True, "address_env": "USDT_WALLET_ADDRESS",
				"heading": "Support this work", "note": "n"})
		finally:
			if original is None:
				os.environ.pop("USDT_WALLET_ADDRESS", None)
			else:
				os.environ["USDT_WALLET_ADDRESS"] = original
		self.assertEqual(public["asset"], payout.accepted_assets("TRC-20 (Tron)"))
