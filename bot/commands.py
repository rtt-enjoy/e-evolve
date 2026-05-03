# Owner Command System
# Read commands from command.txt or GitHub Issues labelled "bot-command".
# Commands execute once, then are cleared automatically.

# Supported commands (case-insensitive, one per line):
#   force articles N         — post N articles this cycle
#   force trade aggressive   — raise trade risk to 5 %
#   force mint N             — mint N NFTs
#   skip evolution           — skip evolution phase
#   reset earnings           — zero this_week_usd
#   post thread              — force a Twitter thread even if not scheduled
#   status report            — dump full status dict to workflow log
from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger(__name__)

COMMAND_FILE = Path("command.txt")


def read() -> list[str]:
    """Read all pending commands. Returns a list of stripped strings."""
    cmds: list[str] = []
    cmds += _from_file()
    cmds += _from_github_issues()
    if cmds:
        log.info("Commands this cycle: %s", cmds)
    return cmds


def apply(commands: list[str], status: dict[str, Any]) -> dict[str, Any]:
    """Parse commands and store runtime overrides in status['_overrides']. Returns the updated status dict."""
    overrides: dict[str, Any] = {}

    for raw in commands:
        cmd = raw.strip().lower()
        log.info("Applying command: %r", cmd)

        if m := re.match(r"force articles (\d+)$", cmd):
            overrides["force_articles"] = max(1, int(m.group(1)))

        elif cmd == "force trade aggressive":
            overrides["trade_risk_pct"] = 0.05

        elif m := re.match(r"force mint (\d+)$", cmd):
            overrides["force_mint"] = max(1, int(m.group(1)))

        elif cmd == "skip evolution":
            overrides["skip_evolution"] = True

        elif cmd == "reset earnings":
            overrides["reset_earnings"] = True

        elif cmd == "post thread":
            overrides["force_twitter"] = True

        elif cmd == "status report":
            log.info("STATUS REPORT:\n%s", json.dumps(status, indent=2, default=str))

        else:
            log.warning("Unknown command ignored: %r", raw)

    # Apply reset earnings immediately so it persists to status.json
    if overrides.get("reset_earnings"):
        if "earnings" in status:
            status["earnings"]["this_week_usd"] = 0.0
            status["earnings"]["week_started"] = None
        log.info("Earnings reset: this_week_usd zeroed")

    return {**status, "_overrides": overrides}


# ── File source ───────────────────────────────────────────────────────────────

def _from_file() -> list[str]:
    """Read commands from command.txt, then clear the file."""
    if not COMMAND_FILE.exists():
        return []
    try:
        text = COMMAND_FILE.read_text(encoding="utf-8").strip()
    except Exception as exc:
        log.warning("Could not read %s: %s", COMMAND_FILE, exc)
        return []

    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not lines:
        return []

    # Clear the file so commands don't repeat next cycle
    try:
        COMMAND_FILE.write_text("", encoding="utf-8")
    except Exception as exc:
        log.warning("Could not clear %s: %s", COMMAND_FILE, exc)

    return lines


# ── GitHub Issues source ──────────────────────────────────────────────────────

def _from_github_issues() -> list[str]:
    """Read open issues labelled 'bot-command', close them, return their titles as commands."""
    token = os.getenv("GH_TOKEN", "").strip()
    repo  = os.getenv("GITHUB_REPO", "").strip()
    if not token or not repo:
        return []

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"https://api.github.com/repos/{repo}/issues"
    params = {"labels": "bot-command", "state": "open", "per_page": 10}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        issues = resp.json()
    except Exception as exc:
        log.warning("GitHub Issues fetch failed: %s", exc)
        return []

    cmds: list[str] = []
    for issue in issues:
        title = (issue.get("title") or "").strip()
        number = issue.get("number")
        if not title or not number:
            continue
        cmds.append(title)
        # Close the issue so it doesn't repeat
        try:
            requests.patch(
                f"{url}/{number}",
                headers=headers,
                json={"state": "closed"},
                timeout=15,
            )
            log.info("Closed issue #%d after reading command: %r", number, title)
        except Exception as exc:
            log.warning("Could not close issue #%d: %s", number, exc)

    return cmds
