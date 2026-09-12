"""
Dashboard data publisher.

The interactive dashboard UI lives in frontend/ and is built with Vite into
docs/ for GitHub Pages. Python owns the backend-facing data contract:

  - docs/status.json
  - docs/earnings-log.md

If the React build has not been generated yet, write a tiny fallback shell so
GitHub Pages still has a helpful index.html.
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


def write_log(actions: list[dict]) -> None:
	"""Append this cycle's completed actions to earnings-log.md."""
	if not actions:
		return

	ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
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
		_HTML_FILE.write_text(_fallback_index(status), encoding="utf-8")

	log.info("Dashboard data written -> docs/status.json")


def _fallback_index(status: dict[str, Any]) -> str:
	"""Minimal page shown only before the frontend bundle is built."""
	# Extract key data from status for the fallback page
	wallet = status.get("wallet", {})
	balance = float(wallet.get("confirmed_usd", 0) or 0)
	usdt_balance = float(wallet.get("usdt_balance", 0) or 0)
	
	articles = status.get("article_stats", {})
	article_count = articles.get("count", 0)
	total_views = articles.get("total_views", 0)
	best_title = articles.get("best_title", "")
	best_views = articles.get("best_views", 0)
	
	earnings = status.get("earnings", {})
	total_earnings = float(earnings.get("total_usd", 0) or 0)
	week_earnings = float(earnings.get("this_week_usd", 0) or 0)
	
	# Get active features
	active_features = status.get("active_features", [])
	inactive_features = status.get("inactive_features", [])
	
	# Build a simple but informative fallback page
	return f"""<!doctype html>
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
      line-height:1.5;
    }}
    main{{
      max-width:800px;
      margin:2vh auto;
      padding:0 24px;
    }}
    a{{
      color:#6aa6ff;
    }}
    .card {{
      background:#17202c;
      border-radius:8px;
      padding:20px;
      margin:20px 0;
      border:1px solid #2a3441;
    }}
    .card h2 {{
      margin-top:0;
      color:#6aa6ff;
      font-size:1.5em;
    }}
    .stat-row {{
      display:flex;
      justify-content:space-between;
      margin:10px 0;
      padding:10px 0;
      border-bottom:1px solid #2a3441;
    }}
    .stat-label {{
      opacity:0.8;
    }}
    .stat-value {{
      font-weight:bold;
    }}
    code{{
      background:#17202c;
      padding:2px 6px;
      border-radius:6px;
      font-family:monospace;
    }}
    .features {{
      display:flex;
      flex-wrap:wrap;
      gap:8px;
      margin:10px 0;
    }}
    .feature-tag {{
      background:#2a3441;
      padding:4px 10px;
      border-radius:20px;
      font-size:0.9em;
    }}
    .active {{
      background:#2a5a3a;
      color:#a3d9a5;
    }}
    .inactive {{
      background:#5a3a2a;
      color:#d9a5a5;
    }}
  </style>
</head>
<body>
  <main>
    <h1>E-Evolve Dashboard</h1>
    <p>The React dashboard has not been built yet, but here's the current status:</p>

    <div class="card">
      <h2>💰 Wallet & Earnings</h2>
      <div class="stat-row">
        <span class="stat-label">Confirmed Balance:</span>
        <span class="stat-value">${balance:,.2f}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">USDT Balance:</span>
        <span class="stat-value">${usdt_balance:,.2f}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Total Earnings:</span>
        <span class="stat-value">${total_earnings:,.2f}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">This Week:</span>
        <span class="stat-value">${week_earnings:,.2f}</span>
      </div>
    </div>

    <div class="card">
      <h2>📊 Articles & Reach</h2>
      <div class="stat-row">
        <span class="stat-label">Published Articles:</span>
        <span class="stat-value">{article_count}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Total Views:</span>
        <span class="stat-value">{total_views:,}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Best Performing:</span>
        <span class="stat-value">{best_title[:50]}{'...' if len(best_title) > 50 else ''}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Best Views:</span>
        <span class="stat-value">{best_views:,}</span>
      </div>
    </div>

    <div class="card">
      <h2>🔧 Active Features</h2>
      <div class="features">
        {''.join(f'<span class="feature-tag active">{feat}</span>' for feat in active_features)}
        {''.join(f'<span class="feature-tag inactive">{feat}</span>' for feat in inactive_features)}
      </div>
    </div>

    <div class="card">
      <h2>📋 Next Steps</h2>
      <p>To get the full interactive dashboard:</p>
      <ol>
        <li>Run <code>npm install</code> in the <code>frontend</code> directory</li>
        <li>Run <code>npm run build</code> to generate the React bundle</li>
        <li>Check <code>status.json</code> for the latest data</li>
        <li>Inspect <code>earnings-log.md</code> for recent activity</li>
      </ol>
      <p>The fallback will be replaced automatically once the frontend is built.</p>
    </div>
  </main>
</body>
</html>"""