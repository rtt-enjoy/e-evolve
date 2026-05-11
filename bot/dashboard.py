"""
Dashboard Generator
Writes docs/index.html (GitHub Pages) and appends to earnings-log.md.

HTML structure (sections rendered by dedicated functions):
  _section_header()        — logo, version, provider, feature badges, last-run meta
  _section_stats()         — 4 metric cards + sparkline card
  _section_earnings()      — weekly projection bar + platform breakdown bars
  _section_suggestions()   — ranked growth suggestions with how-to steps
  _section_evolution()     — last evolution status, file changes, error box
  _section_inactive()      — inactive module list
  _section_actions()       — last cycle action table
  _section_errors()        — recent error box (only shown when errors exist)

CSS class naming (readable):
  .stat-grid / .stat-card  — KPI card grid
  .panel                   — content panel box
  .section                 — vertical-spaced section wrapper
  .badge / .badge-green / .badge-red — inline feature badges
  .pill-version / .pill-provider — header pills
  .suggestion-card / .suggestion-rank — growth suggestion layout
  .secret-needed           — secret hint inside suggestion
  .est-earnings            — earnings estimate inside suggestion
  .how-to-steps            — ordered steps list inside suggestion
  .evo-list                — evolution change list
  .evo-error-box           — red error callout inside evolution panel
  .inactive-tag / .inactive-dot — inactive feature badges
  .error-box               — top-level error list
  .breakdown / .breakdown-row / .breakdown-bar — earnings platform bars
  .proj / .proj-row        — weekly projection rows + progress bar
  .prog-bar / .prog-fill   — progress bar track and fill
  .sparkline               — monospace earnings sparkline
  .age-pill                — last-run age pill in header
  .two-col                 — 2-column responsive grid
  .muted / .err            — muted text / error text colors
"""
from __future__ import annotations

import logging
import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_LOG_FILE  = Path("earnings-log.md")
_HTML_FILE = Path("docs/index.html")
_ASSET_DIR = Path("docs/assets")
_CSS_FILE = _ASSET_DIR / "dashboard.css"
_JS_FILE = _ASSET_DIR / "dashboard.js"
_PUBLIC_STATUS_FILE = Path("docs/status.json")
_PUBLIC_LOG_FILE = Path("docs/earnings-log.md")

# Secrets that are free-tier (no payment required to obtain)
_FREE_TIER_SECRETS = frozenset({
    "GROQ_API_KEY", "DEV_TO_API_KEY", "MEDIUM_INTEGRATION_TOKEN",
    "TWITTER_API_KEY", "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET",
})

# Evolution badge config: status → (text-color, bg-color, border-color)
_EVO_BADGE_STYLES: dict[str, tuple[str, str, str]] = {
    "ok":          ("var(--gn)", "rgba(63,185,80,.15)",  "rgba(63,185,80,.4)"),
    "idle":        ("var(--ac)", "rgba(88,166,255,.1)",  "rgba(88,166,255,.3)"),
    "skipped":     ("var(--mu)", "rgba(139,148,158,.1)", "rgba(139,148,158,.3)"),
    "llm_error":   ("var(--rd)", "rgba(248,81,73,.1)",   "rgba(248,81,73,.35)"),
    "apply_error": ("var(--yw)", "rgba(227,179,65,.1)",  "rgba(227,179,65,.35)"),
}


# ── Public API ─────────────────────────────────────────────────────────────────

def write_log(actions: list[dict]) -> None:
    """Append this cycle's completed actions to earnings-log.md."""
    if not actions:
        return

    ts    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"\n### {ts}\n"]

    for a in actions:
        ok   = a.get("success", False)
        icon = "✅" if ok else "❌"
        plat = a.get("platform", "?")

        if "title" in a:                          # article
            url   = a.get("url", "")
            title = a.get("title", "")[:60]
            link  = f"[{title}]({url})" if url else title
            est   = a.get("estimated_usd", 0)
            lines.append(f"- {icon} **{plat}**: {link}  (est. ${est:.2f})")

        elif "side" in a:                         # trade
            side = a.get("side", "")
            sym  = a.get("symbol", "")
            if side in ("BUY", "SELL"):
                val = a.get("value_usd", 0)
                lines.append(f"- {icon} **{plat}** {side} {sym} — ${val:.2f}")
            elif side == "HOLD":
                lines.append(f"- ⏸  **{plat}** {sym} — HOLD")
            else:
                lines.append(f"- ❌ **{plat}** {sym} — {a.get('error','')[:80]}")

        elif "thread_length" in a:                # twitter
            url   = a.get("url", "#")
            topic = a.get("topic", "thread")[:50]
            n     = a.get("thread_length", 0)
            lines.append(f"- {icon} **{plat}** [{topic}]({url}) ({n} tweets)")

        elif "metadata_uri" in a:                 # nft
            tx  = a.get("tx_hash") or "log-only"
            uri = a.get("metadata_uri", "")[:60]
            lines.append(f"- {icon} **{plat}** NFT tx=`{tx}` uri={uri}")

        else:
            lines.append(f"- {icon} **{plat}** action recorded")

    with _LOG_FILE.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    log.info("earnings-log.md updated (%d actions)", len(actions))


