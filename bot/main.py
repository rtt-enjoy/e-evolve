"""
E-Evolve — Hourly Pulse Orchestrator
Entry point: python -m bot.main

Phases:
  0. Init LLM
  1. Status   — load state, detect active features
  2. Commands — read owner commands
  3. Evolve   — LLM improves codebase, commits changes
  4. Earn     — run all active income modules
  5. Update   — save status, dashboard, commit
"""
from __future__ import annotations

import importlib
import logging
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("e-evolve")

# Load .env for local development (no-op in CI)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def main() -> int:
    _hr("E-Evolve hourly pulse")
    t0     = datetime.now(timezone.utc)
    errors: list[str] = []

    # ── 0. LLM ────────────────────────────────────────────────────────────────
    try:
        from bot.llm import LLMClient
        llm = LLMClient()
    except RuntimeError as exc:
        log.critical("Cannot start: %s", exc)
        return 1   # Fatal — fail the workflow so the owner notices

    # ── 1. Status ─────────────────────────────────────────────────────────────
    _hr("Phase 1 — Status")
    import bot.status as _st
    status = _st.load()
    status = _st.snapshot(status)
    status["llm_provider"] = llm.provider

    # ── 2. Commands ───────────────────────────────────────────────────────────
    _hr("Phase 2 — Commands")
    import bot.commands as _cmd
    status = _cmd.apply(_cmd.read(), status)
    ov: dict = status.get("_overrides", {})

    # ── 3. Evolve ─────────────────────────────────────────────────────────────
    _hr("Phase 3 — Evolution")
    import bot.evolution as _evo
    import bot.git_utils as _git

    if ov.get("skip_evolution"):
        log.info("Evolution skipped by owner command")
        evo = {
            "summary":           "Skipped by owner command",
            "changes_applied":   [],
            "suggestions":       status.get("suggestions", []),
            "version_bumped_to": status.get("version"),
            "error":             None,
        }
    else:
        try:
            evo = _evo.run(llm, status)
        except Exception as exc:
            msg = f"Evolution crashed: {exc}"
            log.error(msg)
            log.debug(traceback.format_exc())
            errors.append(msg)
            evo = {
                "summary":           msg,
                "changes_applied":   [],
                "suggestions":       [],
                "version_bumped_to": status.get("version"),
                "error":             msg,
            }

    status["last_evolution"] = evo
    if evo.get("version_bumped_to"):
        status["version"] = evo["version_bumped_to"]
    if evo.get("suggestions"):
        status["suggestions"] = evo["suggestions"]

    if evo.get("changes_applied"):
        changed_files = [c["file"] for c in evo["changes_applied"]]
        _git.commit(
            f"🧬 evolve v{status['version']}: {evo['summary'][:80]}",
            paths=changed_files + ["version.txt"],
        )

    # ── 4. Earn ───────────────────────────────────────────────────────────────
    _hr("Phase 4 — Earning")
    active  = status.get("active_features", [])
    actions: list[dict] = []

    # Articles (dev.to / Medium)
    if any(f in active for f in ("articles_devto", "articles_medium")):
        n = ov.get("force_articles", 1)
        for i in range(n):
            if n > 1:
                log.info("Article %d/%d", i + 1, n)
            actions += _module("articles", llm, status, errors)

    # Twitter threads
    if "twitter" in active or ov.get("force_twitter"):
        actions += _module("twitter", llm, status, errors)

    # Crypto trading
    if "crypto_binance" in active:
        if ov.get("trade_risk_pct"):
            import bot.earning.crypto as _cr
            _cr.RISK_PCT = ov["trade_risk_pct"]
            log.info("Trade risk overridden to %.0f%%", ov["trade_risk_pct"] * 100)
        actions += _module("crypto", llm, status, errors)

    # NFT minting
    if "nft_ethereum" in active:
        for _ in range(ov.get("force_mint", 1)):
            actions += _module("nft", llm, status, errors)

    if not actions:
        log.warning(
            "No earning actions ran this cycle.\n"
            "Activate modules by adding secrets:\n"
            "  GROQ_API_KEY + DEV_TO_API_KEY         → articles (start here)\n"
            "  TWITTER_API_KEY + 3 others            → Twitter threads\n"
            "  BINANCE_API_KEY + BINANCE_SECRET_KEY  → crypto trading\n"
            "  ETH_PRIVATE_KEY + ETH_WALLET_ADDRESS  → NFT minting"
        )

    # ── 5. Update ─────────────────────────────────────────────────────────────
    _hr("Phase 5 — State Update")
    import bot.earnings as _earn
    import bot.dashboard as _dash

    status = _earn.update(status, actions)
    cycle_usd = status["earnings"]["last_cycle_usd"]
    status["last_earning"] = {"actions": actions, "total_usd": cycle_usd}

    elapsed = round((datetime.now(timezone.utc) - t0).total_seconds())
    status["last_cycle_seconds"] = elapsed
    status["errors"]             = errors[-20:]
    status.pop("_overrides", None)   # don't persist runtime-only key

    _st.save(status)

    try:
        _dash.write_log(actions)
        _dash.write_html(status)
    except Exception as exc:
        log.error("Dashboard write failed: %s", exc)

    _git.commit(
        f"📊 cycle #{status['total_runs']} +${cycle_usd:.4f} {elapsed}s",
        paths=["status.json", "earnings-log.md",
               "docs/index.html", "command.txt", "version.txt"],
    )

    _hr(f"Done | v{status['version']} | {llm.provider} | "
        f"+${cycle_usd:.4f} | {elapsed}s | {len(errors)} err")
    return 0   # Always 0 — partial failures must not break the hourly schedule


# ── Module runner ─────────────────────────────────────────────────────────────

def _module(name: str, llm: Any, status: dict, errors: list) -> list[dict]:
    """Run one earning module with full exception isolation."""
    log.info("▶ %s", name)
    try:
        mod    = importlib.import_module(f"bot.earning.{name}")
        result = mod.run(llm, status)
        return result if isinstance(result, list) else []
    except Exception as exc:
        msg = f"{name}: {exc}"
        log.error("Module '%s' crashed: %s", name, exc)
        log.debug(traceback.format_exc())
        errors.append(msg)
        return [{"platform": name, "success": False, "error": str(exc)[:200]}]


# ── Formatting helpers ────────────────────────────────────────────────────────

def _hr(text: str) -> None:
    bar = "─" * max(0, 60 - len(text))
    log.info("─── %s %s", text, bar)


# Needed for type hint in _module
from typing import Any


if __name__ == "__main__":
    sys.exit(main())
