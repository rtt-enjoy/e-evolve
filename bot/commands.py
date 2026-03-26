"""
Owner Command System
Read commands from command.txt or GitHub Issues labelled "bot-command".
Commands execute once, then are cleared automatically.

Supported commands (case-insensitive, one per line):
  force articles N         — post N articles this cycle
  force trade aggressive   — raise trade risk to 5 %
  force mint N             — mint N NFTs
  skip evolution           — skip evolution phase
  reset earnings           — zero this_week_usd
  post thread              — force a Twitter thread even if not scheduled
  status report            — dump full status dict to workflow log
"""
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
    """
    Parse commands and store runtime overrides in status['_overrides'].
    Returns the updated status dict.
    """
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
            status.setdefault("earnings", {})["this_week_usd"] = 0.0
            log.info("Weekly earnings reset to $0")

        elif cmd == "post thread":
            overrides["force_twitter"] = True

        elif cmd == "status report":
            log.info("STATUS REPORT:\n%s", json.dumps(status, indent=2, default=str))

        else:
            log.warning("Unknown command (ignored): %r", raw)

    status["_overrides"] = overrides
    return status


# ── Sources ──────────────────────────────────────────────────────────────────

def _from_file() -> list[str]:
    """Read commands from command.txt; clear non-comment lines after reading."""
    if not COMMAND_FILE.exists():
        return []
    try:
        text  = COMMAND_FILE.read_text(encoding="utf-8")
        lines = text.splitlines()
        cmds  = [l.strip() for l in lines
                 if l.strip() and not l.strip().startswith("#")]
        if cmds:
            # Keep comment lines; remove executed commands
            kept = [l for l in lines if not l.strip() or l.strip().startswith("#")]
            COMMAND_FILE.write_text("\n".join(kept) + "\n", encoding="utf-8")
            log.info("Read %d command(s) from command.txt (cleared)", len(cmds))
        return cmds
    except Exception as exc:
        log.warning("command.txt read error: %s", exc)
        return []


def _from_github_issues() -> list[str]:
    """Read open issues labelled 'bot-command', close each after reading."""
    token = os.getenv("GH_TOKEN", "") or os.getenv("GITHUB_TOKEN", "")
    repo  = os.getenv("GITHUB_REPO", "").strip()
    if not token or not repo:
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    cmds: list[str] = []
    try:
        resp = requests.get(
            f"https://api.github.com/repos/{repo}/issues",
            headers=headers,
            params={"labels": "bot-command", "state": "open", "per_page": 10},
            timeout=15,
        )
        resp.raise_for_status()
        for issue in resp.json():
            num  = issue["number"]
            text = (issue.get("title") or issue.get("body") or "").strip()
            if text:
                cmds.append(text)
            _gh_post(f"https://api.github.com/repos/{repo}/issues/{num}/comments",
                     headers, {"body": f"✅ Command received: `{text}`"})
            _gh_req("PATCH",
                    f"https://api.github.com/repos/{repo}/issues/{num}",
                    headers, {"state": "closed"})
    except Exception as exc:
        log.debug("GitHub issue fetch (non-critical): %s", exc)
    return cmds


def _gh_post(url: str, headers: dict, body: dict) -> None:
    _gh_req("POST", url, headers, body)


def _gh_req(method: str, url: str, headers: dict, body: dict) -> None:
    try:
        requests.request(method, url, headers=headers, json=body, timeout=10)
    except Exception:
        pass
