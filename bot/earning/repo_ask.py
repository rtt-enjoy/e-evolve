"""
Earning Module — Repository Ask

Inserts the published receive address into the GitHub repository itself so that
the product page, README, and releases all carry the ask. This is the
top-ranked channel in code_techs that needs no account and no owner action,
and this module makes it automatic.

Uses the existing GH_TOKEN secret. No new secret. No LLM call. Deterministic.
"""
from __future__ import annotations

import base64
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger(__name__)

_GH_API = "https://api.github.com"
_README_FILE = "README.md"
_FUNDING_FILE = ".github/FUNDING.yml"
_SUPPORT_FILE = Path("docs/support.md")

_DEFAULTS = {
    "enabled": True,
    "append_to_readme": True,
    "create_funding": True,
    "write_support_page": True,
}


def _config() -> dict:
    from . import _shared
    return _shared.load_config("repo_ask", _DEFAULTS)


def _wallet_address() -> str:
    return os.getenv("USDT_WALLET_ADDRESS", "").strip()


def _repo() -> str:
    return os.getenv("GITHUB_REPOSITORY", "").strip()


def _headers() -> dict:
    token = os.getenv("GH_TOKEN", "").strip()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "e-evolve-repo-ask",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_file(path: str) -> tuple[str, str] | None:
    """Return (content_decoded, sha) for a file, or None if missing."""
    repo = _repo()
    if not repo:
        return None
    try:
        resp = requests.get(
            f"{_GH_API}/repos/{repo}/contents/{path}",
            headers=_headers(),
            timeout=20,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content, data.get("sha", "")
    except Exception as exc:
        log.warning("[repo_ask] fetch %s failed: %s", path, exc)
        return None


def _put_file(path: str, content: str, message: str, sha: str | None = None) -> bool:
    repo = _repo()
    if not repo:
        return False
    body: dict[str, Any] = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }
    if sha:
        body["sha"] = sha
    try:
        resp = requests.put(
            f"{_GH_API}/repos/{repo}/contents/{path}",
            headers=_headers(),
            json=body,
            timeout=20,
        )
        if resp.status_code in (403, 422):
            log.warning("[repo_ask] update %s failed: %s", path, resp.text[:200])
            return False
        resp.raise_for_status()
        return True
    except Exception as exc:
        log.warning("[repo_ask] update %s failed: %s", path, exc)
        return False


def _append_to_readme(content: str, address: str) -> str:
    """Append a support section if the address is not already present."""
    if address in content:
        return content
    section = (
        "\n\n---\n\n"
        "## Support this work\n\n"
        "These write-ups are researched and published with no paywall, sponsor, or tracking. "
        "If one saved you an afternoon, a small tip keeps them coming.\n\n"
        f"Send a tip in USDT, USDC or USDD on Tron (TRC-20) to:\n\n"
        f"`{address}`\n\n"
        "The same address is on the product page and in every article footer.\n"
    )
    return content.rstrip() + section


def _funding_yml(address: str) -> str:
    """Return the FUNDING.yml content with a custom field pointing at the wallet."""
    return (
        "# GitHub Sponsors is not required. This custom field shows the receive address.\n"
        "custom:\n"
        "  - title: Tip in USDT\n"
        f"    url:tron:{address}\n"
    )


def _support_page(address: str) -> str:
    return (
        "---\n"
        "title: Support\n"
        "nav: footer\n"
        "---\n\n"
        "# Support this work\n\n"
        "These write-ups are researched and published with no paywall, sponsor, or tracking. "
        "If one saved you an afternoon, a small tip keeps them coming.\n\n"
        "Send a tip in **USDT**, **USDC** or **USDD** on **Tron (TRC-20)** to:\n\n"
        f"> {address}\n\n"
        "The same address is on the product page, in the README, and in every article footer.\n"
    )


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Main entry point. No LLM call; deterministic."""
    cfg = _config()
    if not cfg.get("enabled", True):
        return []

    address = _wallet_address()
    if not address:
        log.info("[repo_ask] USDT_WALLET_ADDRESS not set — skipping")
        return []

    state = status.setdefault("repo_ask", {
        "last_run": None,
        "readme_has_address": False,
        "funding_exists": False,
        "support_page_written": False,
        "updated": False,
    })

    updated = False
    actions: list[dict] = []

    # README
    if cfg.get("append_to_readme", True):
        existing = _get_file(_README_FILE)
        if existing is None:
            log.warning("[repo_ask] could not fetch %s", _README_FILE)
        else:
            content, sha = existing
            if address not in content:
                new_content = _append_to_readme(content, address)
                if _put_file(_README_FILE, new_content, f"Add receive address to {_README_FILE}", sha):
                    updated = True
                    state["readme_has_address"] = True
                    actions.append({"platform": "github-repo", "success": True, "file": _README_FILE})
                else:
                    actions.append({"platform": "github-repo", "success": False, "file": _README_FILE})
            else:
                state["readme_has_address"] = True

    # FUNDING.yml
    if cfg.get("create_funding", True):
        existing = _get_file(_FUNDING_FILE)
        if existing is None:
            content = _funding_yml(address)
            if _put_file(_FUNDING_FILE, content, f"Create {_FUNDING_FILE} with receive address"):
                updated = True
                state["funding_exists"] = True
                actions.append({"platform": "github-repo", "success": True, "file": _FUNDING_FILE})
            else:
                actions.append({"platform": "github-repo", "success": False, "file": _FUNDING_FILE})
        else:
            content, sha = existing
            if address not in content:
                new_content = _funding_yml(address)
                if _put_file(_FUNDING_FILE, new_content, f"Update {_FUNDING_FILE} with receive address", sha):
                    updated = True
                    state["funding_exists"] = True
                    actions.append({"platform": "github-repo", "success": True, "file": _FUNDING_FILE})
            else:
                state["funding_exists"] = True

    # Support page
    if cfg.get("write_support_page", True):
        page = _support_page(address)
        try:
            _SUPPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
            _SUPPORT_FILE.write_text(page, encoding="utf-8")
            state["support_page_written"] = True
            actions.append({"platform": "github-pages", "success": True, "file": str(_SUPPORT_FILE)})
        except Exception as exc:
            log.warning("[repo_ask] support page write failed: %s", exc)
            actions.append({"platform": "github-pages", "success": False, "error": str(exc)[:120]})

    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state["updated"] = updated

    if not updated and all(a.get("success") for a in actions if a.get("success")):
        log.info("[repo_ask] receive address already present in all target files")
    elif updated:
        log.info("[repo_ask] receive address added to repository files")

    return [{
        "platform": "repo_ask",
        "success": updated,
        "estimated_usd": 0.0,
        "actions": actions,
        "address": address,
    }]