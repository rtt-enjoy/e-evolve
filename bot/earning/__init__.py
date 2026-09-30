"""Earning modules.

Products (each owns a ``run(llm, status)`` the orchestrator calls):
  ``articles``    \u2014 one deep dev.to article per day, plus follow-ups
  ``newsletter``  \u2014 a weekly dev.to digest of several stories
  ``backfill``    \u2014 puts the tip footer on posts published before it existed
  ``code_techs``  \u2014 free-AI earning opportunity queue (research only)
  ``mrr_ideas``   \u2014 recurring-revenue idea triage (research only)
  ``repo_ask``    \u2014 places the receive address in the repo itself

Support (no ``run``; imported by the products):
  ``_shared``     \u2014 config loading, cadence, and feed parsing used by all
  ``devto``       \u2014 the dev.to publish call and the gates every post passes
  ``trending``    \u2014 sources fresh stories from free public feeds
  ``devto_stats`` \u2014 reads this account's own dev.to reach numbers

``bot.main`` imports the products lazily via ``importlib``; these re-exports
are for tests and ad-hoc use.
"""
from .articles import run as articles_run
from .backfill import run as backfill_run
from .code_techs import run as code_techs_run
from .mrr_ideas import run as mrr_ideas_run
from .newsletter import run as newsletter_run
from .repo_ask import run as repo_ask_run

__all__ = [
	"articles_run",
	"backfill_run",
	"code_techs_run",
	"mrr_ideas_run",
	"newsletter_run",
	"repo_ask_run",
]