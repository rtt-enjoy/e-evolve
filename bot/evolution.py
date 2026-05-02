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

Post-apply verification (Phase 3.5):
  • Each changed .py file is import-checked in a subprocess
  • On failure: LLM asked to fix (up to MAX_FIX_RETRIES attempts)
  • If still failing: backup restored, file removed from applied list
"""
from __future__ import annotations

import ast
import json
import logging
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Safety constants
ALLOWED_PREFIXES  = ("bot/", "docs/", "config/", "requirements.txt", "version.txt")
FORBIDDEN_PREFIXES = (".github/", ".git/")
MAX_CHANGES       = 3
MAX_FIX_RETRIES   = 2
# Per-provider codebase snapshot limits.
# Groq free tier: 12k TPM total — status JSON ~1k, system prompt ~0.6k, response 6k → 4k left for codebase.
# Gemini/Anthropic: large context, no TPM issue.
# OpenRouter varies by model — 30k is safe across free-tier models.
_MAX_READ_BYTES = {
    "groq":       4_000,
    "anthropic":  60_000,
    "claude-cli": 60_000,
    "gemini":     80_000,
    "openrouter": 30_000,
}

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
      "estimated_weekly_usd": 0,
      "free_tier": true,
      "how_to": ["Step 1: go to ...", "Step 2: copy the key", "Step 3: add as GitHub secret"]
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
7. Always return at least 3 ranked suggestions; set free_tier=true when the suggestion costs nothing to start (free API tier exists); populate how_to with 2-4 concrete numbered steps the owner must follow to activate it
8. Bump patch for fixes, minor for new features, major for rewrites"""


def run(llm: Any, status: dict[str, Any]) -> dict[str, Any]:
    """
    Run evolution. Returns:
      { version_bumped_to, summary, changes_applied, suggestions, error }
    """
    from bot.llm import ROLE_PROVIDER
    think_provider = ROLE_PROVIDER.get("think", "gemini")
    # Use think-role provider capacity if that key is available, else fallback to default
    key_attr = f"_{think_provider}_key" if think_provider != "claude-cli" else None
    if key_attr and getattr(llm, key_attr, ""):
        evo_provider = think_provider
    else:
        evo_provider = getattr(llm, "provider", "groq")
    max_bytes = _MAX_READ_BYTES.get(evo_provider, _MAX_READ_BYTES["groq"])
    log.info("Evolution provider=%s (think role), max_bytes=%d", evo_provider, max_bytes)
    codebase = _read_codebase(max_bytes, include_config=(evo_provider not in ("groq",)))

    prompt = (
        f"Current status:\n{json.dumps(status, indent=2, default=str)}\n\n"
        f"Active features: {status.get('active_features', [])}\n"
        f"Inactive (need secrets): {status.get('inactive_features', [])}\n\n"
        f"Codebase:\n{codebase}\n\n"
        "Propose improvements. JSON only."
    )

    try:
        plan = llm.complete_json_for_role("think", prompt, system=_SYSTEM, max_tokens=6000)
    except Exception as exc:
        log.error("Evolution LLM call failed: %s", exc)
        return _error_result(str(exc), status.get("version", "1.0.0"))

    applied  = _apply_changes(plan.get("changes", []))
    applied  = _verify_and_fix(applied, llm, status)
    version  = _resolve_version(plan.get("version"), status.get("version", "1.0.0"))

    if applied:
        Path("version.txt").write_text(version + "\n", encoding="utf-8")
    else:
        version = status.get("version", "1.0.0")

    return {
        "version_bumped_to": version,
        "summary":           plan.get("summary", "No summary provided"),
        "changes_applied":   applied,
        "suggestions":       plan.get("suggestions", []),
        "error":             None,
    }


# ── File reading ─────────────────────────────────────────────────────────────

def _read_codebase(max_bytes: int, include_config: bool = True) -> str:
    patterns = ["bot/**/*.py", "requirements.txt"]
    if include_config:
        patterns.insert(1, "config/*.json")

    parts: list[str] = []
    seen: set[str] = set()
    omitted: list[str] = []
    total = 0
    for pat in patterns:
        for path in sorted(Path(".").glob(pat)):
            key = str(path)
            if key in seen or not path.is_file():
                continue
            seen.add(key)
            try:
                raw = path.read_text(encoding="utf-8", errors="replace")
                remaining = max_bytes - total
                if remaining <= 0:
                    log.info("Codebase snapshot full at %d bytes — skipping %s", max_bytes, key)
                    omitted.append(key)
                    continue
                if len(raw) > remaining:
                    raw = raw[:remaining] + "\n... [truncated]"
                parts.append(f"=== {key} ===\n{raw}")
                total += len(raw)
            except Exception as exc:
                parts.append(f"=== {key} === [unreadable: {exc}]")
    if omitted:
        parts.append(f"# OMITTED FILES (budget exceeded — do not propose changes to these): {omitted}")
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


# ── Verification & LLM fix ───────────────────────────────────────────────────

