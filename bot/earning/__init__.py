"""Earning modules.

Products (each owns a ``run(llm, status)`` the orchestrator calls):
  ``articles``    -- one deep dev.to article per day, plus follow-ups
  ``newsletter``  -- a weekly dev.to digest of several stories
  ``backfill``    -- puts the tip footer on posts published before it existed
  ``code_techs``  -- free-AI earning opportunity queue (research only)
  ``mrr_ideas``   -- recurring-revenue idea triage (research only)
  ``attribution`` -- on-chain receipt ledger keyed to publishing context

Support (no ``run``; imported by the products):
  ``_shared``     -- config loading, cadence, and feed parsing used by all
  ``devto``       -- the dev.to publish call and the gates every post passes
  ``trending``    -- sources fresh stories from free public feeds
  ``devto_stats`` -- reads this account's own dev.to reach numbers

``bot.main`` imports the products lazily via ``importlib``; these re-exports
are for tests and ad-hoc use.
"""
from .articles import run as articles_run
from .attribution import record_receipt as attribution_record
from .attribution import summary as attribution_summary
from .backfill import run as backfill_run
from .code_techs import run as code_techs_run
from .mrr_ideas import run as mrr_ideas_run
from .newsletter import run as newsletter_run

__all__ = [
	"articles_run",
	"attribution_record",
	"attribution_summary",
	"backfill_run",
	"code_techs_run",
	"mrr_ideas_run",
	"newsletter_run",
]