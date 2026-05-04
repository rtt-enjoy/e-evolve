"""
Owner Command System
Read commands from command.txt or GitHub Issues labelled "bot-command".

Exports:
  read()          -> list[dict]   parse all pending commands
  apply(cmds, status) -> status   apply parsed commands, return updated status
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
COMMAND_FILE = ROOT / "command.txt"


def read() -> list[dict]:
    """Return list of parsed command dicts from command.txt + GitHub Issues."""
    cmds: list[dict] = []

    # --- command.txt ---
    if COMMAND_FILE.exists():
        text = COMMAND_FILE.read_text(encoding="utf-8").strip()
        if text:
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    cmd = _parse_line(line)
                    if cmd:
                        cmds.append(cmd)
            # Clear file after reading
            COMMAND_FILE.write_text("", encoding="utf-8")
            log.info("Read %d command(s) from command.txt", len(cmds))

    # --- GitHub Issues (label: bot-command) ---
    try:
        cmds.extend(_read_github_issues())
    except Exception as exc:
        log.warning("GitHub Issues command read failed: %s", exc)

    return cmds


def apply(cmds: list[dict], status: dict) -> dict:
    """Apply commands to status dict, return updated status."""
    if not cmds:
        return status

    overrides: dict = status.get("_overrides", {})

    for cmd in cmds:
        kind = cmd.get("type")
        log.info("Applying command: %s", cmd)

        if kind == "skip_evolution":
            overrides["skip_evolution"] = True

        elif kind == "force_articles":
            overrides["force_articles"] = cmd.get("count", 1)

        elif kind == "force_trade":
            overrides["force_trade"] = cmd.get("mode", "normal")

        elif kind == "force_mint":
            overrides["force_mint"] = cmd.get("count", 1)

        elif kind == "post_thread":
            overrides["post_thread"] = True

        elif kind == "reset_earnings":
            earnings = status.get("earnings", {})
            earnings["this_week_usd"] = 0.0
            earnings["last_cycle_usd"] = 0.0
            status["earnings"] = earnings
            log.info("Earnings reset by owner command")

        elif kind == "status_report":
            overrides["status_report"] = True

        else:
            log.warning("Unknown command type: %s", kind)

    status["_overrides"] = overrides
    return status


# ── Internal helpers ──────────────────────────────────────────────────────────

def _parse_line(line: str) -> dict | None:
    """Parse one command line into a dict, or None if unrecognised."""
    parts = line.lower().split()
    if not parts:
        return None

    # force articles N
    if parts[:2] == ["force", "articles"]:
        count = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
        return {"type": "force_articles", "count": count, "raw": line}

    # force trade <mode>
    if parts[:2] == ["force", "trade"]:
        mode = parts[2] if len(parts) > 2 else "normal"
        return {"type": "force_trade", "mode": mode, "raw": line}

    # force mint N
    if parts[:2] == ["force", "mint"]:
        count = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
        return {"type": "force_mint", "count": count, "raw": line}

    # skip evolution
    if parts[:2] == ["skip", "evolution"]:
        return {"type": "skip_evolution", "raw": line}

    # reset earnings
    if parts[:2] == ["reset", "earnings"]:
        return {"type": "reset_earnings", "raw": line}

    # post thread
    if parts[:2] == ["post", "thread"]:
        return {"type": "post_thread", "raw": line}

    # status report
    if parts[:2] == ["status", "report"]:
        return {"type": "status_report", "raw": line}

    log.warning("Unrecognised command line: %r", line)
    return None


def _read_github_issues() -> list[dict]:
    """Fetch open issues labelled 'bot-command' via GitHub API."""
    import urllib.request, json

    token = os.environ.get("GITHUB_TOKEN", "")
    repo  = os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repo:
        return []

    url = f"https://api.github.com/repos/{repo}/issues?labels=bot-command&state=open"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "e-evolve-bot",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        issues = json.loads(resp.read())

    cmds: list[dict] = []
    for issue in issues:
        body = (issue.get("body") or "").strip()
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                cmd = _parse_line(line)
                if cmd:
                    cmd["issue"] = issue["number"]
                    cmds.append(cmd)
        # Close issue after reading
        _close_github_issue(token, repo, issue["number"])

    return cmds


def _close_github_issue(token: str, repo: str, number: int) -> None:
    import urllib.request, json as _json
    url = f"https://api.github.com/repos/{repo}/issues/{number}"
    data = _json.dumps({"state": "closed"}).encode()
    req = urllib.request.Request(url, data=data, method="PATCH", headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "e-evolve-bot",
    })
    with urllib.request.urlopen(req, timeout=10):
        pass
