"""
Evolution — Phase 3
Reads the codebase, asks the LLM for improvements, applies them safely.

Hard safety rules (cannot be overridden by LLM output):
  • Only writes files under: bot/, docs/, config/, requirements.txt, version.txt
  • Never touches: .github/, .git/
  • No path traversal (.. rejected)
  • Python files are syntax-checked before writing
  • Max 3 file changes per cycle
  • Original files are backed up before overwriting
"""
from __future__ import annotations

import ast
import json
import logging
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Safety constants
ALLOWED_PREFIXES  = ("bot/", "docs/", "config/", "requirements.txt", "version.txt")
FORBIDDEN_PREFIXES = (".github/", ".git/")
MAX_CHANGES       = 3
MAX_READ_BYTES    = 20_000   # truncate large files before sending to LLM

_SYSTEM = """\
You are the autonomous evolution engine of E-Evolve, a self-improving GitHub Actions bot.

Analyse the codebase and current status, then propose CONCRETE, WORKING improvements.

Respond with ONLY a single JSON object — no markdown, no prose outside the JSON.

Required JSON schema:
{
  "version": "X.Y.Z",
  "summary": "one-sentence description of changes",
  "suggestions": [
    {
      "title": "short title",
      "description": "what it unlocks or earns",
      "secret_needed": "SECRET_NAME or null",
      "estimated_weekly_usd": 0
    }
  ],
  "changes": [
    {
      "file": "bot/some_file.py",
      "content": "COMPLETE new file content — never a diff or snippet",
      "reason": "why"
    }
  ]
}

Rules:
1. Only write files under: bot/, docs/, config/, requirements.txt, version.txt
2. Never touch .github/ or .git/
3. Every "content" must be the COMPLETE new file — not a patch
4. Python files must be syntactically valid
5. At most 3 changes per response
6. If nothing to change, return "changes": []
7. Always return at least 3 ranked suggestions
8. Bump patch for fixes, minor for new features, major for rewrites"""


def run(llm: Any, status: dict[str, Any]) -> dict[str, Any]:
    """
    Run evolution. Returns:
      { version_bumped_to, summary, changes_applied, suggestions, error }
    """
    log.info("Reading codebase for evolution...")
    codebase = _read_codebase()

    prompt = (
        f"Current status:\n{json.dumps(status, indent=2, default=str)}\n\n"
        f"Active features: {status.get('active_features', [])}\n"
        f"Inactive (need secrets): {status.get('inactive_features', [])}\n\n"
        f"Codebase:\n{codebase}\n\n"
        "Propose improvements. JSON only."
    )

    try:
        plan = llm.complete_json(prompt, system=_SYSTEM, max_tokens=6000)
    except Exception as exc:
        log.error("Evolution LLM call failed: %s", exc)
        return _error_result(str(exc), status.get("version", "1.0.0"))

    applied  = _apply_changes(plan.get("changes", []))
    version  = _resolve_version(plan.get("version"), status.get("version", "1.0.0"))

    Path("version.txt").write_text(version + "\n", encoding="utf-8")

    return {
        "version_bumped_to": version,
        "summary":           plan.get("summary", "No summary provided"),
        "changes_applied":   applied,
        "suggestions":       plan.get("suggestions", []),
        "error":             None,
    }


# ── File reading ─────────────────────────────────────────────────────────────

def _read_codebase() -> str:
    parts: list[str] = []
    patterns = ["bot/**/*.py", "config/*.json", "requirements.txt"]
    seen: set[str] = set()
    for pat in patterns:
        for path in sorted(Path(".").glob(pat)):
            key = str(path)
            if key in seen or not path.is_file():
                continue
            seen.add(key)
            try:
                raw = path.read_text(encoding="utf-8", errors="replace")
                if len(raw) > MAX_READ_BYTES:
                    raw = raw[:MAX_READ_BYTES] + "\n... [truncated]"
                parts.append(f"=== {key} ===\n{raw}")
            except Exception as exc:
                parts.append(f"=== {key} === [unreadable: {exc}]")
    return "\n\n".join(parts) or "(no source files found)"


# ── Change application ────────────────────────────────────────────────────────

def _apply_changes(changes: list) -> list[dict]:
    if not isinstance(changes, list):
        return []
    applied: list[dict] = []
    for ch in changes[:MAX_CHANGES]:
        if not isinstance(ch, dict):
            continue
        filepath = str(ch.get("file", "")).strip().lstrip("/")
        content  = str(ch.get("content", "")).strip()
        reason   = str(ch.get("reason", ""))

        if not filepath or not content:
            log.warning("Skipping malformed change (missing file or content)")
            continue
        if not _is_safe(filepath):
            log.warning("Blocked write to forbidden path: %s", filepath)
            continue
        if filepath.endswith(".py") and not _is_valid_python(content):
            log.warning("Skipping file with Python syntax error: %s", filepath)
            continue

        _backup(filepath)
        dest = Path(filepath)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        log.info("Wrote %s — %s", filepath, reason[:60])
        applied.append({"file": filepath, "reason": reason})

    return applied


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_safe(p: str) -> bool:
    if ".." in p:
        return False
    for bad in FORBIDDEN_PREFIXES:
        if p.startswith(bad):
            return False
    for ok in ALLOWED_PREFIXES:
        if p.startswith(ok):
            return True
    return p in ("requirements.txt", "version.txt")


def _is_valid_python(src: str) -> bool:
    try:
        ast.parse(src)
        return True
    except SyntaxError as exc:
        log.warning("Syntax error in generated code: %s", exc)
        return False


def _backup(filepath: str) -> None:
    src = Path(filepath)
    if not src.exists():
        return
    bdir = Path(".evolution_backups")
    bdir.mkdir(exist_ok=True)
    ts   = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    shutil.copy2(src, bdir / f"{src.name}.{ts}.bak")


def _resolve_version(proposed: Any, current: str) -> str:
    """Use proposed version if it's a valid X.Y.Z string; else bump patch."""
    if proposed and re.match(r"^\d+\.\d+\.\d+$", str(proposed).strip()):
        return str(proposed).strip()
    # Bump patch of current
    try:
        parts = [int(x) for x in current.split(".")]
        parts[2] += 1
        return ".".join(str(p) for p in parts)
    except Exception:
        return "1.0.1"


def _error_result(error: str, current_version: str) -> dict[str, Any]:
    return {
        "version_bumped_to": current_version,
        "summary":           f"Evolution skipped: {error[:120]}",
        "changes_applied":   [],
        "suggestions":       [],
        "error":             error,
    }
