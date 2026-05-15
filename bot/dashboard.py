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
    """Minimal page shown only before the frontend bundle is built."""
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
  </style>
</head>
<body>
  <main>
    <h1>E-Evolve Dashboard</h1>
    <p>The React dashboard has not been built yet.</p>
    <p>Run <code>npm install</code> and <code>npm run build</code> in
    <code>frontend/</code>, or inspect <a href="status.json">status.json</a>.</p>
  </main>
</body>
</html>
"""
