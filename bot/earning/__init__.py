"""Earning modules.

Products (each owns a ``run(llm, status)`` the orchestrator calls):
  ``articles``       -- one deep dev.to article per day, plus follow-ups
  ``newsletter``     -- a weekly dev.to digest of several stories
  ``backfill``       -- puts the tip footer on posts published before it existed
  ``code_techs``     -- free-AI earning opportunity queue (research only)
  ``mrr_ideas``      -- recurring-revenue idea triage (research only)
  ``receipts``       -- receipt book reader, records on-chain receipts
  ``receipt_check``  -- independent footer-verification loop

Support (no ``run``; imported by the products):
  ``_shared``        -- config loading, cadence, and feed parsing used by all
  ``devto``          -- the dev.to publish call and the gates every post passes
  ``trending``       -- sources fresh stories from free public feeds
  ``devto_stats``    -- reads this account's own dev.to reach numbers
  ``attribution``    -- correlates receipts with publishing context
  ``payout``         -- renders the support footer and wallet address
  ``wallet_assets``  -- reads on-chain USDT balance

``bot.main`` imports the products lazily via ``importlib``; these re-exports
are for tests and ad-hoc use.
"""
from .articles import run as articles_run
from .backfill import run as backfill_run
from .code_techs import run as code_techs_run
from .mrr_ideas import run as mrr_ideas_run
from .newsletter import run as newsletter_run
from .receipts import run as receipts_run
from .receipt_check import run as receipt_check_run

__all__ = [
	"articles_run",
	"backfill_run",
	"code_techs_run",
	"mrr_ideas_run",
	"newsletter_run",
	"receipts_run",
	"receipt_check_run",
]