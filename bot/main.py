"""
E-Evolve — Hourly Pulse Orchestrator
Entry point: python -m bot.main

Phases:
  0. Init LLM
  1. Status   — load state, detect active features
  2. Commands — read owner commands
  3. Evolve   — skipped; Codex owns code changes
  4. Research — refresh suggestion-only research queues
  5. Update   — save status, dashboard, commit
"""
from __future__ import annotations

import importlib
import json
import logging
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
	datefmt="%H:%M:%S",
)
log = logging.getLogger("e-evolve")

# Load .env for local development (no-op in CI)
try:
	from dotenv import load_dotenv
	load_dotenv()
except ImportError:
	pass


def main() -> int:
	_hr("E-Evolve hourly pulse")
	t0     = datetime.now(timezone.utc)
	errors: list[str] = []

	# ── 0. LLM ────────────────────────────────────────────────────────────────
	try:
		from bot.llm import LLMClient
		llm = LLMClient()
	except RuntimeError as exc:
		log.critical("Cannot start: %s", exc)
		return 1   # Fatal — fail the workflow so the owner notices

	# ── 1. Status ─────────────────────────────────────────────────────────────
	_hr("Phase 1 — Status")
	import bot.status as _st
	status = _st.load()
	status = _st.snapshot(status)
	if _code_techs_enabled():
		if "code_techs" not in status.get("active_features", []):
			status.setdefault("active_features", []).append("code_techs")
		status["inactive_features"] = [
			f for f in status.get("inactive_features", [])
			if f != "code_techs"
		]
	status["llm_provider"] = llm.provider
	# Populate per-role provider map for dashboard display
	from bot.llm import ROLE_PROVIDER
	status["llm_roles"] = {
		role: p for role, p in ROLE_PROVIDER.items()
		if role in ("upgrade", "research", "post") and getattr(llm, f"_{p}_key", "")
	}

	# ── 2. Commands ───────────────────────────────────────────────────────────
	_hr("Phase 2 — Commands")
	import bot.commands as _cmd
	status = _cmd.apply(_cmd.read(), status)
	ov: dict = status.get("_overrides", {})

	# ── 3. Evolve ─────────────────────────────────────────────────────────────
	_hr("Phase 3 — Evolution")
	import bot.git_utils as _git

	import bot.evolution as _evo

	if ov.get("skip_evolution"):
		log.info("Evolution skipped by owner command")
		evo = {
			"summary":           "Skipped by owner command",
			"changes_applied":   [],
			"suggestions":       status.get("suggestions", []),
			"version_bumped_to": status.get("version"),
			"error":             None,
		}
	elif not _evo.enabled():
		log.info("Evolution disabled (config/strategy.json evolution.enabled=false)")
		evo = {
			"summary":           "Skipped: evolution.enabled is false in config/strategy.json",
			"changes_applied":   [],
			"suggestions":       status.get("suggestions", []),
			"version_bumped_to": status.get("version"),
			"error":             None,
		}
	else:
		try:
			evo = _evo.run(llm, status)
		except Exception as exc:
			# Evolution must never take the cycle down: research and publishing
			# still have to run even when a code proposal blows up.
			msg = f"[EVOLUTION FAIL] {exc}"
			log.exception("Evolution raised")
			errors.append(msg)
			evo = {
				"summary":           f"Evolution failed: {exc}"[:200],
				"changes_applied":   [],
				"suggestions":       status.get("suggestions", []),
				"version_bumped_to": status.get("version"),
				"error":             str(exc)[:500],
			}
		if evo.get("branch"):
			log.info(
				"Evolution proposal on branch %s (%d file(s)) — review and merge to apply",
				evo["branch"], len(evo.get("changes_applied", [])),
			)
		if evo.get("error"):
			errors.append(f"[EVOLUTION] {evo['error']}")

	status["last_evolution_branch"] = evo.get("branch")
	status["evolution_pending_review"] = bool(evo.get("branch"))

	status["last_evolution"] = evo
	if evo.get("version_bumped_to"):
		status["version"] = evo["version_bumped_to"]
	active_secrets = {
		s for f in status.get("active_features", [])
		for s in _st.FEATURE_MAP.get(f, [])
	}
	if evo.get("suggestions"):
		status["suggestions"] = [
			sg for sg in evo["suggestions"]
			if not sg.get("secret_needed") or sg["secret_needed"] not in active_secrets
		]
	else:
		status["suggestions"] = [
			sg for sg in status.get("suggestions", [])
			if not sg.get("secret_needed") or sg["secret_needed"] not in active_secrets
		]


	# ── 4. Research / suggestions ────────────────────────────────────────────
	_hr("Phase 4 — Research")
	actions: list[dict] = []

	status["operation_mode"] = "research_and_article_publishing"
	status["external_action_policy"] = {
		"mode": "research_and_article_publishing",
		"allowed": [
			"RAG", "research", "market analysis", "suggestions", "drafts",
			"article publishing (dev.to)",
		],
		"blocked": ["social posting", "trading", "minting", "payouts"],
	}
	if ov.get("blocked_action_commands"):
		log.warning(
			"Ignored action commands still blocked by policy: %s",
			", ".join(ov["blocked_action_commands"]),
		)

	# Independent code-tech opportunity queue. This is suggestion-only: it may
	# search and rank opportunities, but it must not comment, post, trade, mint,
	# publish, or move funds.
	if _code_techs_enabled():
		actions += _module("code_techs", llm, status, errors)

	# Recurring-revenue idea triage. Suggestion-only: it scores business models
	# against this stack's real constraints and records the ones it must refuse.
	# Self-throttles to mrr_ideas.refresh_hours so it costs ~0.5 LLM calls/day.
	actions += _module("mrr_ideas", llm, status, errors)

	# Article publishing to dev.to. Runs only when DEV_TO_API_KEY is set; the
	# module rate-limits itself to max_articles_per_cycle per day.
	actions += _module("articles", llm, status, errors)

	# Newsletter digest to dev.to. Same key, same policy; the module self-throttles
	# to newsletter.min_interval_hours so the hourly pulse publishes one per week.
	actions += _module("newsletter", llm, status, errors)

	# Retrofit the tip footer onto posts published before the footer existed.
	# Runs after the publishing products so it sees this cycle's post too, and
	# makes no LLM call. Most of this account's readers are on the back
	# catalogue, and until this runs they are being shown no way to pay.
	actions += _module("backfill", llm, status, errors)

	if not actions:
		log.warning(
			"No actions ran this cycle.\n"
			"Add or refresh LLM keys for research and article drafting.\n"
			"Set DEV_TO_API_KEY to enable article and newsletter publishing.\n"
			"Social posting, trading, minting, and payouts remain disabled by policy."
		)

	# ── 5. Update ─────────────────────────────────────────────────────────────
	_hr("Phase 5 — State Update")
	import bot.earnings as _earn
	import bot.dashboard as _dash

	status = _earn.update(status, actions)
	cycle_usd = status["earnings"]["last_cycle_usd"]
	status["last_earning"] = {"actions": actions, "total_usd": cycle_usd}

	elapsed = round((datetime.now(timezone.utc) - t0).total_seconds())
	status["last_cycle_seconds"] = elapsed
	status["errors"]             = errors[-20:]
	status.pop("_overrides", None)   # don't persist runtime-only key

	_st.save(status)

	try:
		_dash.write_log(actions)
		_dash.write_html(status)
	except Exception as exc:
		log.error("Dashboard write failed: %s", exc)

	git_result = _git.commit(
		f"📊 cycle #{status['total_runs']} +${cycle_usd:.4f} {elapsed}s",
		paths=[
			"status.json", "earnings-log.md", "docs/index.html",
			"docs/status.json", "docs/earnings-log.md", "command.txt",
			"docs/code-tech-opportunities.md",
			"docs/mrr-ideas.md",
		],
	)
	if not git_result["success"]:
		log.error("[GIT FAIL] state commit: %s", git_result["error"])

	_hr(f"Done | v{status['version']} | {llm.provider} | "
		f"+${cycle_usd:.4f} | {elapsed}s | {len(errors)} err")
	return 0   # Always 0 — partial failures must not break the hourly schedule


