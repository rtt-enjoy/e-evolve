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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_LOG_FILE  = Path("earnings-log.md")
_HTML_FILE = Path("docs/index.html")

# Secrets that are free-tier (no payment required to obtain)
_FREE_TIER_SECRETS = frozenset({
    "GROQ_API_KEY", "DEV_TO_API_KEY", "MEDIUM_INTEGRATION_TOKEN",
    "TWITTER_API_KEY", "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET",
})

# Evolution badge config: status → (text-color, bg-color, border-color)
_EVO_BADGE_STYLES: dict[str, tuple[str, str, str]] = {
    "ok":          ("var(--gn)", "rgba(63,185,80,.15)",  "rgba(63,185,80,.4)"),
    "skipped":     ("var(--mu)", "rgba(139,148,158,.1)", "rgba(139,148,158,.3)"),
    "llm_error":   ("var(--rd)", "rgba(248,81,73,.1)",   "rgba(248,81,73,.35)"),
    "apply_error": ("#e3b341",   "rgba(227,179,65,.1)",  "rgba(227,179,65,.35)"),
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
            return (f"{int(age_s // 3600)}h {int((age_s % 3600) // 60)}m ago", "#e3b341")
        return (f"{int(age_s // 3600)}h ago", "var(--rd)")
    except Exception:
        return (str(last_run_iso), "var(--mu)")


def _evo_status(evo: dict) -> str:
    """Classify evolution result into one of: ok | skipped | llm_error | apply_error."""
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
    return "ok"


# ── Section renderers ──────────────────────────────────────────────────────────

_PROVIDER_PILL_CLASS: dict[str, str] = {
    "gemini":     "pill-provider-gemini",
    "groq":       "pill-provider-groq",
    "openrouter": "pill-provider-openrouter",
    "anthropic":  "pill-provider",
    "claude-cli": "pill-provider",
}

_PROVIDER_ROLE_LABELS: list[tuple[str, str]] = [
    ("think",      "🧠"),
    ("fast",       "⚡"),
    ("experiment", "🧪"),
]


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
                   history: list, spark: str, spark_tip: str) -> str:
    spark_card = (
        f'<div class="stat-card">'
        f'<div class="stat-value sparkline" title="{spark_tip}">{spark}</div>'
        f'<div class="stat-label">Last {len(history)} earning cycles</div>'
        f'</div>'
    ) if spark else ""

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
    bar_color = "var(--gn)" if pct >= 50 else ("#e3b341" if pct >= 20 else "var(--rd)")
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


def _section_suggestions(suggs: list) -> str:
    icons   = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    content = ""
    for i, sg in enumerate(suggs[:5]):
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


def _section_inactive(inactive: list) -> str:
    content = (
        "".join(
            f'<div class="inactive-tag"><span class="inactive-dot"></span>{f}</div>'
            for f in inactive[:8]
        )
        or "<p class='muted'>All features active 🎉</p>"
    )
    return f"""<div class="section">
  <h2>🔒 Inactive Modules</h2>
  <div class="panel">{content}</div>
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
    ("force trade aggressive",  "Raise trade risk to 5%"),
    ("skip evolution",          "Skip Phase 3 this cycle"),
    ("post thread",             "Force a Twitter thread"),
    ("reset earnings",          "Zero this_week_usd"),
    ("status report",           "Dump full status to workflow log"),
    ("force mint 1",            "Mint 1 NFT this cycle"),
    ("force trade conservative","Lower trade risk to 1%"),
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
  var PROVIDERS = {
    gemini:     'pill-provider-gemini',
    groq:       'pill-provider-groq',
    openrouter: 'pill-provider-openrouter',
    anthropic:  'pill-provider',
    'claude-cli': 'pill-provider'
  };
  var ROLE_ICONS = { think: '🧠', fast: '⚡', experiment: '🧪' };

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
    if (secs < 10800) return [Math.floor(secs/3600) + 'h ' + Math.floor((secs%3600)/60) + 'm ago', '#e3b341'];
    return [Math.floor(secs/3600) + 'h ago', 'var(--rd)'];
  }

  function providerPills(provider, roles) {
    if (roles && Object.keys(roles).length) {
      return ['think','fast','experiment'].filter(function(r){ return roles[r]; }).map(function(r) {
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
      .then(function(r){ return r.json(); })
      .then(applyStatus)
      .catch(function(){});
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
  background: rgba(66,133,244,.15); border: 1px solid #4285f4; color: #4285f4;
}
.pill-provider-groq {
  display: inline-block; padding: 2px 9px; border-radius: 20px;
  font-size: .73rem; font-weight: 700; margin-right: 4px;
  background: rgba(249,115,22,.15); border: 1px solid #f97316; color: #f97316;
}
.pill-provider-openrouter {
  display: inline-block; padding: 2px 9px; border-radius: 20px;
  font-size: .73rem; font-weight: 700; margin-right: 4px;
  background: rgba(16,185,129,.15); border: 1px solid #10b981; color: #10b981;
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
  border-radius: 9px; padding: 16px;
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
  border-radius: 9px; padding: 16px;
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
.btn-primary   { background: var(--ac); color: #0d1117; border-color: var(--ac); }
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
  background: var(--gn); color: #0d1117; padding: 8px 18px; border-radius: 20px;
  font-size: .82rem; font-weight: 700; z-index: 999;
}
.copy-toast.show { display: block; animation: fadeup .3s ease; }
@keyframes fadeup {
  from { opacity: 0; transform: translateX(-50%) translateY(8px); }
  to   { opacity: 1; transform: translateX(-50%) translateY(0); }
}

/* ── Footer ── */
footer {
  text-align: center; color: var(--mu); font-size: .76rem;
  margin-top: 32px; padding-top: 14px; border-top: 1px solid var(--br);
}

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
        _section_stats(earn, n_runs, active, inactive, history, spark, spark_tip),
        _section_earnings(earn),
        _section_suggestions(suggs),
        _section_orders(),
        '<div class="two-col">',
        _section_evolution(evo),
        _section_inactive(inactive),
        "</div>",
        _section_actions(actions),
        _section_errors(errors),
        _ORDERS_JS,
        _LIVE_JS,
    ])

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
</footer>
</body>
</html>"""
