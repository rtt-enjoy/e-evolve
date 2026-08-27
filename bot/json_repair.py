"""Shared JSON-repair helper for every LLM call site.

A recurring failure mode across the bot is that the free-tier LLM returns a
perfectly valid JSON object wrapped in stray prose -- a leading "Here is the
JSON:" line, a trailing explanation, or an outer wrapper that captures the
object inside extra braces. Each caller used to re-implement its own walk to
recover the object, and the copies drifted: some accepted the first '{', some
demanded balanced braces, some stripped code fences first. The skipped
upgrades in status are the symptom -- the upgrade LLM wraps the JSON in stray
text, the caller fails, and the whole evolution is skipped.

This module is the single source of truth. It is pure-Python, has no
dependencies, and costs nothing to call. ``repair_json_object`` returns the
first balanced JSON object found in the input, or the original string when no
object is present (so a caller can still surface the raw response to its own
logs on total failure). The balancer correctly handles braces inside strings
and escaped quotes, so it does not get fooled by `"}"` inside a string value.
"""
from __future__ import annotations

import json
import re
from typing import Any, Optional

# A fenced ```json ...``` block, if present, is the most reliable starting
# point -- the model signalled where the JSON lives. We try this before the
# scan because a scan can match an inner object inside an explanation.
_FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)


def _balanced_object(text: str, start: int) -> Optional[tuple[int, int]]:
    """Return (start, end_exclusive) of the first balanced JSON object.

    ``start`` must point at an opening ``{``. The walker tracks depth,
    ignoring braces that appear inside string literals and after backslash
    escapes. Returns None when the braces never balance -- which means the
    model returned something genuinely broken and the caller should bail.
    """
    if start < 0 or start >= len(text) or text[start] != "{":
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return (start, i + 1)
    return None


def repair_json_object(raw: Any) -> Any:
    """Return the first balanced JSON object parsed from ``raw``, or ``raw``.

    Tries three strategies in order, returning as soon as one yields a parsed
    object. The final fallback returns the input unchanged so the caller can
    still log it -- a dead LLM must degrade, never silently swallow output.

    Strategies, in order:
      1. A fenced ```json ...``` block, if any is present.
      2. A plain ``json.loads`` on the whole input -- the clean case.
      3. A balanced-brace scan from each ``{`` in the input.
    """
    if raw is None:
        return raw
    if isinstance(raw, (dict, list)):
        return raw
    text = str(raw).strip()
    if not text:
        return raw

    # 1. Fenced JSON block. Cheap, and the model often wraps the object this way.
    fence = _FENCE_RE.search(text)
    if fence:
        try:
            return json.loads(fence.group(1).strip())
        except Exception:
            pass

    # 2. Whole input is valid JSON. The ideal case.
    try:
        return json.loads(text)
    except Exception:
        pass

    # 3. Balanced-brace scan. Tries the first '{' first, then every later one,
    # so a wrapping wrapper that opens and closes around the real object does
    # not hide it.
    cursor = 0
    while True:
        idx = text.find("{", cursor)
        if idx == -1:
            return raw
        match = _balanced_object(text, idx)
        if match is None:
            cursor = idx + 1
            continue
        candidate = text[match[0]:match[1]]
        try:
            return json.loads(candidate)
        except Exception:
            cursor = match[1]


__all__ = ["repair_json_object"]