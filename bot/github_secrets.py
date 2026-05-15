"""
GitHub Actions secret-name discovery.

GitHub does not expose secret values after they are saved. This module only
fetches secret names so local status checks can match the repository's online
Actions setup without risking credential leaks.
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import urllib.error
import urllib.request

log = logging.getLogger(__name__)

_SECRET_NAME_RE = re.compile(r"^[A-Z0-9_]{4,}$")


def configured_secret_names() -> set[str]:
    """Return safe GitHub Actions secret names known to be configured online."""
    names = _names_from_env()
    if names:
        return names
    if os.getenv("GITHUB_ACTIONS", "").strip().lower() == "true":
        return set()

    repo = _repo_name()
    token = os.getenv("GH_TOKEN", "").strip() or os.getenv("GITHUB_TOKEN", "").strip()
    if not repo or not token:
        return set()

    return _names_from_github_api(repo, token)


def _names_from_env() -> set[str]:
    """Allow CI or local shells to pass a comma/space-separated secret-name list."""
    raw = os.getenv("GITHUB_CONFIGURED_SECRETS", "").strip()
    if not raw:
        return set()
    return {
        name
        for name in re.split(r"[\s,]+", raw)
        if _SECRET_NAME_RE.match(name)
    }


def _repo_name() -> str:
    repo = os.getenv("GITHUB_REPO", "").strip() or os.getenv("GITHUB_REPOSITORY", "").strip()
    if repo:
        return repo

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return _repo_from_remote(result.stdout.strip())


def _repo_from_remote(remote: str) -> str:
    if remote.endswith(".git"):
        remote = remote[:-4]
    match = re.search(r"github\.com[:/](?P<owner>[^/\s]+)/(?P<repo>[^/\s]+)$", remote)
    if not match:
        return ""
    return f"{match.group('owner')}/{match.group('repo')}"


def _names_from_github_api(repo: str, token: str) -> set[str]:
    url = f"https://api.github.com/repos/{repo}/actions/secrets?per_page=100"
    names: set[str] = set()
    while url:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "e-evolve-secret-readiness",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                names.update(
                    item["name"]
                    for item in payload.get("secrets", [])
                    if _SECRET_NAME_RE.match(str(item.get("name", "")))
                )
                url = _next_link(response.headers.get("Link", ""))
        except urllib.error.HTTPError as exc:
            log.warning("GitHub secret-name lookup failed for %s: HTTP %s", repo, exc.code)
            return names
        except Exception as exc:
            log.debug("GitHub secret-name lookup skipped: %s", exc)
            return names
    return names


def _next_link(link_header: str) -> str:
    for part in link_header.split(","):
        section = part.strip()
        if 'rel="next"' not in section:
            continue
        match = re.match(r"<([^>]+)>", section)
        if match:
            return match.group(1)
    return ""


if __name__ == "__main__":
    for name in sorted(configured_secret_names()):
        print(name)
