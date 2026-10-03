"""
Dashboard data publisher.

The interactive dashboard UI lives in frontend/ and is built with Vite into
docs/ for GitHub Pages. Python owns the backend-facing data contract:

  - docs/status.json
  - docs/earnings-log.md
  - docs/daily-summary.md

If the React build has not been generated yet, write a helpful fallback shell
so GitHub Pages still has a useful index.html.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_LOG_FILE = Path("earnings-log.md")
_HTML_FILE = Path("docs/index.html")
_PUBLIC_STATUS_FILE = Path("docs/status.json")
_PUBLIC_LOG_FILE = Path("docs/earnings-log.md")
_PUBLIC_DAILY_SUMMARY_FILE = Path("docs/daily-summary.md")


def write_log(actions: list[dict]) -> None:
	"""Append this cycle's completed actions to earnings-log.md."""
	if not actions:
		return

	s = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
	lines = [f"\n### {ts}\n"]

	for action in actions:
		ok = action.get("success", False)
		icon = "[ok]" if ok else "[fail]"
		platform = action.get("platform", "?")

		if "title" in action:
			url = action.get("url", "")
			title = str(action.get("title", ""))[:60]
			link = f"[{title}]({url})" if url else title
			est = float(action.get("estimated_usd", 0) or 0)
			lines.append(f"- {icon} **{platform}**: {link} (est. ${est:.2f})")

		elif "side" in action:
			side = action.get("side", "")
			symbol = action.get("symbol", "")
			if side in ("BUY", "SELL"):
				val = float(action.get("value_usd", 0) or 0)
				lines.append(f"- {icon} **{platform}** {side} {symbol} - ${val:.2f}")
			elif side == "HOLD":
				lines.append(f"- [hold] **{platform}** {symbol} - HOLD")
			else:
				err = str(action.get("error", ""))[:80]
				lines.append(f"- [fail] **{platform}** {symbol} - {err}")

		elif "thread_length" in action:
			url = action.get("url", "#")
			topic = str(action.get("topic", "thread"))[:50]
			n = action.get("thread_length", 0)
			lines.append(f"- {icon} **{platform}** [{topic}]({url}) ({n} tweets)")

		elif "metadata_uri" in action:
			tx = action.get("tx_hash") or "log-only"
			uri = str(action.get("metadata_uri", ""))[:60]
			lines.append(f"- {icon} **{platform}** NFT tx=`{tx}` uri={uri}")

		else:
			err = str(action.get("error", "")).strip()
			if not ok and err:
				lines.append(f"- {icon} **{platform}**: {err[:120]}")
			else:
				lines.append(f"- {icon} **{platform}** action recorded")

	with _LOG_FILE.open("a", encoding="utf-8") as handle:
		handle.write("\n".join(lines) + "\n")

	log.info("earnings-log.md updated (%d actions)", len(actions))