_FIX_SYSTEM = """\
You are a Python code repair agent for E-Evolve, a self-improving GitHub Actions bot.
A file you previously generated has an import/runtime error. Fix it.

Respond with ONLY a single JSON object — no markdown, no prose.

Schema:
{
  "content": "COMPLETE fixed file content — not a diff or snippet",
  "reason": "one-sentence description of what was wrong"
}

Rules:
1. Output the ENTIRE file, not just the changed lines
2. The fix must be syntactically valid Python
3. Do not remove existing functionality — only fix the error
4. Respect the config schema shown in the prompt"""


def _import_check(filepath: str) -> str | None:
    """
    Run `python -c "import <module>"` for bot/ .py files,
    or `python -m py_compile <file>` for others.
    Returns error string on failure, None on success.
    """
    path = Path(filepath)
    if not path.exists() or not filepath.endswith(".py"):
        return None

    if filepath.startswith("bot/") or filepath.startswith("bot\\"):
        # Convert path to module name: bot/earning/articles.py -> bot.earning.articles
        module = filepath.replace("\\", "/")
        if module.endswith(".py"):
            module = module[:-3]
        module = module.replace("/", ".")

        result = subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    else:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True,
            timeout=30,
        )

    if result.returncode != 0:
        err = (result.stderr or result.stdout or "unknown error").strip()
        return err[:800]
    return None


def _load_strategy_config() -> str:
    try:
        return Path("config/strategy.json").read_text(encoding="utf-8")
    except Exception:
        return "{}"


def _verify_and_fix(applied: list[dict], llm: Any, status: dict) -> list[dict]:
    """
    For each applied .py change, import-check it.
    On error: ask LLM to fix (up to MAX_FIX_RETRIES).
    On repeated failure: restore backup and drop from applied list.
    Returns the final list of successfully verified changes.
    """
    if not applied:
        return applied

    strategy_cfg = _load_strategy_config()
    verified: list[dict] = []

    for change in applied:
        filepath = change["file"]
        if not filepath.endswith(".py"):
            verified.append(change)
            continue

        error = _import_check(filepath)
        if error is None:
            log.info("Verification passed: %s", filepath)
            verified.append(change)
            continue

        log.warning("Verification FAILED for %s: %s", filepath, error[:120])

        fixed = False
        for attempt in range(1, MAX_FIX_RETRIES + 1):
            log.info("Fix attempt %d/%d for %s", attempt, MAX_FIX_RETRIES, filepath)
            try:
                current_content = Path(filepath).read_text(encoding="utf-8", errors="replace")
            except Exception:
                current_content = "(unreadable)"

            fix_prompt = (
                f"File: {filepath}\n\n"
                f"Error:\n{error}\n\n"
                f"Current (broken) content:\n{current_content}\n\n"
                f"Strategy config (for context):\n{strategy_cfg}\n\n"
                f"Bot status summary: version={status.get('version')}, "
                f"active_features={status.get('active_features', [])}\n\n"
                "Fix the file. JSON only."
            )
            try:
                fix_plan = llm.complete_json_for_role("think", fix_prompt, system=_FIX_SYSTEM, max_tokens=4000)
                fixed_content = str(fix_plan.get("content", "")).strip()
                fix_reason    = str(fix_plan.get("reason", ""))
            except Exception as exc:
                log.warning("Fix LLM call failed attempt %d: %s", attempt, exc)
                continue

            if not fixed_content or not _is_valid_python(fixed_content):
                log.warning("Fix attempt %d produced invalid Python for %s", attempt, filepath)
                continue

            _backup(filepath)
            Path(filepath).write_text(fixed_content, encoding="utf-8")
            log.info("Applied fix attempt %d to %s: %s", attempt, filepath, fix_reason[:60])

            error = _import_check(filepath)
            if error is None:
                log.info("Verification passed after fix attempt %d: %s", attempt, filepath)
                change = {**change, "reason": f"{change.get('reason', '')} [fix: {fix_reason}]"}
                fixed = True
                break
            log.warning("Still failing after fix attempt %d: %s — %s", attempt, filepath, error[:80])

        if fixed:
            verified.append(change)
        else:
            log.error(
                "Could not fix %s after %d attempts — restoring backup",
                filepath, MAX_FIX_RETRIES,
            )
            _restore_backup(filepath)

    return verified


def _restore_backup(filepath: str) -> None:
    """Restore the most recent backup for filepath."""
    bdir = Path(".evolution_backups")
    src  = Path(filepath)
    pattern = f"{src.name}.*.bak"
    baks = sorted(bdir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not baks:
        log.warning("No backup found for %s — leaving broken file in place", filepath)
        return
    shutil.copy2(baks[0], src)
    log.info("Restored %s from %s", filepath, baks[0].name)


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
    # Prune: keep only newest 20 backups
    baks = sorted(bdir.glob("*.bak"), key=lambda p: p.stat().st_mtime)
    for old in baks[:-20]:
        old.unlink()


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


def _classify_error(error: str) -> str:
    s = error.lower()
    if "413" in s or "too large" in s or "request entity" in s:
        return "413"
    if "json" in s or "parse" in s or "decode" in s:
        return "json"
    return "api"


def _error_result(error: str, current_version: str) -> dict[str, Any]:
    error_type = _classify_error(error)
    return {
        "version_bumped_to": current_version,
        "summary":           f"Evolution skipped [{error_type}]: {error[:500]}",
        "changes_applied":   [],
        "suggestions":       [],
        "error":             error[:500],
        "error_type":        error_type,
    }