# ── Module runner ─────────────────────────────────────────────────────────────

def safe_main() -> int:
	"""Run the pulse without letting an unexpected crash fail the scheduler."""
	try:
		code = main()
		if code != 0:
			_record_crash(RuntimeError(f"pulse exited with code {code}"))
		return 0
	except Exception as exc:
		log.critical("Unhandled pulse crash: %s", exc)
		log.debug(traceback.format_exc())
		try:
			_record_crash(exc)
		except Exception as record_exc:
			log.error("Crash recording failed: %s", record_exc)
		return 0


def _record_crash(exc: Exception) -> None:
	"""Persist a short crash note so the dashboard shows why the cycle degraded."""
	import bot.status as _st
	import bot.dashboard as _dash
	import bot.git_utils as _git

	status = _st.load()
	status["last_run"] = datetime.now(timezone.utc).isoformat()
	status["errors"] = (
		[f"Unhandled pulse crash: {exc}"] + list(status.get("errors", []))
	)[:20]
	status["last_evolution"] = {
		"summary": f"Pulse crash before completion: {str(exc)[:300]}",
		"changes_applied": [],
		"suggestions": status.get("suggestions", []),
		"version_bumped_to": status.get("version"),
		"error": str(exc)[:500],
	}
	_st.save(status)
	_dash.write_html(status)
	_git.commit(
		"fix(pulse): record unhandled crash state",
		paths=["status.json", "docs/status.json", "docs/index.html"],
	)


def _module(name: str, llm: Any, status: dict, errors: list) -> list[dict]:
	"""Run one earning module with full exception isolation."""
	log.info("▶ %s", name)
	try:
		mod    = importlib.import_module(f"bot.earning.{name}")
		result = mod.run(llm, status)
		return result if isinstance(result, list) else []
	except Exception as exc:
		msg = f"{name}: {exc}"
		log.error("Module '%s' crashed: %s", name, exc)
		log.debug(traceback.format_exc())
		errors.append(msg)
		return [{"platform": name, "success": False, "error": str(exc)[:200]}]


def _code_techs_enabled() -> bool:
	"""Return whether the independent code-tech opportunity flow should run."""
	raw = os.getenv("CODE_TECH_EARN_ENABLED", "").strip().lower()
	if raw in {"0", "false", "no", "off"}:
		return False
	if raw in {"1", "true", "yes", "on"}:
		return True
	try:
		cfg = json.loads(Path("config/strategy.json").read_text(encoding="utf-8"))
		return bool(cfg.get("code_techs", {}).get("enabled", True))
	except Exception:
		return True


# ── Formatting helpers ────────────────────────────────────────────────────────

def _hr(text: str) -> None:
	bar = "─" * max(0, 60 - len(text))
	log.info("─── %s %s", text, bar)


if __name__ == "__main__":
	sys.exit(safe_main())
