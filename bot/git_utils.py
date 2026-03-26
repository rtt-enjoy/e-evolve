"""
Git Utilities
Wraps the git CLI for staging and committing.
The push step is handled by the GitHub Actions workflow YAML.
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


def commit(message: str, paths: Optional[list[str]] = None) -> bool:
    """
    Stage and commit.
    - If `paths` given: only stages files that exist on disk.
    - If `paths` is None: stages everything (git add -A) except backups dir.
    Returns True if a commit was created, False if nothing changed.
    """
    try:
        if paths is not None:
            existing = [p for p in paths if Path(p).exists()]
            if not existing:
                return False
            for p in existing:
                _run("add", "--", p)
        else:
            _run("add", "-A")
            if Path(".evolution_backups").exists():
                _run("reset", "--", ".evolution_backups")

        # Is anything staged?
        r = _run("diff", "--cached", "--quiet", check=False)
        if r.returncode == 0:
            log.debug("Nothing to commit for: %s", message[:60])
            return False

        _run("commit", "-m", message,
             "--author", "E-Evolve Bot <evolve-bot@users.noreply.github.com>")

        sha = _run("rev-parse", "--short", "HEAD", capture=True)
        log.info("Committed [%s]: %s", sha, message[:80])
        return True

    except subprocess.CalledProcessError as exc:
        log.error("git failed: cmd=%s stdout=%s stderr=%s",
                  exc.cmd, exc.stdout, exc.stderr)
        return False


def short_sha() -> str:
    try:
        return _run("rev-parse", "--short", "HEAD", capture=True)
    except Exception:
        return "unknown"


# ── internal ────────────────────────────────────────────────────────────────

def _run(
    *args: str,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess | str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, ["git", *args],
            result.stdout, result.stderr,
        )
    return result.stdout.strip() if capture else result
