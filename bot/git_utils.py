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


def commit(message: str, paths: Optional[list[str]] = None) -> dict:
	"""
    Stage and commit.
    - If `paths` given: only stages files that exist on disk.
    - If `paths` is None: stages everything (git add -A) except backups dir.
    Returns dict with keys: success (bool), committed (bool), error (str|None).
    """
	try:
		if paths is not None:
			existing = [p for p in paths if Path(p).exists()]
			if not existing:
				return {"success": True, "committed": False, "error": None}
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
			return {"success": True, "committed": False, "error": None}

		_run("commit", "-m", message,
			 "--author", "E-Evolve Bot <evolve-bot@users.noreply.github.com>")

		sha = _run("rev-parse", "--short", "HEAD", capture=True)
		log.info("Committed [%s]: %s", sha, message[:80])
		return {"success": True, "committed": True, "error": None}

	except subprocess.CalledProcessError as exc:
		err = f"cmd={exc.cmd} stdout={exc.stdout!r} stderr={exc.stderr!r}"
		log.error("git failed: %s", err)
		return {"success": False, "committed": False, "error": err}


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


def current_branch() -> str:
	"""Name of the checked-out branch, or empty string if detached/unavailable."""
	try:
		return _run("rev-parse", "--abbrev-ref", "HEAD", capture=True)  # type: ignore[return-value]
	except subprocess.CalledProcessError:
		return ""


def commit_to_branch(message: str, paths: list[str], branch: str) -> dict:
	"""
    Commit `paths` onto `branch` without leaving changes on the current branch.

    Evolution output is never committed to main: it lands on its own branch so
    the owner reviews it before it can affect the hourly cycle. The original
    branch is always restored, and the evolved files are reverted to their
    committed state on it, so the state commit at the end of the cycle does not
    silently pick up unreviewed code.

    Returns dict with keys: success, committed, branch, error.
    """
	origin = current_branch()
	if not origin:
		return {"success": False, "committed": False, "branch": branch,
				"error": "could not resolve current branch (detached HEAD?)"}

	existing = [p for p in paths if Path(p).exists()]
	if not existing:
		return {"success": True, "committed": False, "branch": branch, "error": None}

	try:
		# Carry the working-tree changes onto a fresh branch, commit them there,
		# then return to the original branch and discard them from it.
		_run("checkout", "-b", branch)
		for p in existing:
			_run("add", "--", p)

		r = _run("diff", "--cached", "--quiet", check=False)
		if r.returncode == 0:  # type: ignore[union-attr]
			_run("checkout", origin)
			_run("branch", "-D", branch, check=False)
			return {"success": True, "committed": False, "branch": branch, "error": None}

		_run("commit", "-m", message,
			 "--author", "E-Evolve Bot <evolve-bot@users.noreply.github.com>")
		sha = _run("rev-parse", "--short", "HEAD", capture=True)
		_run("checkout", origin)
		# Drop the evolved content from the working branch — it lives on `branch` only.
		for p in existing:
			_run("checkout", "--", p, check=False)
		log.info("Evolution committed to branch %s [%s] — awaiting review", branch, sha)
		return {"success": True, "committed": True, "branch": branch, "error": None}

	except subprocess.CalledProcessError as exc:
		err = f"cmd={exc.cmd} stdout={exc.stdout!r} stderr={exc.stderr!r}"
		log.error("git branch commit failed: %s", err)
		# Return to the working branch and drop the un-reviewed content, so a
		# failed branch commit cannot leak evolved files into the state commit.
		_run("checkout", origin, check=False)
		for p in existing:
			_run("checkout", "--", p, check=False)
		return {"success": False, "committed": False, "branch": branch, "error": err}
