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
			# A failed action carries an "error" explaining itself; printing
			# only "action recorded" threw that away, so 17 dev.to failures in
			# this log are indistinguishable from each other and from a crash.
			err = str(action.get("error", "")).strip()
			if not ok and err:
				lines.append(f"- {icon} **{platform}**: {err[:120]}")
			else:
				lines.append(f"- {icon} **{platform}** action recorded")

	with _LOG_FILE.open("a", encoding="utf-8") as handle:
		handle.write("\n".join(lines) + "\n")

	log.info("earnings-log.md updated (%d actions)", len(actions))


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

	if not _HTML_FILE.exists():
		_HTML_FILE.write_text(_fallback_index(), encoding="utf-8")

	log.info("Dashboard data written -> docs/status.json")


def _fallback_index() -> str:
	"""Minimal page shown only before the frontend bundle is built.

	This version includes the product pitch, receive address, and tip CTA
	from status["payout_public"] so that the landing page can receive
	on-chain tips even when the React build is missing.
	"""
	status = {}
	# The status dict is not available here; we rely on the caller to have
	# already written docs/status.json, which is read by the dashboard.
	# For simplicity, we read the file directly.
	status_path = Path("docs/status.json")
	if status_path.exists():
		try:
			with status_path.open(encoding="utf-8") as f:
				status = json.load(f)
		except Exception:
			status = {}

	payout = status.get("payout_public") or {}
	address = payout.get("address", "")
	note = payout.get("note", "")
	headline = payout.get("heading", "Support this work")
	asset = payout.get("asset", "USDT, USDC or USDD")

	# Product pitch: use a generic description if not present.
	product_pitch = status.get("product_description") or (
		"E-Evolve is a self-improving GitHub Actions bot that writes technical articles, "
		"tracks earnings, and continuously upgrades its own code to maximize passive income."
	)

	html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>E-Evolve Dashboard</title>
  <style>
    body{{
      margin:0;
      font-family:system-ui,sans-serif;
      background:#0b0f14;
      color:#e5edf7;
    }}
    main{{
      max-width:760px;
      margin:12vh auto;
      padding:0 24px;
    }}
    a{{
      color:#6aa6ff;
    }}
    code{{
      background:#17202c;
      padding:2px 6px;
      border-radius:6px;
    }}
    .pitch{{
      font-size:1.2rem;
      line-height:1.6;
      margin:1.5rem 0;
    }}
    .address{{
      word-break:break-all;
      background:#17202c;
      padding:12px;
      border-radius:8px;
      font-family:monospace;
      font-size:0.95rem;
      margin:1rem 0;
    }}
    .cta{{
      margin-top:2rem;
      padding:12px 24px;
      background:#6aa6ff;
      color:#0b0f14;
      text-decoration:none;
      border-radius:8px;
      font-weight:600;
      display:inline-block;
    }}
  </style>
</head>
<body>
  <main>
    <h1>E-Evolve Dashboard</h1>
    <p>The React dashboard has not been built yet, but you can still support the project.</p>

    <div class="pitch">{product_pitch}</div>

    <h2>{headline}</h2>
    <div class="address">{address}</div>
    <p><strong>Network:</strong> {payout.get("network", "TRC-20 (Tron)")}</p>
    <p><strong>Assets accepted:</strong> {asset}</p>
    <p>{note}</p>

    <a class="cta" href="https://tronscan.io/#/send?to={address}" target="_blank">Send a tip</a>
  </main>
</body>
</html>"""
	return html