def write_html(status: dict[str, Any]) -> None:
    """Regenerate docs/index.html from current status dict."""
    _HTML_FILE.parent.mkdir(exist_ok=True)
    _ASSET_DIR.mkdir(parents=True, exist_ok=True)
    _PUBLIC_STATUS_FILE.write_text(
        json.dumps(
            {k: v for k, v in status.items() if not k.startswith("_")},
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    if _LOG_FILE.exists():
        _PUBLIC_LOG_FILE.write_text(_LOG_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    _CSS_FILE.write_text(_APP_CSS, encoding="utf-8")
    _JS_FILE.write_text(_APP_JS, encoding="utf-8")
    _HTML_FILE.write_text(_render(status), encoding="utf-8")
    log.info("Dashboard written → docs/index.html")


# ── Small helpers ──────────────────────────────────────────────────────────────

def _fmt(iso: Any) -> str:
    """ISO timestamp → 'YYYY-MM-DD HH:MM UTC', or 'never'."""
    if not iso:
        return "never"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(iso)


def _sparkline(history: list) -> str:
    """Unicode block sparkline from a list of floats (empty string if no data)."""
    bars = " ▁▂▃▄▅▆▇█"
    if not history:
        return ""
    mx = max(history) or 1
    return "".join(bars[min(8, int(v / mx * 8))] for v in history)


def _last_run_age(last_run_iso: Any) -> tuple[str, str]:
    """Returns (age_label, css_color). Green <75 min, yellow <3 h, red otherwise."""
    if not last_run_iso:
        return ("never", "var(--rd)")
    try:
        dt    = datetime.fromisoformat(str(last_run_iso).replace("Z", "+00:00"))
        age_s = (datetime.now(timezone.utc) - dt).total_seconds()
        if age_s < 4500:
            return (f"{int(age_s // 60)}m ago", "var(--gn)")
        if age_s < 10800:
            return (f"{int(age_s // 3600)}h {int((age_s % 3600) // 60)}m ago", "var(--yw)")
        return (f"{int(age_s // 3600)}h ago", "var(--rd)")
    except Exception:
        return (str(last_run_iso), "var(--mu)")


def _evo_status(evo: dict) -> str:
    """Classify evolution result into one of: ok | idle | skipped | llm_error | apply_error."""
    err      = evo.get("error")
    err_type = evo.get("error_type", "")
    summary  = evo.get("summary", "")
    if not err and evo.get("changes_applied"):
        return "ok"
    if not err and "skipped by owner" in summary.lower():
        return "skipped"
    if err and err_type in ("413", "json", "api"):
        return "llm_error"
    if err:
        return "apply_error"
    return "idle"


def _missing_secrets_for(s: dict[str, Any], feature: str, fallback: list[str]) -> list[str]:
    """Return only secrets still missing for a feature, using the safe status snapshot."""
    readiness = s.get("secret_readiness", {}) or {}
    info = readiness.get(feature)
    if info is not None:
        return list(info.get("missing", []))
    if feature in set(s.get("active_features", [])):
        return []
    return list(fallback)


def _missing_secret_names(s: dict[str, Any]) -> set[str]:
    readiness = s.get("secret_readiness", {}) or {}
    if not readiness:
        missing: set[str] = set()
        active = set(s.get("active_features", []))
        for feature in s.get("inactive_features", []):
            if feature in active:
                continue
            missing.update(_MODULE_SETUP.get(feature, {}).get("secrets", []))
        return missing
    missing: set[str] = set()
    for info in readiness.values():
        missing.update(info.get("missing", []))
    return missing


# ── Section renderers ──────────────────────────────────────────────────────────

_PROVIDER_PILL_CLASS: dict[str, str] = {
    "gemini":     "pill-provider-gemini",
    "groq":       "pill-provider-groq",
    "openrouter": "pill-provider-openrouter",
    "anthropic":  "pill-provider",
    "claude-cli": "pill-provider",
}

_PROVIDER_ROLE_LABELS = [
    ("upgrade", "Up"),
    ("research", "Re"),
    ("post", "Po"),
    ("think", "Th"),
    ("fast", "Fa"),
    ("experiment", "Ex"),
]

_ROLE_LABELS = {
    "upgrade": "Upgrade",
    "research": "Research",
    "post": "Post",
    "think": "Evolution",
    "fast": "Research/content",
    "experiment": "Model experiments",
}


def _provider_pills(provider: str, llm_roles: dict) -> str:
    """Render provider pills. If role info available show per-role pills, else single pill."""
    if llm_roles:
        pills = []
        for role, icon in _PROVIDER_ROLE_LABELS:
            p = llm_roles.get(role)
            if p:
                cls = _PROVIDER_PILL_CLASS.get(p, "pill-provider")
                pills.append(f'<span class="{cls}" title="{role}">{icon} {p}</span>')
        return "".join(pills) if pills else f'<span class="pill-provider">{provider}</span>'
    cls = _PROVIDER_PILL_CLASS.get(provider, "pill-provider")
    return f'<span class="{cls}">{provider}</span>'


def _section_header(version: str, provider: str, active: list, last_run: str,
                    age_label: str, age_color: str, n_runs: int, cycle_str: str,
                    llm_roles: dict | None = None) -> str:
    badges = (
        "".join(f'<span class="badge badge-green">{f}</span>' for f in active)
        or '<span class="badge badge-red">no active modules — add a secret</span>'
    )
    provider_html = _provider_pills(provider, llm_roles or {})
    return f"""<header>
  <div class="logo">🤖</div>
  <div>
    <h1>E-Evolve
      <span class="pill-version" id="hdr-version">{version}</span>
      <span id="hdr-providers">{provider_html}</span>
    </h1>
    <div style="margin-top:5px" id="hdr-badges">{badges}</div>
    <div class="muted" style="font-size:.8rem;margin-top:5px">
      Last cycle: <span id="hdr-last-run">{last_run}</span>
      <span class="age-pill" id="hdr-age" style="background:rgba(0,0,0,.3);color:{age_color};border:1px solid {age_color}">{age_label}</span>
      &nbsp;·&nbsp; Total cycles: <span id="hdr-total-runs">{n_runs}</span>
      &nbsp;·&nbsp; Cycle time: <span id="hdr-cycle-time">{cycle_str}</span>
    </div>
  </div>
</header>"""


def _section_stats(earn: dict, n_runs: int, active: list, inactive: list,
                   history: list, spark: str, spark_tip: str, s: dict = None) -> str:
    s = s or {}
    spark_card = (
        f'<div class="stat-card">'
        f'<div class="stat-value sparkline" title="{spark_tip}">{spark}</div>'
        f'<div class="stat-label">Last {len(history)} earning cycles</div>'
        f'</div>'
    ) if spark else ""

    usdt_bal   = float(s.get("usdt_balance", 0.0))
    usdt_recv  = s.get("usdt_received")
    recv_badge = (
        f'<div class="stat-sub" id="stat-usdt-recv" style="color:var(--gn)">+{usdt_recv:.6f} received</div>'
    ) if usdt_recv else '<div class="stat-sub" id="stat-usdt-recv"></div>'

    usdt_card = (
        f'<div class="stat-card">'
        f'<div class="stat-value" id="stat-usdt-bal" style="color:var(--gn)">{usdt_bal:.2f} USDT</div>'
        f'<div class="stat-label">Wallet balance</div>'
        f'{recv_badge}'
        f'</div>'
    ) if s.get("usdt_wallet") else ""

    return f"""<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-value" id="stat-total">${earn.get("total_usd", 0):.2f}</div>
    <div class="stat-label">Total earned</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="stat-week" style="color:var(--yw)">${earn.get("this_week_usd", 0):.2f}</div>
    <div class="stat-label">This week</div>
    <div class="stat-sub" id="stat-last-cycle">last cycle: ${earn.get("last_cycle_usd", 0):.4f}</div>
  </div>
  <div class="stat-card">
    <div class="stat-value stat-neutral" id="stat-runs">{n_runs}</div>
    <div class="stat-label">Cycles run</div>
  </div>
  <div class="stat-card">
    <div class="stat-value stat-neutral" id="stat-active" style="color:var(--pu)">{len(active)}</div>
    <div class="stat-label">Active modules</div>
    <div class="stat-sub" id="stat-inactive">{len(inactive)} inactive</div>
  </div>
  {usdt_card}
  {spark_card}
</div>"""


def _section_earnings(earn: dict) -> str:
    """Weekly projection + platform breakdown bars. Empty string if no data."""
    proj_html      = _render_projection(earn)
    breakdown_html = _render_breakdown(earn.get("breakdown", {}))
    if not proj_html and not breakdown_html:
        return ""
    return f"""<div class="section">
  <h2>📈 Earnings Analysis</h2>
  <div class="panel">
    {proj_html}
    {breakdown_html}
  </div>
</div>"""


def _render_projection(earn: dict) -> str:
    history = earn.get("history", [])
    if len(history) < 2:
        return ""
    avg       = sum(history) / len(history)
    projected = round(avg * 168, 2)           # 168 cycles/week (hourly)
    this_week = earn.get("this_week_usd", 0)
    goal      = 10.0
    pct       = min(100, int(this_week / goal * 100)) if goal else 0
    bar_color = "var(--gn)" if pct >= 50 else ("var(--yw)" if pct >= 20 else "var(--rd)")
    return (
        f'<div class="proj">'
        f'<div class="proj-row">'
        f'<span>Weekly projection (avg {avg:.4f}/cycle × 168):</span>'
        f'<strong style="color:var(--gn)">${projected:.2f}/week</strong>'
        f'</div>'
        f'<div class="proj-row">'
        f'<span>Progress to $10/week goal:</span>'
        f'<span style="color:{bar_color}">{pct}%</span>'
        f'</div>'
        f'<div class="prog-bar"><div class="prog-fill" style="width:{pct}%;background:{bar_color}"></div></div>'
        f'</div>'
    )


def _section_research_focus(s: dict[str, Any]) -> str:
    """Rank the next practical revenue moves from current state."""
    active   = set(s.get("active_features", []))
    missing  = _missing_secret_names(s)
    earn     = s.get("earnings", {})
    last     = float(earn.get("last_cycle_usd", 0) or 0)
    week     = float(earn.get("this_week_usd", 0) or 0)
    has_cta  = bool(os.getenv("EARN_CTA_URL", "").strip())

    cards: list[dict[str, str]] = []
    if "articles_devto" not in active and "DEV_TO_API_KEY" in missing:
        cards.append({
            "rank": "1",
            "title": "Start the free content loop",
            "metric": "$0 setup",
            "body": "Use Groq plus dev.to first. It costs nothing, runs on GitHub Actions, and avoids funded trading or gas fees.",
            "action": "Add DEV_TO_API_KEY",
        })
    if "articles_devto" in active and "MEDIUM_INTEGRATION_TOKEN" in missing:
        cards.append({
            "rank": str(len(cards) + 1),
            "title": "Dual-publish every article",
            "metric": "$0 setup",
            "body": "Add Medium so the same generated article reaches a second audience with no extra LLM call.",
            "action": "Add MEDIUM_INTEGRATION_TOKEN",
        })
    if "articles_devto" in active and not has_cta:
        cards.append({
            "rank": str(len(cards) + 1),
            "title": "Add a free article CTA",
            "metric": "No API key",
            "body": "Set EARN_CTA_URL to a sponsor, tip, newsletter, affiliate, or product link so every free article has a conversion path.",
            "action": "Add variable EARN_CTA_URL",
        })
    if "articles_devto" in active and has_cta:
        cards.append({
            "rank": str(len(cards) + 1),
            "title": "Write buyer-intent articles",
            "metric": "Active",
            "body": "The article loop now periodically chooses no-budget, tool-adoption, and implementation topics that match the configured CTA.",
            "action": "Tune config.strategy articles.buyer_intent_ratio",
        })
    payout_missing = [
        key for key in ("BINANCE_API_KEY", "BINANCE_SECRET_KEY", "BINANCE_WITHDRAW_ADDRESS")
        if key in missing
    ]
    if "usdt_wallet" in active and payout_missing:
        cards.append({
            "rank": str(len(cards) + 1),
            "title": "Wallet is ready",
            "metric": "Payout path",
            "body": "The USDT address is configured, so the dashboard can track incoming funds while payout automation waits for exchange keys.",
            "action": "Add " + ", ".join(payout_missing),
        })
    twitter_missing = [
        key for key in ("TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET")
        if key in missing
    ]
    if twitter_missing:
        cards.append({
            "rank": str(len(cards) + 1),
            "title": "Turn articles into distribution",
            "metric": "Optional",
            "body": "Threads can recycle each article into short-form discovery, but only enable this if your X developer access is actually free.",
            "action": "Add " + ", ".join(twitter_missing),
        })
    llm_missing = [
        key for key in ("GEMINI_API_KEY", "OPENROUTER_API_KEY")
        if key in missing
    ]
    if llm_missing:
        cards.append({
            "rank": str(len(cards) + 1),
            "title": "Improve research depth",
            "metric": "$0 setup",
            "body": "Activate a long-context thinking provider so evolution and article research rely less on the Groq short-context path.",
            "action": "Add " + " or ".join(llm_missing),
        })
    trading_missing = [
        key for key in ("BINANCE_API_KEY", "BINANCE_SECRET_KEY")
        if key in missing
    ]
    if trading_missing and ("articles_devto" in active or "articles_medium" in active):
        cards.append({
            "rank": str(len(cards) + 1),
            "title": "Add capital-backed earning",
            "metric": "Needs funds",
            "body": "Trading is the first module with direct compounding potential, but it should wait until API keys and risk limits are deliberate.",
            "action": "Fund exchange account, then add " + ", ".join(trading_missing),
        })
    if not cards:
        trend = "positive" if last > 0 or week > 0 else "idle"
        cards.append({
            "rank": "1",
            "title": "Tighten the active loop",
            "metric": trend,
            "body": "All listed modules are active. Watch conversion by platform and raise output only where the last-cycle signal is positive.",
            "action": "Use Owner Orders for controlled experiments",
        })

    cards_html = "".join(
        f'<div class="research-card">'
        f'<span class="research-rank">{c["rank"]}</span>'
        f'<div><div class="research-top"><strong>{c["title"]}</strong>'
        f'<span>{c["metric"]}</span></div>'
        f'<p>{c["body"]}</p>'
        f'<code>{c["action"]}</code></div>'
        f'</div>'
        for c in cards[:4]
    )
    return f"""<div class="section">
  <h2>Research & Revenue Focus</h2>
  <div class="research-grid">{cards_html}</div>
</div>"""


def _section_llm_workflows(s: dict[str, Any]) -> str:
    """Show how model roles are routed this cycle."""
    roles = s.get("llm_workflows", {}) or {}
    active_roles = s.get("llm_roles", {}) or {}
    if not roles and not active_roles:
        return ""

    role_order = ("upgrade", "research", "post")
    if not any(role in roles or role in active_roles for role in role_order):
        role_order = ("think", "fast", "experiment")

    cards = ""
    for role in role_order:
        cfg = roles.get(role, {})
        provider = active_roles.get(role) or cfg.get("provider", "unknown")
        model = cfg.get("model", "")
        purpose = cfg.get("purpose", "")
        active = bool(active_roles.get(role) or cfg.get("active"))
        missing = cfg.get("secret")
        state_cls = "workflow-ready" if active else "workflow-missing"
        state = "ready" if active else f"needs {missing or 'setup'}"
        cards += (
            f'<div class="workflow-card {state_cls}">'
            f'<div class="workflow-top"><strong>{_ROLE_LABELS.get(role, role)}</strong>'
            f'<span>{state}</span></div>'
            f'<div class="workflow-provider">{provider}</div>'
            f'<div class="workflow-model">{html.escape(str(model))}</div>'
            f'<p>{purpose}</p>'
            f'</div>'
        )

    return f"""<div class="section">
  <h2>AI Model Workflow</h2>
  <div class="workflow-grid">{cards}</div>
</div>"""


def _section_secret_readiness(s: dict[str, Any]) -> str:
    """Safe secret audit: names only, never values."""
    readiness = s.get("secret_readiness", {}) or {}
    if not readiness:
        return ""

    priority = [
        "llm_gemini", "llm_openrouter", "llm_groq",
        "articles_devto", "articles_medium", "usdt_wallet",
        "twitter", "crypto_binance", "crypto_payout", "nft_ethereum",
    ]
    rows = ""
    for feature in priority:
        info = readiness.get(feature)
        if not info:
            continue
        present = int(info.get("present_count", 0))
        required = int(info.get("required_count", 0)) or 1
        pct = int(present / required * 100)
        present_names = list(info.get("present", []))
        missing_names = list(info.get("missing", []))
        detail_names = present_names if present_names else missing_names
        detail = ", ".join(detail_names) or "none"
        label = "active" if info.get("active") else f"{present}/{required}"
        rows += (
            f'<div class="secret-row">'
            f'<div><strong>{html.escape(feature)}</strong><span>{html.escape(label)}</span></div>'
            f'<div class="secret-meter"><div style="width:{pct}%"></div></div>'
            f'<code>{html.escape(detail)}</code>'
            f'</div>'
        )
    if not rows:
        return ""
    return f"""<div class="section">
  <h2>Secret Readiness</h2>
  <div class="panel">
    <p class="muted secret-intro">Current GitHub Actions secret audit. Values are never stored or shown.</p>
    {rows}
  </div>
</div>"""


def _render_breakdown(breakdown: dict) -> str:
    if not breakdown:
        return ""
    total = sum(breakdown.values()) or 1
    rows  = ""
    for plat, amt in sorted(breakdown.items(), key=lambda x: -x[1]):
        pct  = int(amt / total * 100)
        rows += (
            f'<div class="breakdown-row">'
            f'<span class="breakdown-label">{plat}</span>'
            f'<div class="breakdown-bar-track"><div class="breakdown-bar" style="width:{pct}%"></div></div>'
            f'<span class="breakdown-amount">${amt:.4f}</span>'
            f'</div>'
        )
    return f'<div class="breakdown">{rows}</div>'


def _section_suggestions(suggs: list, s: dict[str, Any]) -> str:
    icons   = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    missing = _missing_secret_names(s)
    content = ""
    visible = [
        sg for sg in suggs
        if not sg.get("secret_needed") or sg.get("secret_needed") in missing
    ]
    for i, sg in enumerate(visible[:5]):
        sec      = sg.get("secret_needed")
        est      = sg.get("estimated_weekly_usd", 0)
        is_free  = sg.get("free_tier", sec in _FREE_TIER_SECRETS if sec else False)
        free_badge = (
            '<span class="free-badge">Free to start</span>'
        ) if is_free else ""
        secret_block = (
            f'<div class="secret-needed">Add secret: <code>{sec}</code></div>'
        ) if sec else ""
        est_block = (
            f'<div class="est-earnings">~${est:.0f}/week estimated</div>'
        ) if est else ""
        how_to = sg.get("how_to", [])
        how_block = (
            f'<ol class="how-to-steps">{"".join(f"<li>{step}</li>" for step in how_to)}</ol>'
        ) if how_to else ""
        icon = icons[i] if i < len(icons) else "•"
        content += (
            f'<div class="suggestion-card">'
            f'<span class="suggestion-rank">{icon}</span>'
            f'<div><strong>{sg.get("title", "")}</strong>{free_badge}'
            f'<p>{sg.get("description", "")}</p>'
            f'{secret_block}{est_block}{how_block}</div>'
            f'</div>'
        )
    if not content:
        content = "<p class='muted'>Suggestions appear after the first evolution cycle.</p>"
    return f"""<div class="section">
  <h2>🧠 Smart Growth Suggestions</h2>
  <div class="panel">{content}</div>
</div>"""


def _section_evolution(evo: dict) -> str:
    status  = _evo_status(evo)
    bc, bg, border = _EVO_BADGE_STYLES.get(status, _EVO_BADGE_STYLES["ok"])
    badge   = (
        f'<span style="display:inline-block;padding:1px 8px;border-radius:20px;'
        f'font-size:.73rem;font-weight:700;color:{bc};background:{bg};'
        f'border:1px solid {border};margin-left:8px">{status}</span>'
    )
    summary = evo.get("summary", "—")
    changes = "".join(
        f'<li><code>{c.get("file", "")}</code> — {c.get("reason", "")[:80]}</li>'
        for c in evo.get("changes_applied", [])
    ) or "<li>No file changes this cycle</li>"

    err_html = ""
    evo_err  = evo.get("error")
    if evo_err:
        import re as _re
        match      = _re.search(r"'message':\s*'([^']{1,200})'", evo_err)
        clean_msg  = match.group(1) if match else evo_err[:200]
        type_label = {
            "413": "413 Too Large", "json": "JSON Parse Error", "api": "API Error"
        }.get(evo.get("error_type", ""), "Error")
        err_html = (
            f'<div class="evo-error-box">'
            f'<strong>{type_label}:</strong> {clean_msg}'
            f'</div>'
        )

    return f"""<div class="section">
  <h2>⚡ Last Evolution</h2>
  <div class="panel">
    <p style="margin-bottom:9px"><strong>{summary}</strong>{badge}</p>
    <ul class="evo-list">{changes}</ul>
    {err_html}
  </div>
</div>"""


_MODULE_SETUP: dict[str, dict] = {
    "llm_anthropic": {
        "label": "Anthropic (Claude)",
        "secrets": ["ANTHROPIC_API_KEY"],
        "free": False,
        "signup_url": "https://console.anthropic.com/",
        "steps": [
            "Go to console.anthropic.com → sign up (email only, no KYC)",
            "API Keys → Create Key → copy it",
            "GitHub repo → Settings → Secrets → New secret: <code>ANTHROPIC_API_KEY</code>",
        ],
        "note": "Paid API credit. Skip this while running the no-money setup.",
    },
    "llm_gemini": {
        "label": "Google Gemini",
        "secrets": ["GEMINI_API_KEY"],
        "free": True,
        "signup_url": "https://aistudio.google.com/app/apikey",
        "steps": [
            "Go to aistudio.google.com → sign in with Google",
            "Click <em>Get API key</em> → Create API key",
            "GitHub → Settings → Secrets → <code>GEMINI_API_KEY</code>",
        ],
        "note": "Completely free tier, no credit card needed.",
    },
    "llm_openrouter": {
        "label": "OpenRouter",
        "secrets": ["OPENROUTER_API_KEY"],
        "free": True,
        "signup_url": "https://openrouter.ai/keys",
        "steps": [
            "openrouter.ai → Sign up (email/GitHub, no KYC)",
            "Keys → Create Key",
            "GitHub → Secrets → <code>OPENROUTER_API_KEY</code>",
        ],
        "note": "Many free models available (Mistral, Llama, etc.).",
    },
    "articles_medium": {
        "label": "Medium",
        "secrets": ["MEDIUM_INTEGRATION_TOKEN"],
        "free": True,
        "signup_url": "https://medium.com/me/settings/security",
        "steps": [
            "medium.com → sign in → Settings → Security",
            "Integration tokens → Get integration token",
            "GitHub → Secrets → <code>MEDIUM_INTEGRATION_TOKEN</code>",
        ],
        "note": "Free. Doubles article reach alongside dev.to.",
    },
    "twitter": {
        "label": "Twitter / X",
        "secrets": ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"],
        "free": False,
        "signup_url": "https://developer.twitter.com/en/portal/dashboard",
        "steps": [
            "developer.twitter.com → sign in → Create project + app",
            "Keys and Tokens → generate all 4 keys",
            "GitHub → Secrets → add all 4: <code>TWITTER_API_KEY</code>, <code>TWITTER_API_SECRET</code>, <code>TWITTER_ACCESS_TOKEN</code>, <code>TWITTER_ACCESS_SECRET</code>",
        ],
        "note": "Developer access can require paid or approved access. Treat as optional for the free path.",
    },
    "crypto_binance": {
        "label": "Crypto Trading (KuCoin — no KYC)",
        "secrets": ["BINANCE_API_KEY", "BINANCE_SECRET_KEY"],
        "free": False,
        "signup_url": "https://www.kucoin.com/",
        "steps": [
            "kucoin.com → Sign up (email only, no ID required for basic tier)",
            "Account → API Management → Create API",
            "GitHub → Secrets → <code>BINANCE_API_KEY</code> + <code>BINANCE_SECRET_KEY</code> (bot reads these names)",
        ],
        "note": "KuCoin unverified: up to ~$1k/day withdrawal. Deposit USDT to start.",
    },
    "nft_ethereum": {
        "label": "NFT Minting (Ethereum)",
        "secrets": ["ETH_PRIVATE_KEY", "ETH_WALLET_ADDRESS"],
        "free": False,
        "signup_url": "https://metamask.io/",
        "steps": [
            "Install MetaMask → create wallet → copy private key + address",
            "Get free RPC: alchemy.com → sign up (email only) → create app → copy HTTP URL (optional, uses public RPC by default)",
            "GitHub → Secrets → <code>ETH_PRIVATE_KEY</code> + <code>ETH_WALLET_ADDRESS</code>",
        ],
        "note": "Needs ETH for gas fees (~$1–5/mint on mainnet). Use testnet first.",
    },
}


def _section_inactive(inactive: list, s: dict[str, Any]) -> str:
    if not inactive:
        return f"""<div class="section">
  <h2>🔓 Activate Modules</h2>
  <div class="panel"><p class="muted">All features active 🎉</p></div>
</div>"""

    cards = ""
    for feat in inactive:
        cfg = _MODULE_SETUP.get(feat)
        if not cfg:
            cards += f'<div class="inactive-tag"><span class="inactive-dot"></span>{feat}</div>'
            continue
        missing = _missing_secrets_for(s, feat, cfg["secrets"])
        if not missing:
            continue
        free_badge = (
            '<span class="free-badge">Free</span>'
            if cfg["free"]
            else '<span class="paid-badge">Needs funds</span>'
        )
        secrets_html = "".join(f'<code class="secret-code">{secret}</code>' for secret in missing)
        if missing == cfg["secrets"]:
            steps_html = "".join(f"<li>{step}</li>" for step in cfg["steps"])
        else:
            steps_html = "<li>GitHub -> Settings -> Secrets -> add the remaining secrets shown above</li>"
        note_html    = f'<div class="activate-note">{cfg["note"]}</div>' if cfg.get("note") else ""
        cards += f"""<div class="activate-card">
  <div class="activate-header">
    <strong>{cfg["label"]}</strong>{free_badge}
    <a class="activate-link" href="{cfg["signup_url"]}" target="_blank" rel="noopener">Get API key →</a>
  </div>
  <div class="activate-secrets">{secrets_html}</div>
  <ol class="activate-steps">{steps_html}</ol>
  {note_html}
</div>"""

    return f"""<div class="section">
  <h2>🔓 Activate Modules</h2>
  <div class="panel">{cards or '<p class="muted">No missing setup secrets.</p>'}</div>
</div>"""


def _section_actions(actions: list) -> str:
    if not actions:
        return """<div class="section">
  <h2>💰 Last Cycle Actions</h2>
  <div class="panel"><p class="muted">No actions yet — add a secret to activate an earning module.</p></div>
</div>"""

    rows = ""
    for a in actions[-20:]:
        ok   = a.get("success", False)
        plat = a.get("platform", "?")
        icon = "✅" if ok else "❌"
        err  = (a.get("error") or "")[:80]

        if "title" in a:
            title  = (a.get("title") or "").strip()
            url    = (a.get("url") or "").strip()
            detail = (
                f'<a href="{url}" target="_blank">{title[:50]}</a>'
                if ok and title and url
                else f'<span class="err">{plat} — {err or "unknown error"}</span>'
            )
        elif "side" in a:
            detail = f'{a.get("side")} {a.get("symbol", "")} ${a.get("value_usd", 0):.2f}'
        elif "thread_length" in a:
            url    = (a.get("url") or "").strip()
            topic  = (a.get("topic") or "thread")[:50]
            detail = (
                f'<a href="{url}" target="_blank">{topic}</a>'
                if url
                else f'<span class="err">{topic} — {err}</span>'
            )
        else:
            detail = (a.get("metadata_uri") or err or "")[:50]

        rows += f"<tr><td>{icon}</td><td>{plat}</td><td>{detail}</td></tr>"

    n = len(actions)
    return f"""<div class="section">
  <h2>💰 Last Cycle Actions</h2>
  <div class="panel">
    <table>
      <thead><tr><th></th><th>Platform</th><th>Detail</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p class="muted" style="font-size:.78rem;margin-top:8px">
      Showing last {min(n, 20)} of {n} · <a href="earnings-log.md">full log</a>
    </p>
  </div>
</div>"""


_ORDER_PRESETS: list[tuple[str, str]] = [
    ("force articles 3",       "Post 3 articles this cycle"),
    ("force articles 1",       "Run one research-backed article"),
    ("force trade aggressive",  "Raise trade risk to 5%"),
    ("skip evolution",          "Skip Phase 3 this cycle"),
    ("post thread",             "Force a Twitter thread"),
    ("reset earnings",          "Zero this_week_usd"),
    ("status report",           "Dump full status to workflow log"),
    ("force mint 1",            "Mint 1 NFT this cycle"),
    ("force trade conservative","Lower trade risk to 1%"),
    ("force articles 5",       "Stress-test content throughput"),
]

_ORDERS_JS = """\
<script>
(function() {
  var _cmds = [];
  window.addOrder = function(cmd) {
    if (!_cmds.includes(cmd)) _cmds.push(cmd);
    _sync();
  };
  window.addCustomOrder = function() {
    var el = document.getElementById('customOrder');
    var val = el.value.trim();
    if (val && !_cmds.includes(val)) { _cmds.push(val); _sync(); }
    el.value = ''; el.focus();
  };
  window.clearCommands = function() {
    _cmds = [];
    document.getElementById('commandOutput').value = '# no commands';
  };
  window.copyCommands = function() {
    var ta = document.getElementById('commandOutput');
    navigator.clipboard.writeText(ta.value).then(function() {
      var t = document.getElementById('toast');
      t.classList.add('show');
      setTimeout(function() { t.classList.remove('show'); }, 2000);
    }).catch(function() { ta.select(); document.execCommand('copy'); });
  };
  window.downloadCommands = function() {
    var content = document.getElementById('commandOutput').value;
    var blob = new Blob([content], { type: 'text/plain' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'command.txt'; a.click();
  };
  function _sync() {
    document.getElementById('commandOutput').value =
      _cmds.length ? _cmds.join('\\n') : '# no commands';
  }
  document.getElementById('commandOutput').addEventListener('input', function() {
    _cmds = this.value.split('\\n').map(function(l){return l.trim();}).filter(Boolean);
  });
})();
</script>
<div class="copy-toast" id="toast">Copied to clipboard!</div>"""

_LIVE_JS = """\
<script>
(function() {
  var POLL_MS = 60000;
  var runEl = document.getElementById('hdr-total-runs');
  var versionEl = document.getElementById('hdr-version');
  var initialRun = Number(runEl ? runEl.textContent : 0);
  var initialVersion = versionEl ? versionEl.textContent : '';
  var reloading = false;
  var PROVIDERS = {
    gemini:     'pill-provider-gemini',
    groq:       'pill-provider-groq',
    openrouter: 'pill-provider-openrouter',
    anthropic:  'pill-provider',
    'claude-cli': 'pill-provider'
  };
  var ROLE_ICONS = { upgrade: 'Up', research: 'Re', post: 'Po', think: 'Th', fast: 'Fa', experiment: 'Ex' };

  function fmt(iso) {
    if (!iso) return 'never';
    try {
      var d = new Date(iso);
      return d.getUTCFullYear() + '-' +
        String(d.getUTCMonth()+1).padStart(2,'0') + '-' +
        String(d.getUTCDate()).padStart(2,'0') + ' ' +
        String(d.getUTCHours()).padStart(2,'0') + ':' +
        String(d.getUTCMinutes()).padStart(2,'0') + ' UTC';
    } catch(e) { return iso; }
  }

  function age(iso) {
    if (!iso) return ['never', 'var(--rd)'];
    var secs = (Date.now() - new Date(iso).getTime()) / 1000;
    if (secs < 4500) return [Math.floor(secs/60) + 'm ago', 'var(--gn)'];
    if (secs < 10800) return [Math.floor(secs/3600) + 'h ' + Math.floor((secs%3600)/60) + 'm ago', 'var(--yw)'];
    return [Math.floor(secs/3600) + 'h ago', 'var(--rd)'];
  }

  function providerPills(provider, roles) {
    if (roles && Object.keys(roles).length) {
      var order = ['upgrade','research','post','think','fast','experiment'];
      return order.filter(function(r){ return roles[r]; }).map(function(r) {
        var p = roles[r];
        var cls = PROVIDERS[p] || 'pill-provider';
        return '<span class="' + cls + '" title="' + r + '">' + (ROLE_ICONS[r]||'') + ' ' + p + '</span>';
      }).join('');
    }
    var cls = PROVIDERS[provider] || 'pill-provider';
    return '<span class="' + cls + '">' + provider + '</span>';
  }

  function setText(id, val) {
    var el = document.getElementById(id);
    if (el) el.textContent = val;
  }
  function setHTML(id, val) {
    var el = document.getElementById(id);
    if (el) el.innerHTML = val;
  }

  function applyStatus(s) {
    var earn = s.earnings || {};
    var active = s.active_features || [];
    var inactive = s.inactive_features || [];
    var nextRun = Number(s.total_runs || 0);
    var nextVersion = s.version || '';

    if (!reloading && ((initialRun && nextRun && nextRun !== initialRun) ||
        (initialVersion && nextVersion && nextVersion !== initialVersion))) {
      reloading = true;
      window.location.reload();
      return;
    }

    // Header
    setText('hdr-version', s.version || '');
    setHTML('hdr-providers', providerPills(s.llm_provider || '', s.llm_roles || {}));
    var badges = active.map(function(f){
      return '<span class="badge badge-green">' + f + '</span>';
    }).join('') || '<span class="badge badge-red">no active modules — add a secret</span>';
    setHTML('hdr-badges', badges);
    setText('hdr-last-run', fmt(s.last_run));
    setText('hdr-total-runs', s.total_runs || 0);
    setText('hdr-cycle-time', s.last_cycle_seconds ? s.last_cycle_seconds + 's' : '—');

    var agePair = age(s.last_run);
    var ageEl = document.getElementById('hdr-age');
    if (ageEl) {
      ageEl.textContent = agePair[0];
      ageEl.style.color = agePair[1];
      ageEl.style.borderColor = agePair[1];
    }

    // Stats
    setText('stat-total', '$' + (earn.total_usd || 0).toFixed(2));
    setText('stat-week', '$' + (earn.this_week_usd || 0).toFixed(2));
    setText('stat-last-cycle', 'last cycle: $' + (earn.last_cycle_usd || 0).toFixed(4));
    setText('stat-runs', s.total_runs || 0);
    setText('stat-active', active.length);
    setText('stat-inactive', inactive.length + ' inactive');

    // USDT wallet balance (real-time from status.json)
    if (s.usdt_wallet) {
      var addrEl = document.getElementById('usdt-addr');
      if (addrEl) addrEl.textContent = s.usdt_wallet;
      var copyBtn = document.querySelector('.btn-copy-addr');
      if (copyBtn) copyBtn.setAttribute('onclick', "navigator.clipboard.writeText('" + s.usdt_wallet + "')");
    }
    if (s.usdt_balance !== undefined) {
      setText('stat-usdt-bal', parseFloat(s.usdt_balance).toFixed(2) + ' USDT');
    }
    var recvEl = document.getElementById('stat-usdt-recv');
    if (recvEl) {
      if (s.usdt_received) {
        recvEl.textContent = '+' + parseFloat(s.usdt_received).toFixed(6) + ' received';
        recvEl.style.color = 'var(--gn)';
      } else {
        recvEl.textContent = '';
      }
    }

    // Live indicator
    var dot = document.getElementById('live-dot');
    if (dot) {
      dot.style.background = 'var(--gn)';
      setTimeout(function(){ dot.style.background = 'var(--br)'; }, 1200);
    }
    var ts = document.getElementById('live-ts');
    if (ts) ts.textContent = fmt(new Date().toISOString());
  }

  function poll() {
    fetch('status.json?_=' + Date.now())
      .then(function(r){
        if (!r.ok) throw new Error('status fetch failed');
        return r.json();
      })
      .then(applyStatus)
      .catch(function(){
        var dot = document.getElementById('live-dot');
        if (dot) dot.style.background = 'var(--rd)';
      });
  }

  // Tick age pill every minute even without new data
  function tickAge() {
    var lastRunEl = document.getElementById('hdr-last-run');
    if (!lastRunEl) return;
    var txt = lastRunEl.textContent;
    if (!txt || txt === 'never') return;
    // parse back to ISO
    var iso = txt.replace(' UTC', ':00Z').replace(' ', 'T');
    var agePair = age(iso);
    var ageEl = document.getElementById('hdr-age');
    if (ageEl) {
      ageEl.textContent = agePair[0];
      ageEl.style.color = agePair[1];
      ageEl.style.borderColor = agePair[1];
    }
  }

  poll();
  setInterval(poll, POLL_MS);
  setInterval(tickAge, 60000);
})();
</script>"""


def _section_orders() -> str:
    btns = "".join(
        f'<button class="order-btn" onclick="addOrder(\'{cmd}\')">'
        f'<span class="ob-label">{cmd}</span>'
        f'<span class="ob-desc">{desc}</span>'
        f'</button>'
        for cmd, desc in _ORDER_PRESETS
    )
    return f"""<div class="section">
  <h2>📋 Owner Orders</h2>
  <div class="panel">
    <p class="muted" style="font-size:.82rem;margin-bottom:12px">
      Queue commands for the next evolution cycle. Click a preset or type a custom order.
    </p>
    <div class="orders-grid">{btns}</div>
    <div class="order-custom-row">
      <input type="text" id="customOrder" class="order-input"
             placeholder="Custom order (e.g. force articles 5)"
             onkeydown="if(event.key==='Enter'){{addCustomOrder()}}" />
      <button class="btn btn-secondary" onclick="addCustomOrder()">Add</button>
    </div>
    <textarea id="commandOutput" class="order-textarea"
              placeholder="# no commands&#10;(click presets or add custom orders above)"></textarea>
    <div class="order-actions">
      <button class="btn btn-primary" onclick="copyCommands()">📋 Copy command.txt</button>
      <button class="btn btn-secondary" onclick="downloadCommands()">⬇ Download</button>
      <button class="btn btn-danger" onclick="clearCommands()">✕ Clear</button>
    </div>
    <div class="order-hint">
      <strong>How to apply:</strong>
      Copy the text above, commit it to <code>command.txt</code> in your repo root.
      The next cycle (~1h) executes and clears it automatically.<br>
      CLI: <code>echo "your command" &gt; command.txt &amp;&amp; git add command.txt &amp;&amp; git commit -m "cmd" &amp;&amp; git push</code>
    </div>
  </div>
</div>"""


def _section_errors(errors: list) -> str:
    if not errors:
        return ""
    items = "".join(f"<li>{e[:120]}</li>" for e in errors[-5:])
    return f'<div class="error-box"><h3>⚠️ Recent Errors</h3><ul>{items}</ul></div>'


# ── CSS ────────────────────────────────────────────────────────────────────────

_CSS = """\
:root {
  --bg: #0d1117; --sf: #161b22; --br: #30363d;
  --tx: #c9d1d9; --mu: #8b949e;
  --ac: #58a6ff; --gn: #3fb950; --rd: #f85149;
  --pu: #bc8cff; --yw: #e3b341;
  --gemini: #4285f4; --groq: #f97316; --openrouter: #10b981;
  --f: 'Segoe UI', system-ui, sans-serif;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg); color: var(--tx); font-family: var(--f);
  padding: 20px; max-width: 960px; margin: 0 auto;
}
a { color: var(--ac); }
h2 {
  font-size: .82rem; text-transform: uppercase;
  letter-spacing: .07em; color: var(--mu); margin-bottom: 12px;
}

/* ── Header ── */
header {
  display: flex; align-items: flex-start; gap: 14px;
  border-bottom: 1px solid var(--br); padding-bottom: 18px; margin-bottom: 22px;
}
.logo { font-size: 2.2rem; line-height: 1; }
h1 { font-size: 1.4rem; margin-bottom: 6px; }
.pill-version {
  display: inline-block; padding: 2px 9px; border-radius: 20px;
  font-size: .73rem; font-weight: 700; margin-right: 4px;
  background: rgba(88,166,255,.15); border: 1px solid var(--ac); color: var(--ac);
}
.pill-provider {
  display: inline-block; padding: 2px 9px; border-radius: 20px;
  font-size: .73rem; font-weight: 700; margin-right: 4px;
  background: rgba(188,140,255,.15); border: 1px solid var(--pu); color: var(--pu);
}
.pill-provider-gemini {
  display: inline-block; padding: 2px 9px; border-radius: 20px;
  font-size: .73rem; font-weight: 700; margin-right: 4px;
  background: rgba(66,133,244,.15); border: 1px solid var(--gemini); color: var(--gemini);
}
.pill-provider-groq {
  display: inline-block; padding: 2px 9px; border-radius: 20px;
  font-size: .73rem; font-weight: 700; margin-right: 4px;
  background: rgba(249,115,22,.15); border: 1px solid var(--groq); color: var(--groq);
}
.pill-provider-openrouter {
  display: inline-block; padding: 2px 9px; border-radius: 20px;
  font-size: .73rem; font-weight: 700; margin-right: 4px;
  background: rgba(16,185,129,.15); border: 1px solid var(--openrouter); color: var(--openrouter);
}
.age-pill {
  display: inline-block; padding: 1px 7px; border-radius: 10px;
  font-size: .72rem; font-weight: 600; margin-left: 6px;
}

/* ── Feature badges ── */
.badge {
  display: inline-block; padding: 2px 8px; border-radius: 20px;
  font-size: .76rem; margin: 2px;
}
.badge-green { background: rgba(63,185,80,.15); border: 1px solid var(--gn); color: var(--gn); }
.badge-red   { background: rgba(248,81,73,.1);  border: 1px solid var(--rd); color: var(--rd); }

/* ── KPI stat cards ── */
.stat-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px; margin-bottom: 26px;
}
.stat-card {
  background: var(--sf); border: 1px solid var(--br);
  border-radius: 8px; padding: 16px;
}
.stat-value {
  font-size: 1.8rem; font-weight: 700; color: var(--gn);
}
.stat-value.sparkline {
  font-size: 1.2rem; font-family: monospace;
  letter-spacing: 2px; cursor: default;
}
.stat-value.stat-neutral { color: var(--tx); }
.stat-label { color: var(--mu); font-size: .78rem; margin-top: 2px; }
.stat-sub   { font-size: .75rem; color: var(--mu); margin-top: 4px; }

/* ── Section / panel wrappers ── */
.section { margin-bottom: 26px; }
.panel {
  background: var(--sf); border: 1px solid var(--br);
  border-radius: 8px; padding: 16px;
}

/* ── Earnings projection ── */
.proj {
  margin-top: 12px; padding: 12px;
  background: rgba(63,185,80,.06); border: 1px solid rgba(63,185,80,.2);
  border-radius: 7px;
}
.proj-row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: .85rem; margin-bottom: 6px;
}
.prog-bar {
  height: 6px; background: var(--br);
  border-radius: 3px; overflow: hidden; margin-top: 2px;
}
.prog-fill { height: 100%; border-radius: 3px; transition: width .3s; }

/* ── Earnings breakdown bars ── */
.breakdown { margin-top: 10px; }
.breakdown-row {
  display: flex; align-items: center;
  gap: 8px; margin-bottom: 6px; font-size: .83rem;
}
.breakdown-label  { width: 80px; color: var(--mu); flex-shrink: 0; }
.breakdown-bar-track {
  flex: 1; height: 8px; background: var(--br);
  border-radius: 4px; overflow: hidden;
}
.breakdown-bar    { height: 100%; background: var(--gn); border-radius: 4px; }
.breakdown-amount { width: 70px; text-align: right; color: var(--gn); }

/* -- Research focus -- */
.research-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 10px;
}
.research-card {
  display: flex; gap: 11px; min-height: 150px;
  background: var(--sf); border: 1px solid var(--br);
  border-radius: 8px; padding: 13px;
}
.research-rank {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; flex: 0 0 26px;
  border-radius: 50%; background: rgba(88,166,255,.12);
  border: 1px solid rgba(88,166,255,.35); color: var(--ac);
  font-size: .78rem; font-weight: 800;
}
.research-top {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 8px; margin-bottom: 5px;
}
.research-top span {
  color: var(--yw); font-size: .72rem; font-weight: 700; white-space: nowrap;
}
.research-card p {
  color: var(--mu); font-size: .82rem; line-height: 1.45; margin-bottom: 9px;
}
.research-card code {
  display: inline-block; max-width: 100%;
  background: rgba(110,118,129,.15); border: 1px solid var(--br);
  border-radius: 4px; padding: 3px 6px; color: var(--ac);
  font-size: .74rem; white-space: normal;
}

/* -- AI workflow -- */
.workflow-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}
.workflow-card {
  background: var(--sf); border: 1px solid var(--br);
  border-radius: 8px; padding: 13px; min-height: 126px;
}
.workflow-card.workflow-ready { border-color: rgba(63,185,80,.35); }
.workflow-card.workflow-missing { border-color: rgba(227,179,65,.35); }
.workflow-top {
  display: flex; justify-content: space-between; align-items: center;
  gap: 8px; margin-bottom: 7px;
}
.workflow-top span {
  font-size: .72rem; font-weight: 700; color: var(--mu);
  border: 1px solid var(--br); border-radius: 12px; padding: 1px 7px;
}
.workflow-ready .workflow-top span { color: var(--gn); border-color: rgba(63,185,80,.35); }
.workflow-missing .workflow-top span { color: var(--yw); border-color: rgba(227,179,65,.35); }
.workflow-provider { color: var(--ac); font-size: .9rem; font-weight: 700; margin-bottom: 6px; }
.workflow-model {
  color: var(--tx); font-family: monospace; font-size: .72rem;
  line-height: 1.35; word-break: break-word; margin-bottom: 6px;
}
.workflow-card p { color: var(--mu); font-size: .8rem; line-height: 1.4; }

/* ── Growth suggestions ── */
.suggestion-card {
  display: flex; gap: 12px; padding: 12px;
  border: 1px solid var(--br); border-radius: 7px; margin-bottom: 8px;
}
.suggestion-rank { font-size: 1.4rem; flex-shrink: 0; line-height: 1; }
.suggestion-card p { color: var(--mu); font-size: .86rem; margin-top: 3px; }
.secret-needed {
  background: rgba(88,166,255,.1); border: 1px solid rgba(88,166,255,.3);
  border-radius: 4px; padding: 3px 8px; margin-top: 6px;
  font-size: .8rem; display: inline-block;
}
.est-earnings { color: var(--gn); font-size: .8rem; margin-top: 4px; }
.how-to-steps {
  padding-left: 18px; margin-top: 8px;
  color: var(--mu); font-size: .82rem;
}
.how-to-steps li { margin-bottom: 3px; }
.free-badge {
  display: inline-block; padding: 1px 7px; border-radius: 10px;
  font-size: .72rem; font-weight: 700; color: var(--gn);
  background: rgba(63,185,80,.12); border: 1px solid rgba(63,185,80,.35);
  margin-left: 6px;
}

/* ── Evolution panel ── */
.evo-list { padding-left: 16px; color: var(--mu); font-size: .86rem; }
.evo-list li { margin-bottom: 4px; }
.evo-error-box {
  margin-top: 8px; padding: 6px 10px;
  background: rgba(248,81,73,.08); border: 1px solid rgba(248,81,73,.25);
  border-radius: 5px; font-size: .8rem; color: var(--rd);
}

/* ── Inactive modules ── */
.inactive-tag {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border: 1px solid var(--br);
  border-radius: 6px; margin: 3px; font-size: .8rem;
}
.inactive-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--rd); flex-shrink: 0;
}

/* ── Action table ── */
table { width: 100%; border-collapse: collapse; font-size: .86rem; }
th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--br); }
th { color: var(--mu); font-weight: 500; }

/* ── Top-level error box ── */
.error-box {
  background: rgba(248,81,73,.08); border: 1px solid rgba(248,81,73,.3);
  border-radius: 7px; padding: 12px; margin-top: 14px;
}
.error-box h3 { color: var(--rd); }
.error-box li { color: var(--mu); font-size: .83rem; margin-top: 3px; }

/* ── Utilities ── */
.muted { color: var(--mu); }
.err   { color: var(--rd); font-size: .83rem; }

/* ── Two-column layout ── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 600px) { .two-col { grid-template-columns: 1fr; } }

/* ── Owner Orders panel ── */
.orders-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;
}
@media (max-width: 600px) { .orders-grid { grid-template-columns: 1fr; } }
.order-btn {
  background: var(--sf); border: 1px solid var(--br); color: var(--tx);
  border-radius: 6px; padding: 8px 12px; font-size: .82rem;
  cursor: pointer; text-align: left; transition: border-color .15s, background .15s;
  font-family: var(--f);
}
.order-btn:hover { border-color: var(--ac); background: rgba(88,166,255,.06); }
.order-btn .ob-label { font-weight: 600; color: var(--ac); display: block; margin-bottom: 2px; }
.order-btn .ob-desc  { color: var(--mu); font-size: .77rem; }
.order-custom-row {
  display: flex; gap: 8px; align-items: flex-start; margin-bottom: 12px;
}
.order-input {
  flex: 1; background: var(--bg); border: 1px solid var(--br); color: var(--tx);
  border-radius: 6px; padding: 8px 10px; font-size: .84rem; font-family: var(--f);
  min-height: 38px;
}
.order-input:focus { outline: none; border-color: var(--ac); }
.order-textarea {
  width: 100%; background: var(--bg); border: 1px solid var(--br); color: var(--tx);
  border-radius: 6px; padding: 10px 12px; font-size: .84rem;
  font-family: 'JetBrains Mono', 'Cascadia Code', monospace;
  resize: vertical; min-height: 80px; margin-bottom: 10px;
}
.order-textarea:focus { outline: none; border-color: var(--ac); }
.order-actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.btn {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 6px 14px; border-radius: 6px; font-size: .82rem; font-weight: 600;
  cursor: pointer; border: 1px solid transparent; font-family: var(--f);
  transition: opacity .15s;
}
.btn:hover { opacity: .85; }
.btn-primary   { background: var(--ac); color: var(--bg); border-color: var(--ac); }
.btn-secondary { background: transparent; border-color: var(--br); color: var(--tx); }
.btn-danger    { background: rgba(248,81,73,.15); border-color: var(--rd); color: var(--rd); }
.order-hint {
  font-size: .77rem; color: var(--mu); margin-top: 10px; line-height: 1.5;
  padding: 8px 10px; background: rgba(88,166,255,.05);
  border: 1px solid rgba(88,166,255,.15); border-radius: 5px;
}
.order-hint code {
  background: rgba(110,118,129,.15); padding: 1px 5px; border-radius: 3px;
  font-size: .78em; font-family: monospace;
}
.copy-toast {
  display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
  background: var(--gn); color: var(--bg); padding: 8px 18px; border-radius: 20px;
  font-size: .82rem; font-weight: 700; z-index: 999;
}
.copy-toast.show { display: block; animation: fadeup .3s ease; }
@keyframes fadeup {
  from { opacity: 0; transform: translateX(-50%) translateY(8px); }
  to   { opacity: 1; transform: translateX(-50%) translateY(0); }
}

/* ── Activate Modules panel ── */
.activate-card {
  border: 1px solid var(--br); border-radius: 7px;
  padding: 12px 14px; margin-bottom: 10px;
}
.activate-card:last-child { margin-bottom: 0; }
.activate-header {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px;
}
.activate-link {
  margin-left: auto; font-size: .78rem; color: var(--ac);
  white-space: nowrap;
}
.activate-secrets { margin-bottom: 6px; }
.secret-code {
  display: inline-block; background: rgba(110,118,129,.15);
  border: 1px solid var(--br); border-radius: 4px;
  padding: 1px 6px; font-size: .75rem; font-family: monospace;
  margin-right: 4px; margin-bottom: 2px; color: var(--ac);
}
.activate-steps {
  padding-left: 18px; color: var(--mu); font-size: .82rem; margin-bottom: 4px;
}
.activate-steps li { margin-bottom: 3px; }
.activate-note {
  font-size: .78rem; color: var(--mu); margin-top: 5px;
  padding: 4px 8px; background: rgba(88,166,255,.05);
  border-left: 2px solid rgba(88,166,255,.3); border-radius: 2px;
}
.paid-badge {
  display: inline-block; padding: 1px 7px; border-radius: 10px;
  font-size: .72rem; font-weight: 700; color: var(--yw);
  background: rgba(227,179,65,.12); border: 1px solid rgba(227,179,65,.35);
  margin-left: 6px;
}

/* -- Secret readiness -- */
.secret-intro { font-size: .8rem; margin-bottom: 10px; }
.secret-row {
  display: grid; grid-template-columns: 160px 1fr minmax(120px, 260px);
  gap: 10px; align-items: center; padding: 8px 0;
  border-bottom: 1px solid rgba(48,54,61,.75);
}
.secret-row:last-child { border-bottom: 0; }
.secret-row div:first-child {
  display: flex; align-items: baseline; justify-content: space-between; gap: 8px;
}
.secret-row strong { font-size: .82rem; }
.secret-row span { color: var(--mu); font-size: .76rem; }
.secret-meter {
  height: 7px; background: var(--br); border-radius: 4px; overflow: hidden;
}
.secret-meter div { height: 100%; background: var(--gn); border-radius: 4px; }
.secret-row code {
  color: var(--yw); background: rgba(110,118,129,.12);
  border: 1px solid var(--br); border-radius: 4px;
  padding: 2px 6px; font-size: .72rem; white-space: normal;
}
@media (max-width: 700px) {
  .secret-row { grid-template-columns: 1fr; gap: 6px; }
}

/* ── Footer ── */
footer {
  text-align: center; color: var(--mu); font-size: .76rem;
  margin-top: 32px; padding-top: 14px; border-top: 1px solid var(--br);
}
.wallet-row { display: inline-flex; align-items: center; gap: 6px; margin-top: 6px; }
.wallet-row code {
  font-family: monospace; font-size: .75rem;
  background: rgba(110,118,129,.15); padding: 1px 6px; border-radius: 3px;
  word-break: break-all;
}
.btn-copy-addr {
  background: transparent; border: 1px solid var(--br); color: var(--mu);
  border-radius: 4px; padding: 1px 5px; font-size: .72rem;
  cursor: pointer; line-height: 1.4;
}
.btn-copy-addr:hover { border-color: var(--ac); color: var(--ac); }

/* ── Live indicator ── */
.live-indicator {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: .74rem; color: var(--mu);
}
#live-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--br); transition: background .4s;
  flex-shrink: 0;
}
"""


# ── Main renderer ──────────────────────────────────────────────────────────────

def _render(s: dict[str, Any]) -> str:
    version   = s.get("version", "1.0.0")
    provider  = s.get("llm_provider", "unknown")
    llm_roles = s.get("llm_roles", {})
    active    = s.get("active_features", [])
    inactive  = s.get("inactive_features", [])
    earn      = s.get("earnings", {})
    suggs     = s.get("suggestions", [])
    evo       = s.get("last_evolution", {})
    actions   = s.get("last_earning", {}).get("actions", [])
    errors    = s.get("errors", [])
    n_runs    = s.get("total_runs", 0)

    last_run            = _fmt(s.get("last_run"))
    age_label, age_color = _last_run_age(s.get("last_run"))
    cycle_secs          = s.get("last_cycle_seconds")
    cycle_str           = f"{cycle_secs}s" if cycle_secs else "—"

    history  = [v for v in earn.get("history", []) if v > 0]
    spark    = _sparkline(history)
    spark_tip = " · ".join(f"${v:.4f}" for v in history) if history else "no data"

    body = "\n".join([
        _section_header(version, provider, active, last_run,
                        age_label, age_color, n_runs, cycle_str, llm_roles),
        _section_stats(earn, n_runs, active, inactive, history, spark, spark_tip, s),
        _section_earnings(earn),
        _section_llm_workflows(s),
        _section_secret_readiness(s),
        _section_research_focus(s),
        _section_suggestions(suggs, s),
        _section_inactive(inactive, s),
        _section_orders(),
        _section_evolution(evo),
        _section_actions(actions),
        _section_errors(errors),
        _ORDERS_JS,
        _LIVE_JS,
    ])

    wallet      = s.get("usdt_wallet", "")
    wallet_html = (
        f'<br><span class="wallet-row">💰 USDT (TRC-20/ERC-20): '
        f'<code id="usdt-addr">{wallet}</code>'
        f'<button class="btn-copy-addr" onclick="navigator.clipboard.writeText(\'{wallet}\')"'
        f' title="Copy address">⧉</button></span>'
    ) if wallet else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>E-Evolve Dashboard</title>
<style>
{_CSS}
</style>
</head>
<body>
{body}
<footer>
  E-Evolve · hourly via GitHub Actions ·
  <a href="status.json">status.json</a> · <a href="earnings-log.md">earnings log</a>
  &nbsp;·&nbsp;
  <span class="live-indicator">
    <span id="live-dot"></span>
    live · updated <span id="live-ts">—</span>
  </span>
  {wallet_html}
</footer>
</body>
</html>"""


# Modern GitHub Pages dashboard app. This definition intentionally appears after
# the legacy renderer so future calls use the structured static-app shell below.
def _render(s: dict[str, Any]) -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>E-Evolve Dashboard</title>
  <link rel="stylesheet" href="assets/dashboard.css">
  <script type="importmap">
    {"imports":{"vue":"https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js"}}
  </script>
</head>
<body>
  <div id="app" v-cloak>
    <div class="loading">Loading dashboard...</div>
  </div>
  <noscript>This dashboard needs JavaScript enabled.</noscript>
  <script type="module" src="assets/dashboard.js"></script>
</body>
</html>
"""


_APP_CSS = """\
:root {
  --bg: #0b0f14;
  --panel: #121923;
  --panel-2: #17202c;
  --line: #263343;
  --line-soft: #1d2937;
  --text: #e5edf7;
  --muted: #93a4b8;
  --soft: #c4d1df;
  --blue: #6aa6ff;
  --green: #49d17c;
  --red: #ff6b6b;
  --yellow: #f6c85f;
  --cyan: #58d7d3;
  --pink: #e49bff;
  --shadow: 0 18px 60px rgba(0, 0, 0, .34);
  --font: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  min-width: 320px;
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
}

button,
input,
textarea {
  font: inherit;
}

button {
  cursor: pointer;
}

a {
  color: var(--blue);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

[v-cloak] {
  display: none;
}

.loading,
noscript {
  display: grid;
  min-height: 100vh;
  place-items: center;
  color: var(--muted);
}

.app-shell {
  min-height: 100vh;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 5;
  border-bottom: 1px solid rgba(38, 51, 67, .9);
  background: rgba(11, 15, 20, .88);
  backdrop-filter: blur(14px);
}

.topbar-inner,
.page {
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
}

.topbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 68px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.brand-mark {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  color: var(--cyan);
  font-weight: 800;
}

.brand h1 {
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.15;
}

.brand p {
  margin: 3px 0 0;
  color: var(--muted);
  font-size: .82rem;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.live-chip,
.chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 30px;
  padding: 5px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--panel);
  color: var(--soft);
  font-size: .78rem;
  white-space: nowrap;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 99px;
  background: var(--green);
  box-shadow: 0 0 0 4px rgba(73, 209, 124, .12);
}

.live-dot.error {
  background: var(--red);
  box-shadow: 0 0 0 4px rgba(255, 107, 107, .14);
}

.page {
  padding: 26px 0 34px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(280px, .7fr);
  gap: 18px;
  align-items: stretch;
  margin-bottom: 18px;
}

.hero-main,
.panel,
.metric-card,
.card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  box-shadow: var(--shadow);
}

.hero-main {
  padding: 24px;
}

.eyebrow {
  margin: 0 0 9px;
  color: var(--cyan);
  font-size: .76rem;
  font-weight: 800;
  text-transform: uppercase;
}

.hero h2 {
  max-width: 720px;
  margin: 0;
  font-size: clamp(2rem, 4vw, 4.3rem);
  line-height: .98;
}

.hero-copy {
  max-width: 680px;
  margin: 14px 0 0;
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.6;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 22px;
}

.summary-panel {
  padding: 18px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 13px 0;
  border-bottom: 1px solid var(--line-soft);
}

.summary-row:last-child {
  border-bottom: 0;
}

.summary-row span {
  color: var(--muted);
  font-size: .82rem;
}

.summary-row strong {
  color: var(--text);
  text-align: right;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.cockpit {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, .85fr);
  gap: 18px;
  align-items: start;
  margin-bottom: 18px;
}

.metric-card {
  padding: 17px;
  min-height: 118px;
}

.metric-label {
  color: var(--muted);
  font-size: .78rem;
}

.metric-value {
  margin-top: 10px;
  color: var(--text);
  font-size: 2rem;
  font-weight: 800;
}

.metric-value.good {
  color: var(--green);
}

.metric-value.warn {
  color: var(--yellow);
}

.metric-note {
  margin-top: 7px;
  color: var(--muted);
  font-size: .76rem;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 18px;
  align-items: start;
}

.stack {
  display: grid;
  gap: 18px;
}

.panel {
  overflow: hidden;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 56px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--line-soft);
}

.panel-head h3 {
  margin: 0;
  font-size: .95rem;
}

.panel-head p {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: .78rem;
}

.panel-body {
  padding: 18px;
}

.grid-2,
.grid-3 {
  display: grid;
  gap: 12px;
}

.grid-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.card {
  min-height: 126px;
  padding: 15px;
  box-shadow: none;
}

.card-top,
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.card h4 {
  margin: 0;
  font-size: .9rem;
}

.card p,
.muted {
  color: var(--muted);
}

.card p {
  margin: 10px 0 0;
  font-size: .82rem;
  line-height: 1.45;
}

.tag {
  display: inline-flex;
  align-items: center;
  min-height: 25px;
  padding: 3px 9px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--panel-2);
  color: var(--soft);
  font-size: .75rem;
  font-weight: 700;
}

.tag.good {
  border-color: rgba(73, 209, 124, .35);
  color: var(--green);
}

.tag.warn {
  border-color: rgba(246, 200, 95, .35);
  color: var(--yellow);
}

.tag.bad {
  border-color: rgba(255, 107, 107, .35);
  color: var(--red);
}

.tag.info {
  border-color: rgba(106, 166, 255, .35);
  color: var(--blue);
}

.bar {
  height: 8px;
  overflow: hidden;
  border-radius: 99px;
  background: #0d141d;
}

.bar-fill {
  height: 100%;
  border-radius: inherit;
  background: var(--green);
}

.secret-list,
.action-list,
.evo-list,
.focus-list {
  display: grid;
  gap: 10px;
}

.pipeline,
.opportunity-list {
  display: grid;
  gap: 10px;
}

.pipeline-stage,
.opportunity-item {
  display: grid;
  align-items: center;
  gap: 12px;
  min-height: 72px;
  padding: 12px;
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  background: rgba(23, 32, 44, .56);
}

.pipeline-stage {
  grid-template-columns: auto minmax(0, 1fr) auto;
}

.pipeline-stage.ready {
  border-color: rgba(73, 209, 124, .28);
}

.pipeline-stage p,
.opportunity-item p {
  margin: 4px 0 0;
  font-size: .78rem;
  line-height: 1.45;
}

.stage-dot {
  width: 12px;
  height: 12px;
  border-radius: 99px;
  background: var(--yellow);
  box-shadow: 0 0 0 4px rgba(246, 200, 95, .12);
}

.stage-dot.good {
  background: var(--green);
  box-shadow: 0 0 0 4px rgba(73, 209, 124, .12);
}

.stage-dot.bad {
  background: var(--red);
  box-shadow: 0 0 0 4px rgba(255, 107, 107, .14);
}

.opportunity-item {
  grid-template-columns: 58px minmax(0, 1fr);
}

.opportunity-score {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border: 1px solid rgba(106, 166, 255, .36);
  border-radius: 8px;
  background: rgba(106, 166, 255, .08);
  color: var(--blue);
}

.opportunity-score strong {
  line-height: 1;
}

.opportunity-score span {
  color: var(--muted);
  font-size: .62rem;
}

.secret-item,
.action-item,
.evo-item,
.focus-item {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  background: rgba(23, 32, 44, .56);
}

.secret-item {
  grid-template-columns: 150px minmax(0, 1fr) 130px;
  align-items: center;
}

.secret-item code,
.command-area,
.cmd-input,
.code-pill {
  font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
}

.secret-item code,
.code-pill {
  overflow-wrap: anywhere;
  color: var(--yellow);
  font-size: .75rem;
}

.focus-rank {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border: 1px solid rgba(106, 166, 255, .4);
  border-radius: 999px;
  color: var(--blue);
  font-size: .78rem;
  font-weight: 800;
}

.focus-item {
  grid-template-columns: auto minmax(0, 1fr);
}

.active-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.active-module {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  background: rgba(23, 32, 44, .56);
}

.active-module p {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: .76rem;
}

.module-dot {
  width: 11px;
  height: 11px;
  border-radius: 99px;
  background: var(--green);
  box-shadow: 0 0 0 4px rgba(73, 209, 124, .12);
}

.module-dot.model {
  background: var(--blue);
  box-shadow: 0 0 0 4px rgba(106, 166, 255, .12);
}

.quota-card {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid rgba(106, 166, 255, .22);
  border-radius: 8px;
  background: rgba(106, 166, 255, .07);
}

.quota-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 9px;
}

.quota-top span {
  color: var(--green);
  font-weight: 800;
}

.quota-card p {
  margin: 9px 0 0;
  font-size: .78rem;
}

.dispatch-card {
  display: grid;
  gap: 10px;
  margin-bottom: 14px;
  padding: 12px;
  border: 1px solid rgba(88, 215, 211, .28);
  border-radius: 8px;
  background: rgba(88, 215, 211, .06);
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.field-label {
  display: grid;
  gap: 5px;
  color: var(--muted);
  font-size: .72rem;
  font-weight: 800;
}

.status-line {
  min-height: 18px;
  color: var(--muted);
  font-size: .75rem;
  line-height: 1.45;
}

.status-line.good {
  color: var(--green);
}

.status-line.bad {
  color: var(--red);
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.segmented {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 6px;
  margin-bottom: 10px;
  padding: 4px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #0d141d;
}

.segment-btn {
  min-height: 31px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: var(--muted);
  font-size: .75rem;
  font-weight: 800;
}

.segment-btn.active {
  border-color: rgba(106, 166, 255, .44);
  background: rgba(106, 166, 255, .12);
  color: var(--blue);
}

.preset-btn,
.small-btn,
.icon-btn {
  border: 1px solid var(--line);
  border-radius: 7px;
  background: var(--panel-2);
  color: var(--text);
}

.preset-btn {
  min-height: 64px;
  padding: 10px;
  text-align: left;
}

.preset-btn strong {
  display: block;
  font-size: .8rem;
}

.preset-btn span {
  display: block;
  margin-top: 4px;
  color: var(--muted);
  font-size: .72rem;
}

.preset-btn:hover,
.small-btn:hover,
.icon-btn:hover {
  border-color: var(--blue);
}

.cmd-row {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.cmd-input {
  width: 100%;
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: #0d141d;
  color: var(--text);
  padding: 9px 10px;
}

.command-area {
  width: 100%;
  min-height: 96px;
  margin-top: 12px;
  resize: vertical;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: #0d141d;
  color: var(--text);
  padding: 11px;
}

.button-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.small-btn {
  min-height: 35px;
  padding: 7px 11px;
  color: var(--soft);
}

.small-btn.primary {
  border-color: rgba(106, 166, 255, .5);
  color: var(--blue);
}

.small-btn.danger {
  border-color: rgba(255, 107, 107, .4);
  color: var(--red);
}

.small-btn:disabled {
  cursor: not-allowed;
  opacity: .55;
}

.empty {
  padding: 18px;
  color: var(--muted);
  text-align: center;
}

.footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
  color: var(--muted);
  font-size: .78rem;
}

@media (max-width: 980px) {
  .hero,
  .layout,
  .cockpit {
    grid-template-columns: 1fr;
  }

  .metrics,
  .grid-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .topbar-inner,
  .page {
    width: min(100% - 20px, 1200px);
  }

  .topbar-inner {
    align-items: flex-start;
    flex-direction: column;
    padding: 12px 0;
  }

  .top-actions,
  .hero-meta,
  .button-row {
    width: 100%;
  }

  .metrics,
  .grid-2,
  .grid-3,
  .field-grid,
  .active-grid,
  .preset-grid,
  .segmented,
  .secret-item {
    grid-template-columns: 1fr;
  }

  .hero-main,
  .summary-panel,
  .panel-body {
    padding: 14px;
  }

  .hero h2 {
    font-size: 2rem;
  }
}
"""


_APP_JS = """\
import { createApp } from 'vue';

const POLL_MS = 60000;
const WORKFLOW_FILE = 'evolve.yml';
const DEFAULT_REF = 'main';
const STORAGE_KEYS = {
  repo: 'e-evolve.githubRepo',
  token: 'e-evolve.githubToken',
  ref: 'e-evolve.workflowRef',
};

const ORDER_PRESETS = [
  ['force articles 2', 'Fill today\\'s article quota'],
  ['force articles 1', 'Publish one buyer-intent article'],
  ['post thread', 'Distribute the latest article'],
  ['status report', 'Audit setup and failures'],
  ['skip evolution', 'Protect earning cycle once'],
  ['force trade conservative', 'Only when Binance is funded'],
  ['force mint 1', 'Only when wallet is funded'],
  ['reset earnings', 'Start a fresh weekly view'],
];

const REVENUE_STAGES = [
  { key: 'model', label: 'Model', detail: 'Generate articles and upgrades', features: ['llm_groq', 'llm_gemini', 'llm_openrouter', 'llm_anthropic'] },
  { key: 'publish', label: 'Publish', detail: 'Ship buyer-intent content', features: ['articles_devto', 'articles_medium'] },
  { key: 'convert', label: 'Convert', detail: 'Send readers to a CTA or wallet', features: ['usdt_wallet'] },
  { key: 'distribute', label: 'Distribute', detail: 'Turn posts into repeat reach', features: ['twitter'] },
  { key: 'payout', label: 'Payout', detail: 'Move funds when thresholds hit', features: ['crypto_payout'] },
];

const SECRET_IMPACT = {
  MEDIUM_INTEGRATION_TOKEN: 94,
  EARN_CTA_URL: 90,
  USDT_WALLET_ADDRESS: 86,
  TWITTER_API_KEY: 72,
  TWITTER_API_SECRET: 72,
  TWITTER_ACCESS_TOKEN: 72,
  TWITTER_ACCESS_SECRET: 72,
  OPENROUTER_API_KEY: 64,
  GEMINI_API_KEY: 62,
  ANTHROPIC_API_KEY: 56,
  BINANCE_WITHDRAW_ADDRESS: 48,
  BINANCE_API_KEY: 42,
  BINANCE_SECRET_KEY: 42,
  ETH_PRIVATE_KEY: 24,
  ETH_WALLET_ADDRESS: 24,
};

const MODULE_LABELS = {
  llm_anthropic: 'Anthropic',
  llm_gemini: 'Gemini',
  llm_openrouter: 'OpenRouter',
  llm_groq: 'Groq',
  articles_devto: 'dev.to articles',
  articles_medium: 'Medium articles',
  usdt_wallet: 'USDT wallet',
  twitter: 'Twitter / X',
  crypto_binance: 'Crypto trading',
  crypto_payout: 'Payout automation',
  nft_ethereum: 'NFT minting',
};

function money(value, digits = 2) {
  const n = Number(value || 0);
  return '$' + n.toFixed(digits);
}

function fmtDate(iso) {
  if (!iso) return 'never';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return String(iso);
  return d.toISOString().slice(0, 16).replace('T', ' ') + ' UTC';
}

function ageLabel(iso) {
  if (!iso) return 'never';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return 'unknown';
  const secs = Math.max(0, Math.floor((Date.now() - d.getTime()) / 1000));
  if (secs < 90) return 'just now';
  if (secs < 3600) return Math.floor(secs / 60) + 'm ago';
  if (secs < 86400) return Math.floor(secs / 3600) + 'h ago';
  return Math.floor(secs / 86400) + 'd ago';
}

function compactNumber(value) {
  return new Intl.NumberFormat('en', { notation: 'compact' }).format(Number(value || 0));
}

function pct(done, total) {
  if (!total) return 0;
  return Math.max(0, Math.min(100, Math.round(Number(done || 0) / Number(total) * 100)));
}

function providerClass(provider) {
  if (provider === 'gemini') return 'info';
  if (provider === 'groq') return 'warn';
  if (provider === 'openrouter') return 'good';
  return 'info';
}

function cycleState(lastRun) {
  if (!lastRun) return { label: 'never run', cls: 'bad' };
  const d = new Date(lastRun);
  if (Number.isNaN(d.getTime())) return { label: 'unknown', cls: 'warn' };
  const mins = Math.floor((Date.now() - d.getTime()) / 60000);
  if (mins <= 75) return { label: 'healthy', cls: 'good' };
  if (mins <= 180) return { label: 'late', cls: 'warn' };
  return { label: 'stalled', cls: 'bad' };
}

function inferGitHubRepo() {
  const host = window.location.hostname;
  if (!host.endsWith('.github.io')) return '';
  const owner = host.slice(0, -'.github.io'.length);
  const repo = window.location.pathname.split('/').filter(Boolean)[0];
  return owner && repo ? owner + '/' + repo : '';
}

createApp({
  data() {
    return {
      status: {},
      loaded: false,
      online: true,
      lastPoll: null,
      ORDER_PRESETS,
      commands: [],
      customCommand: '',
      copyLabel: 'Copy',
      activeCommandGroup: 'earn',
      githubRepo: localStorage.getItem(STORAGE_KEYS.repo) || inferGitHubRepo(),
      githubToken: localStorage.getItem(STORAGE_KEYS.token) || '',
      workflowRef: localStorage.getItem(STORAGE_KEYS.ref) || DEFAULT_REF,
      dispatchState: 'idle',
      dispatchMessage: '',
    };
  },

  computed: {
    earn() {
      return this.status.earnings || {};
    },
    active() {
      return this.status.active_features || [];
    },
    inactive() {
      return this.status.inactive_features || [];
    },
    cycleHealth() {
      return cycleState(this.status.last_run);
    },
    workflows() {
      return Object.entries(this.status.llm_workflows || {}).map(([name, item]) => ({
        name,
        ...item,
      }));
    },
    secrets() {
      return Object.entries(this.status.secret_readiness || {}).map(([name, item]) => ({
        name,
        label: MODULE_LABELS[name] || name,
        percent: pct(item.present_count, item.required_count),
        ...item,
      }));
    },
    focusItems() {
      const missing = new Set(this.secrets.flatMap((item) => item.missing || []));
      const active = new Set(this.active);
      const cards = [];

      if (active.has('articles_devto') && missing.has('MEDIUM_INTEGRATION_TOKEN')) {
        cards.push(['Dual-publish articles', 'Add Medium to reuse every dev.to article with no extra model call.', 'MEDIUM_INTEGRATION_TOKEN']);
      }
      if (active.has('articles_devto') && !this.status.usdt_wallet) {
        cards.push(['Add a conversion target', 'Set a wallet, sponsor, tip, newsletter, or product CTA for every article.', 'USDT_WALLET_ADDRESS or EARN_CTA_URL']);
      }
      if (missing.has('TWITTER_API_KEY')) {
        cards.push(['Turn articles into distribution', 'Activate the social module only when your X developer access is ready.', 'TWITTER_API_KEY']);
      }
      if (missing.has('BINANCE_WITHDRAW_ADDRESS') && active.has('usdt_wallet')) {
        cards.push(['Finish payout automation', 'The wallet is known; add exchange withdrawal settings when you are ready.', 'BINANCE_WITHDRAW_ADDRESS']);
      }
      if (!cards.length) {
        cards.push(['Keep the loop healthy', 'All obvious setup gaps are covered. Watch cycle age, errors, and article output.', 'status report']);
      }
      if (active.has('articles_devto')) {
        cards.unshift(['Protect article quality', 'The normal schedule is capped at two generated articles per UTC day, with separate topic seeds for each post.', 'articles.daily_limit = 2']);
      }

      return cards.map((card, index) => ({ rank: index + 1, title: card[0], body: card[1], action: card[2] }));
    },
    opportunityItems() {
      const missingSecrets = new Set(this.secrets.flatMap((item) => item.missing || []));
      if (this.active.includes('articles_devto') && !this.status.usdt_wallet) missingSecrets.add('EARN_CTA_URL');
      const rows = Array.from(missingSecrets).map((name) => ({
        name,
        impact: SECRET_IMPACT[name] || 35,
        note: this.opportunityNote(name),
      }));
      return rows.sort((a, b) => b.impact - a.impact).slice(0, 5);
    },
    revenueStages() {
      const active = new Set(this.active);
      return REVENUE_STAGES.map((stage) => {
        const readyCount = stage.features.filter((feature) => active.has(feature)).length;
        const ready = readyCount > 0;
        return {
          ...stage,
          ready,
          readyCount,
          total: stage.features.length,
          cls: ready ? 'good' : 'warn',
        };
      });
    },
    commandGroups() {
      return {
        earn: this.ORDER_PRESETS.slice(0, 3),
        protect: this.ORDER_PRESETS.slice(3, 5),
        funded: this.ORDER_PRESETS.slice(5, 7),
        admin: this.ORDER_PRESETS.slice(7),
      };
    },
    activePresets() {
      return this.commandGroups[this.activeCommandGroup] || this.commandGroups.earn;
    },
    suggestions() {
      return this.status.suggestions || [];
    },
    actions() {
      return (this.status.last_earning && this.status.last_earning.actions) || [];
    },
    articleDaily() {
      const daily = this.status.article_daily || {};
      return {
        date: daily.date || 'not started',
        published: Number(daily.published || 0),
        limit: 2,
      };
    },
    articleProgress() {
      return pct(this.articleDaily.published, this.articleDaily.limit);
    },
    activeModules() {
      const freeNames = new Set(['llm_groq', 'llm_gemini', 'llm_openrouter', 'articles_devto', 'articles_medium', 'usdt_wallet']);
      return this.secrets
        .filter((item) => item.active)
        .map((item) => ({
          name: item.name,
          label: item.label,
          free: freeNames.has(item.name),
          role: item.name.startsWith('llm_') ? 'model' : 'earning',
        }));
    },
    evolution() {
      return this.status.last_evolution || {};
    },
    breakdown() {
      const entries = Object.entries(this.earn.breakdown || {});
      const max = Math.max(...entries.map(([, value]) => Number(value || 0)), 1);
      return entries.map(([name, value]) => ({
        name,
        value: Number(value || 0),
        percent: Math.round(Number(value || 0) / max * 100),
      }));
    },
    commandText: {
      get() {
        return this.commands.length ? this.commands.join('\\n') : '# no commands';
      },
      set(value) {
        this.commands = value.split('\\n').map((line) => line.trim()).filter(Boolean).filter((line) => line !== '# no commands');
      },
    },
    weeklyProjection() {
      const history = (this.earn.history || []).map(Number).filter((n) => n > 0);
      if (!history.length) return money(0);
      const avg = history.reduce((sum, n) => sum + n, 0) / history.length;
      return money(avg * 168);
    },
    baselineProjection() {
      const perPublish = 0.02;
      const dailyLimit = Math.max(1, Number(this.articleDaily.limit || 2));
      return money(perPublish * dailyLimit * 7);
    },
    nextBestAction() {
      if (this.opportunityItems.length) {
        return 'Add ' + this.opportunityItems[0].name;
      }
      if (this.articleDaily.published < this.articleDaily.limit) {
        return 'Run force articles 1';
      }
      return 'Watch next cycle';
    },
    weekGoalPercent() {
      return pct(this.earn.this_week_usd || 0, 10);
    },
    canDispatchWorkflow() {
      return Boolean(this.githubRepo.trim() && this.githubToken.trim() && this.workflowRef.trim() && this.dispatchState !== 'running');
    },
    dispatchStatusClass() {
      if (this.dispatchState === 'success') return 'good';
      if (this.dispatchState === 'error') return 'bad';
      return '';
    },
  },

  methods: {
    money,
    fmtDate,
    ageLabel,
    compactNumber,
    providerClass,
    moduleLabel(name) {
      return MODULE_LABELS[name] || name;
    },
    opportunityNote(name) {
      const notes = {
        MEDIUM_INTEGRATION_TOKEN: 'Doubles article reach without another generation.',
        EARN_CTA_URL: 'Gives each article a conversion path.',
        USDT_WALLET_ADDRESS: 'Lets the dashboard show a payment destination.',
        TWITTER_API_KEY: 'Starts distribution beyond publishing platforms.',
        TWITTER_API_SECRET: 'Required with the X posting keys.',
        TWITTER_ACCESS_TOKEN: 'Required with the X posting keys.',
        TWITTER_ACCESS_SECRET: 'Required with the X posting keys.',
        OPENROUTER_API_KEY: 'Adds cheap research and second opinions.',
        GEMINI_API_KEY: 'Unblocks stronger upgrade planning.',
        ANTHROPIC_API_KEY: 'Adds a premium evolution fallback.',
        BINANCE_WITHDRAW_ADDRESS: 'Completes automated payout routing.',
        BINANCE_API_KEY: 'Only useful when funded trading or payouts are intended.',
        BINANCE_SECRET_KEY: 'Only useful when funded trading or payouts are intended.',
      };
      return notes[name] || 'Optional module setup.';
    },
    addCommand(cmd) {
      if (!this.commands.includes(cmd)) this.commands.push(cmd);
    },
    addCustomCommand() {
      const cmd = this.customCommand.trim();
      if (cmd) this.addCommand(cmd);
      this.customCommand = '';
    },
    clearCommands() {
      this.commands = [];
    },
    rememberWorkflowSettings() {
      const repo = this.githubRepo.trim();
      const ref = this.workflowRef.trim() || DEFAULT_REF;
      if (repo) localStorage.setItem(STORAGE_KEYS.repo, repo);
      if (this.githubToken.trim()) localStorage.setItem(STORAGE_KEYS.token, this.githubToken.trim());
      localStorage.setItem(STORAGE_KEYS.ref, ref);
    },
    async runWorkflow() {
      const repo = this.githubRepo.trim();
      const token = this.githubToken.trim();
      const ref = this.workflowRef.trim() || DEFAULT_REF;
      if (!repo || !token) {
        this.dispatchState = 'error';
        this.dispatchMessage = 'Add a repo and a GitHub token with Actions write access.';
        return;
      }
      this.rememberWorkflowSettings();
      this.dispatchState = 'running';
      this.dispatchMessage = 'Ordering GitHub Actions to run evolve...';
      try {
        const response = await fetch(`https://api.github.com/repos/${repo}/actions/workflows/${WORKFLOW_FILE}/dispatches`, {
          method: 'POST',
          headers: {
            Accept: 'application/vnd.github+json',
            Authorization: `Bearer ${token}`,
            'X-GitHub-Api-Version': '2022-11-28',
          },
          body: JSON.stringify({ ref }),
        });
        if (response.status !== 204) {
          let detail = '';
          try {
            const payload = await response.json();
            detail = payload.message ? ': ' + payload.message : '';
          } catch (err) {
            detail = response.statusText ? ': ' + response.statusText : '';
          }
          throw new Error(`GitHub returned ${response.status}${detail}`);
        }
        this.dispatchState = 'success';
        this.dispatchMessage = `evolve workflow queued on ${ref}.`;
      } catch (err) {
        this.dispatchState = 'error';
        this.dispatchMessage = err.message || 'Workflow dispatch failed.';
      }
    },
    async copyCommands() {
      try {
        await navigator.clipboard.writeText(this.commandText);
        this.copyLabel = 'Copied';
      } catch (err) {
        this.copyLabel = 'Select text';
      }
      setTimeout(() => { this.copyLabel = 'Copy'; }, 1600);
    },
    downloadCommands() {
      const blob = new Blob([this.commandText], { type: 'text/plain' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'command.txt';
      a.click();
      URL.revokeObjectURL(a.href);
    },
    async loadStatus() {
      try {
        const response = await fetch('status.json?ts=' + Date.now(), { cache: 'no-store' });
        if (!response.ok) throw new Error('status fetch failed');
        this.status = await response.json();
        this.loaded = true;
        this.online = true;
        this.lastPoll = new Date().toISOString();
      } catch (err) {
        this.online = false;
        this.loaded = true;
      }
    },
  },

  mounted() {
    this.loadStatus();
    setInterval(this.loadStatus, POLL_MS);
  },

  template: `
    <div class="app-shell">
      <header class="topbar">
        <div class="topbar-inner">
          <div class="brand">
            <div class="brand-mark">EE</div>
            <div>
              <h1>E-Evolve</h1>
              <p>Self-improving earning bot dashboard</p>
            </div>
          </div>
          <div class="top-actions">
            <span class="live-chip"><span class="live-dot" :class="{ error: !online }"></span>{{ online ? 'live' : 'offline' }}</span>
            <a class="chip" href="status.json">status.json</a>
            <a class="chip" href="earnings-log.md">earnings log</a>
          </div>
        </div>
      </header>

      <main class="page" v-if="loaded">
        <section class="hero">
          <div class="hero-main">
            <p class="eyebrow">GitHub Actions automation</p>
            <h2>{{ money(earn.total_usd) }} earned, next move: {{ nextBestAction }}</h2>
            <p class="hero-copy">
              Current version {{ status.version || 'unknown' }} runs with {{ active.length }} active modules.
              Last cycle finished {{ ageLabel(status.last_run) }} in {{ status.last_cycle_seconds || 0 }} seconds.
            </p>
            <div class="hero-meta">
              <span v-for="feature in active" :key="feature" class="tag good">{{ moduleLabel(feature) }}</span>
              <span v-if="!active.length" class="tag bad">No active modules</span>
            </div>
          </div>
          <aside class="summary-panel">
            <div class="summary-row"><span>Last run</span><strong>{{ fmtDate(status.last_run) }}</strong></div>
            <div class="summary-row"><span>Provider</span><strong>{{ status.llm_provider || 'unknown' }}</strong></div>
            <div class="summary-row"><span>Cycle health</span><strong><span class="tag" :class="cycleHealth.cls">{{ cycleHealth.label }}</span></strong></div>
            <div class="summary-row"><span>Article quota</span><strong>{{ articleDaily.published }}/{{ articleDaily.limit }} today</strong></div>
            <div class="summary-row"><span>This week</span><strong>{{ money(earn.this_week_usd) }}</strong></div>
            <div class="summary-row"><span>Projection</span><strong>{{ weeklyProjection }}/week</strong></div>
          </aside>
        </section>

        <section class="metrics">
          <article class="metric-card"><div class="metric-label">Total earned</div><div class="metric-value good">{{ money(earn.total_usd) }}</div><div class="metric-note">Lifetime estimate</div></article>
          <article class="metric-card"><div class="metric-label">This week</div><div class="metric-value warn">{{ money(earn.this_week_usd) }}</div><div class="metric-note">Goal progress {{ weekGoalPercent }}%</div></article>
          <article class="metric-card"><div class="metric-label">Cycles</div><div class="metric-value">{{ compactNumber(status.total_runs) }}</div><div class="metric-note">Hourly runner history</div></article>
          <article class="metric-card"><div class="metric-label">Modules</div><div class="metric-value">{{ active.length }}/{{ active.length + inactive.length }}</div><div class="metric-note">{{ inactive.length }} waiting for setup</div></article>
        </section>

        <section class="cockpit">
          <section class="panel">
            <div class="panel-head"><div><h3>Revenue Pipeline</h3><p>Where the loop is ready, and where money can leak.</p></div><span class="tag" :class="cycleHealth.cls">{{ cycleHealth.label }}</span></div>
            <div class="panel-body pipeline">
              <article v-for="stage in revenueStages" :key="stage.key" class="pipeline-stage" :class="{ ready: stage.ready }">
                <span class="stage-dot" :class="stage.cls"></span>
                <div>
                  <strong>{{ stage.label }}</strong>
                  <p>{{ stage.detail }}</p>
                </div>
                <span class="tag" :class="stage.cls">{{ stage.readyCount }}/{{ stage.total }}</span>
              </article>
            </div>
          </section>

          <section class="panel">
            <div class="panel-head"><div><h3>Highest-Leverage Setup</h3><p>Ranked by likely earning impact for this bot.</p></div><span class="tag info">{{ baselineProjection }}/wk base</span></div>
            <div class="panel-body opportunity-list">
              <article v-for="item in opportunityItems" :key="item.name" class="opportunity-item">
                <div class="opportunity-score"><strong>{{ item.impact }}</strong><span>impact</span></div>
                <div>
                  <strong>{{ item.name }}</strong>
                  <p class="muted">{{ item.note }}</p>
                </div>
              </article>
              <p v-if="!opportunityItems.length" class="empty">No obvious setup gaps. Keep publishing and watch conversion data.</p>
            </div>
          </section>
        </section>

        <div class="layout">
          <div class="stack">
            <section class="panel">
              <div class="panel-head"><div><h3>Active Earning Loop</h3><p>Free-first setup, current module health, and today's publishing pace.</p></div><span class="tag good">$0 infrastructure</span></div>
              <div class="panel-body">
                <div class="active-grid">
                  <article v-for="mod in activeModules" :key="mod.name" class="active-module">
                    <span class="module-dot" :class="mod.role"></span>
                    <div>
                      <strong>{{ mod.label }}</strong>
                      <p>{{ mod.free ? 'Free/no-verification path' : 'Needs funded or approved access' }}</p>
                    </div>
                    <span class="tag" :class="mod.free ? 'good' : 'warn'">{{ mod.role }}</span>
                  </article>
                  <p v-if="!activeModules.length" class="empty">No active modules detected.</p>
                </div>
                <div class="quota-card">
                  <div class="quota-top"><strong>Daily article target</strong><span>{{ articleDaily.published }}/{{ articleDaily.limit }}</span></div>
                  <div class="bar"><div class="bar-fill" :style="{ width: articleProgress + '%' }"></div></div>
                  <p class="muted">Normal cycles stop after two successful article generations per UTC day. Use owner orders only for deliberate experiments.</p>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>AI Model Workflow</h3><p>Role-based model routing currently detected by the bot.</p></div></div>
              <div class="panel-body grid-3">
                <article v-for="flow in workflows" :key="flow.name" class="card">
                  <div class="card-top"><h4>{{ flow.name }}</h4><span class="tag" :class="flow.active ? 'good' : 'warn'">{{ flow.active ? 'ready' : 'missing' }}</span></div>
                  <p><strong>{{ flow.provider }}</strong></p>
                  <p class="code-pill">{{ flow.model }}</p>
                  <p>{{ flow.purpose }}</p>
                </article>
                <p v-if="!workflows.length" class="empty">No workflow data yet.</p>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Revenue Focus</h3><p>Next practical moves based on active modules and missing secrets.</p></div></div>
              <div class="panel-body focus-list">
                <article v-for="item in focusItems" :key="item.title" class="focus-item">
                  <span class="focus-rank">{{ item.rank }}</span>
                  <div><div class="row"><strong>{{ item.title }}</strong><span class="tag info">{{ item.action }}</span></div><p class="muted">{{ item.body }}</p></div>
                </article>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Earnings Analysis</h3><p>Breakdown and weekly goal progress.</p></div><span class="tag warn">{{ weekGoalPercent }}% of $10/wk</span></div>
              <div class="panel-body">
                <div class="bar"><div class="bar-fill" :style="{ width: weekGoalPercent + '%' }"></div></div>
                <div class="secret-list" style="margin-top:14px">
                  <div v-for="item in breakdown" :key="item.name" class="secret-item">
                    <strong>{{ item.name }}</strong>
                    <div class="bar"><div class="bar-fill" :style="{ width: item.percent + '%' }"></div></div>
                    <span>{{ money(item.value, 4) }}</span>
                  </div>
                  <p v-if="!breakdown.length" class="empty">No earnings breakdown yet.</p>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Last Evolution</h3><p>The latest code evolution result.</p></div><span class="tag" :class="evolution.error ? 'bad' : 'good'">{{ evolution.error ? 'needs review' : 'ok' }}</span></div>
              <div class="panel-body evo-list">
                <div class="evo-item">
                  <strong>{{ evolution.summary || 'No evolution summary yet.' }}</strong>
                  <p v-if="evolution.error" class="muted">{{ evolution.error }}</p>
                </div>
                <div v-for="change in evolution.changes_applied || []" :key="change.file + change.reason" class="evo-item">
                  <span class="code-pill">{{ change.file }}</span>
                  <p class="muted">{{ change.reason }}</p>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Last Cycle Actions</h3><p>Actions emitted by earning modules during the last cycle.</p></div></div>
              <div class="panel-body action-list">
                <article v-for="action in actions" :key="JSON.stringify(action)" class="action-item">
                  <div class="row"><strong>{{ action.platform || 'unknown' }}</strong><span class="tag" :class="action.success ? 'good' : 'bad'">{{ action.success ? 'success' : 'failed' }}</span></div>
                  <p class="muted">{{ action.title || action.topic || action.symbol || action.error || 'Action recorded' }}</p>
                </article>
                <p v-if="!actions.length" class="empty">No actions recorded in the latest cycle.</p>
              </div>
            </section>
          </div>

          <aside class="stack">
            <section class="panel">
              <div class="panel-head"><div><h3>Secret Readiness</h3><p>Values are detected, never shown.</p></div></div>
              <div class="panel-body secret-list">
                <div v-for="secret in secrets" :key="secret.name" class="secret-item">
                  <strong>{{ secret.label }}</strong>
                  <div class="bar"><div class="bar-fill" :style="{ width: secret.percent + '%' }"></div></div>
                  <span class="tag" :class="secret.active ? 'good' : 'warn'">{{ secret.present_count }}/{{ secret.required_count }}</span>
                  <code v-if="secret.missing && secret.missing.length" style="grid-column:1 / -1">{{ secret.missing.join(', ') }}</code>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Owner Orders</h3><p>Build command.txt for the next cycle.</p></div></div>
              <div class="panel-body">
                <div class="dispatch-card">
                  <div class="row"><strong>Run evolve now</strong><span class="tag info">workflow_dispatch</span></div>
                  <div class="field-grid">
                    <label class="field-label">Repository
                      <input class="cmd-input" v-model="githubRepo" placeholder="owner/repo" @change="rememberWorkflowSettings">
                    </label>
                    <label class="field-label">Ref
                      <input class="cmd-input" v-model="workflowRef" placeholder="main" @change="rememberWorkflowSettings">
                    </label>
                  </div>
                  <label class="field-label">GitHub token
                    <input class="cmd-input" type="password" v-model="githubToken" placeholder="Fine-grained token with Actions write" @change="rememberWorkflowSettings">
                  </label>
                  <div class="button-row">
                    <button class="small-btn primary" :disabled="!canDispatchWorkflow" @click="runWorkflow">{{ dispatchState === 'running' ? 'Ordering...' : 'Run evolve' }}</button>
                    <a class="small-btn" :href="'https://github.com/' + githubRepo + '/actions/workflows/evolve.yml'" target="_blank" rel="noopener">Open Actions</a>
                  </div>
                  <p class="status-line" :class="dispatchStatusClass">{{ dispatchMessage || 'Token stays in this browser local storage, never in status.json.' }}</p>
                </div>
                <div class="segmented">
                  <button class="segment-btn" :class="{ active: activeCommandGroup === 'earn' }" @click="activeCommandGroup = 'earn'">Earn</button>
                  <button class="segment-btn" :class="{ active: activeCommandGroup === 'protect' }" @click="activeCommandGroup = 'protect'">Protect</button>
                  <button class="segment-btn" :class="{ active: activeCommandGroup === 'funded' }" @click="activeCommandGroup = 'funded'">Funded</button>
                  <button class="segment-btn" :class="{ active: activeCommandGroup === 'admin' }" @click="activeCommandGroup = 'admin'">Admin</button>
                </div>
                <div class="preset-grid">
                  <button v-for="preset in activePresets" :key="preset[0]" class="preset-btn" @click="addCommand(preset[0])">
                    <strong>{{ preset[0] }}</strong><span>{{ preset[1] }}</span>
                  </button>
                </div>
                <div class="cmd-row">
                  <input class="cmd-input" v-model="customCommand" @keyup.enter="addCustomCommand" placeholder="Custom order">
                  <button class="small-btn" @click="addCustomCommand">Add</button>
                </div>
                <textarea class="command-area" v-model="commandText"></textarea>
                <div class="button-row">
                  <button class="small-btn primary" @click="copyCommands">{{ copyLabel }}</button>
                  <button class="small-btn" @click="downloadCommands">Download</button>
                  <button class="small-btn danger" @click="clearCommands">Clear</button>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Growth Suggestions</h3><p>Bot-proposed setup ideas.</p></div></div>
              <div class="panel-body action-list">
                <article v-for="item in suggestions" :key="item.title" class="action-item">
                  <div class="row"><strong>{{ item.title }}</strong><span class="tag" :class="item.free_tier ? 'good' : 'warn'">{{ item.free_tier ? 'free' : 'paid' }}</span></div>
                  <p class="muted">{{ item.description }}</p>
                  <span v-if="item.secret_needed" class="code-pill">{{ item.secret_needed }}</span>
                </article>
                <p v-if="!suggestions.length" class="empty">No suggestions yet.</p>
              </div>
            </section>
          </aside>
        </div>

        <footer class="footer">
          <span>Updated {{ lastPoll ? fmtDate(lastPoll) : 'not yet' }}</span>
          <span>GitHub Pages static Vue dashboard</span>
        </footer>
      </main>
    </div>
  `,
}).mount('#app');
"""
