"""
Earning Module \u2014 Repo Ask

Puts the published receive address into the repository itself:
.github/FUNDING.yml, README.md, and a GitHub release. This is the top-ranked
channel in code_techs because it needs no account, no owner action, and pays
stablecoin to the address this project already publishes.

Runs once. After that it is a no-op until the address changes.
"""
from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from . import _shared

log = logging.getLogger(__name__)

_DEFAULTS = {
    "enabled": True,
    "release_tag": "v0.0.1-support",
}


def config() -> dict:
    return _shared.load_config("repo_ask", _DEFAULTS)


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Ensure the repo carries the published receive address."""
    cfg = config()
    if not cfg.get("enabled", True):
        return []

    address = _resolve_address(status)
    if not address:
        log.info("[repo_ask] no wallet address configured \u2014 skipping")
        return []

    actions: list[dict] = []
    if _ensure_funding(address):
        actions.append({
            "platform": "github-repo",
            "success": True,
            "action": "funding_yml",
            "estimated_usd": 0.0,
        })
    if _ensure_readme(address):
        actions.append({
            "platform": "github-repo",
            "success": True,
            "action": "readme",
            "estimated_usd": 0.0,
        })
    if _ensure_release(address, cfg):
        actions.append({
            "platform": "github-repo",
            "success": True,
            "action": "release",
            "estimated_usd": 0.0,
        })

    if actions:
        _commit(actions)
    return actions


def _resolve_address(status: dict) -> str:
    """Return the full Tron address, preferring the public one over the masked."""
    public = status.get("payout_public") or {}
    addr = str(public.get("address", "")).strip()
    if addr:
        return addr
    env_addr = os.getenv("USDT_WALLET_ADDRESS", "").strip()
    if env_addr:
        return env_addr
    return ""


def _ensure_funding(address: str) -> bool:
    path = Path(".github/FUNDING.yml")
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"custom: ['tron:{address}']\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    log.info("[repo_ask] wrote %s", path)
    return True


def _ensure_readme(address: str) -> bool:
    path = Path("README.md")
    section = (
        f"\n## Support this work\n\n"
        f"If you find this project useful, you can send a tip to:\n\n"
        f"- **Tron (TRC-20):** `{address}`\n"
    )
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if address in text:
            return False
        text = text.rstrip() + section
    else:
        text = f"# E-Evolve\n{section}"
    path.write_text(text, encoding="utf-8")
    log.info("[repo_ask] updated %s", path)
    return True


def _ensure_release(address: str, cfg: dict) -> bool:
    tag = cfg.get("release_tag", "v0.0.1-support")
    try:
        result = subprocess.run(
            ["git", "tag", "-l", tag],
            capture_output=True, text=True, check=False,
        )
        if tag in result.stdout.split():
            return False
    except Exception:
        return False

    try:
        subprocess.run([
            "gh", "release", "create", tag,
            "--notes", f"Support this project: send USDT to {address}",
        ], check=True)
        return True
    except Exception as exc:
        log.warning("[repo_ask] release creation failed: %s", exc)
        return False


def _commit(actions: list[dict]) -> None:
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(
            ["git", "commit", "-m", "Add receive address to repo"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        log.info("[repo_ask] committed %d change(s)", len(actions))
    except Exception as exc:
        log.warning("[repo_ask] commit failed: %s", exc)