def write_daily_summary(status: dict[str, Any]) -> None:
	"""Write a concise daily earnings summary for quick dashboard scanning."""
	summary_lines = [
		"# Daily Earnings Summary – " + datetime.now(timezone.utc).date().isoformat(),
		"",
	]

	# Earnings from status
	earnings = status.get("earnings", {})
	total_usd = float(earnings.get("total_usd", 0.0))
	this_week_usd = float(earnings.get("this_week_usd", 0.0))
	last_cycle_usd = float(earnings.get("last_cycle_usd", 0.0))
	summary_lines.extend([
		"## Earnings",
		f"- Total (on‑chain): ${total_usd:,.2f}",
		f"- This week: ${this_week_usd:,.2f}",
		f"- Last cycle: ${last_cycle_usd:,.2f}",
	])

	# Articles published today
	article_daily = status.get("article_daily", {})
	today = article_daily.get("date", "")
	published_today = article_daily.get("published", 0)
	summary_lines.extend([
		"## Articles",
		f"- Published today: {published_today}",
	])

	# Code‑techs leads
	code_techs = status.get("code_tech_earning", {})
	summary_lines.extend([
		"## Code‑Tech Opportunities",
		f"- Leads refreshed: {code_techs.get('channel_count', 0) + code_techs.get('asset_count', 0)}",
		f"- Channels (where product gets paid): {code_techs.get('channel_count', 0)}",
		f"- Assets (free tooling/reach): {code_techs.get('asset_count', 0)}",
	])

	# Payout / wallet
	wallet = status.get("wallet", {})
	address = wallet.get("address_masked", "")
	network = wallet.get("network", "")
	balance = float(wallet.get("confirmed_usd", 0.0))
	summary_lines.extend([
		"## Wallet",
		f"- Network: {network}",
		f"- Address (masked): {address}",
		f"- Confirmed balance: ${balance:,.2f}",
	])

	# Backfill progress
	backfill = status.get("backfill", {})
	done = backfill.get("done_ids", [])
	remaining = backfill.get("remaining", 0)
	summary_lines.extend([
		"## Backfill",
		f"- Posts processed: {len(done)}",
		f"- Remaining (no footer): {remaining}",
	])

	# Attribution receipts
	attribution = status.get("attribution", {})
	receipt_count = attribution.get("receipt_count", 0)
	total_attributed = float(attribution.get("total_attributed_usd", 0.0))
	summary_lines.extend([
		"## Attribution",
		f"- Receipts (correlated): {receipt_count}",
		f"- Total attributed (correlated): ${total_attributed:,.2f}",
	])

	# LLM providers status
	llm_roles = status.get("llm_roles", {})
	summary_lines.extend([
		"## LLM Providers",
		f"- Upgrade: {llm_roles.get('upgrade', 'unknown')}",
		f"- Research: {llm_roles.get('research', 'unknown')}",
		f"- Post: {llm_roles.get('post', 'unknown')}",
	])

	# Write the summary file
	_PUBLIC_DAILY_SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
	_PUBLIC_DAILY_SUMMARY_FILE.write_text("\n".join(summary_lines), encoding="utf-8")
	log.info("Daily summary written -> docs/daily-summary.md")


def write_html(status: dict[str, Any]) -> None:
	"""Publish safe dashboard data files consumed by the React frontend."""
	_HTML_FILE.parent.mkdir(parents=True, exist_ok=True)
	from bot.status import sanitize_for_git
	public_status = sanitize_for_git(status)
	github_repo = os.getenv("GITHUB_REPO", "").strip()
	if github_repo:
		public_status["github_repo"] = github_repo
	_PUBLIC_STATUS_FILE.write_text(
		json.dumps(public_status, indent=2, default=str),
		encoding="utf-8",
	)

	if _LOG_FILE.exists():
		_PUBLIC_LOG_FILE.write_text(
			_LOG_FILE.read_text(encoding="utf-8"),
			encoding="utf-8",
		)

	# Write the daily summary for quick scanning
	write_daily_summary(status)

	if not _HTML_FILE.exists():
		_HTML_FILE.write_text(_fallback_index(), encoding="utf-8")

	log.info("Dashboard data written -> docs/status.json")


def _fallback_index() -> str:
	"""Helpful fallback page shown only before the frontend bundle is built."""
	return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>E-Evolve Dashboard</title>
  <style>
    body{margin:0;font-family:system-ui,sans-serif;background:#0b0f14;color:#e5edf7}
    main{max-width:760px;margin:12vh auto;padding:0 24px}
    a{color:#6aa6ff}
    code{background:#17202c;padding:2px 6px;border-radius:6px}
    .summary{border:1px solid #2a3a4a;background:#11181f;padding:12px;margin:12px 0;border-radius:8px}
  </style>
</head>
<body>
  <main>
    <h1>E-Evolve Dashboard</h1>
    <p>The React dashboard has not been built yet. Use the static JSON files below for quick data access.</p>
    <div class="summary">
      <h2>Quick Links</h2>
      <ul>
        <li><a href="status.json">status.json</a> – full bot state (including earnings, articles, LLM roles)</li>
        <li><a href="earnings-log.md">earnings-log.md</a> – human‑readable log of actions this cycle</li>
        <li><a href="daily-summary.md">daily-summary.md</a> – concise earnings snapshot for today</li>
      </ul>
    </div>
    <p>Run <code>npm install</code> and <code>npm run build</code> in
    <code>frontend/</code> to generate the interactive dashboard.</p>
  </main>
</body>
</html>
"""