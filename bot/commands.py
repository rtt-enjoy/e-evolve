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
            # Implement minting logic
            pass

        elif cmd == "skip evolution":
            # Implement skip evolution logic
            pass

        elif cmd == "reset earnings":
            # Implement reset earnings logic
            pass

        elif cmd == "post thread":
            # Implement post thread logic
            pass

        elif cmd == "status report":
            # Implement status report logic
            pass

    return {**status, '_overrides': overrides}