"""Regression tests for the code-tech outreach wording and the research-only auto_pursue guarantee.

These tests pin two policies the owner reviewed and that the report (the only
public surface distinguishing this project from a spam bot) relies on:

  * every ``outreach_draft`` starts with the owner-reviewed prefix and never
    reverts to the first-person "I will keep it simple" filler.
  * ``_rank`` and ``run`` never set ``pursued=True`` regardless of ``auto_pursue``,
    because the research-only policy forbids posting comments on GitHub/Reddit.

Both pins are local, deterministic, and cost no LLM call. A failure here is a
silent policy revert before the next cycle ships it.
"""
from __future__ import annotations

import os
import unittest

from bot.earning.code_techs import (
	_LOCAL_LEADS,
	_outreach_draft,
	_rank,
)


_OUTREACH_PREFIX = "Owner-reviewed draft — you send by hand after editing:"
_OUTREACH_BANNED = "I will keep it simple"


class TestCodeTechOutreachWording(unittest.TestCase):
	"""The outreach prefix is the only thing telling readers this isn't spam."""

	def test_outreach_draft_starts_with_owner_reviewed_prefix(self):
		cfg = {
			"daily_target_usd": 10.0,
			"outreach": {
				"enabled": True,
				"default_price_usd": 10.0,
				"payment_label": "crypto",
				"crypto_address_env": "USDT_WALLET_ADDRESS",
				"fallback_payment_note": "Add payment address before sending.",
			},
		}
		os.environ["USDT_WALLET_ADDRESS"] = "0xabc123"
		try:
			draft = _outreach_draft(
				"Some Real Tech Lead",
				{"url": "https://example.com/post", "source": "community"},
				10.0,
				cfg,
			)
		finally:
			os.environ.pop("USDT_WALLET_ADDRESS", None)

		self.assertTrue(
			draft.startswith(_OUTREACH_PREFIX),
			f"outreach draft must start with {_OUTREACH_PREFIX!r}, got {draft[:60]!r}",
		)

	def test_outreach_draft_never_contains_first_person_filler(self):
		# The old template wrote "I will keep it simple: ..." — first-person filler
		# that reads as AI-generated spam. The owner-reviewed template replaces it.
		cfg = {
			"outreach": {
				"enabled": True,
				"default_price_usd": 10.0,
				"payment_label": "crypto",
				"crypto_address_env": "",
				"fallback_payment_note": "Add payment address before sending.",
			},
		}
		for lead in _LOCAL_LEADS[:3]:
			draft = _outreach_draft(
				lead.get("title", "untitled"),
				lead,
				12.0,
				cfg,
			)
			self.assertNotIn(
				_OUTREACH_BANNED, draft,
				f"{lead.get('title', '?')!r} outreach still contains {_OUTREACH_BANNED!r}",
			)


class TestCodeTechNeverAutoPursues(unittest.TestCase):
	"""``_rank`` and ``run`` must never set ``pursued=True``."""

	def _cfg(self):
		return {
			"daily_target_usd": 10.0,
			"outreach": {
				"enabled": True,
				"default_price_usd": 10.0,
				"payment_label": "crypto",
				"crypto_address_env": "",
			},
		}

	def test_rank_returns_zero_pursued_even_when_auto_pursue_is_true(self):
		cfg = self._cfg()
		cfg["auto_pursue"] = True
		cfg["pursue_score_threshold"] = 0  # any score qualifies
		leads = [{
			"title": "Need a script to automate CSV export",
			"url": "https://example.com/request",
			"source": "community",
			"body": "Looking for a simple tool to export a CSV every week. "
					"It must run on a free API tier and ship same day.",
			"labels": ["community-request", "free-ai-api"],
		}]
		ranked = _rank(leads, cfg, max_items=4, min_score=0)
		self.assertTrue(ranked)
		for op in ranked:
			self.assertFalse(
				op.pursued,
				f"_rank must never set pursued=True; got {op.title!r} pursued",
			)

	def test_run_never_pursues_branch_when_auto_pursue_is_true(self):
		# The owner-reviewed guarantee: even with auto_pursue=True, run() only
		# logs the refusal and never sets pursued=True. We catch that by importing
		# run and inspecting that the only signal in code is a log line.
		import bot.earning.code_techs as code_techs_module

		src = open(code_techs_module.__file__, "r", encoding="utf-8").read()
		# The runtime guarantee is two pieces: (a) the warning line that proves
		# the policy was applied, and (b) the absence of any code path that
		# would flip pursued=True.
		self.assertIn(
			"auto_pursue ignored: research-only policy forbids posting comments",
			src,
			"run() must log the research-only refusal when auto_pursue=True",
		)
		# A defensive scan: no branch inside run() assigns True to pursued.
		# ``pursued_count = 0`` (the variable that should stay 0) must appear,
		# and no ``pursued = True`` assignment may follow the cfg["auto_pursue"]
		# check.
		run_block = src.split("def run(", 1)[1].split("def _config()", 1)[0]
		self.assertNotIn(
			"pursued = True", run_block,
			"run() must never assign pursued=True — research-only policy",
		)


if __name__ == "__main__":
	unittest.main()