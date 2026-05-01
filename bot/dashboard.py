"""
Dashboard Generator
Writes docs/index.html (GitHub Pages) and appends to earnings-log.md.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_LOG_FILE  = Path("earnings-log.md")
_HTML_FILE = Path("docs/index.html")


def write_log(actions: list[dict]) -> None:
    """Append this cycle's actions to earnings-log.md."""
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


# ── HTML renderer ─────────────────────────────────────────────────────────────

def _sparkline(history: list) -> str:
    """Render a Unicode block sparkline from a list of floats."""
    bars = " ▁▂▃▄▅▆▇█"
    if not history:
        return ""
    mx = max(history) or 1
    return "".join(bars[min(8, int(v / mx * 8))] for v in history)


def _last_run_age(last_run_iso: Any) -> tuple[str, str]:
    """Returns (age_label, css_color) based on how stale the last run is."""
    if not last_run_iso:
        return ("never", "var(--rd)")
    try:
        from datetime import datetime, timezone
        dt = datetime.fromisoformat(str(last_run_iso).replace("Z", "+00:00"))
        age_s = (datetime.now(timezone.utc) - dt).total_seconds()
        if age_s < 4500:   # < 75min — healthy
            return (f"{int(age_s//60)}m ago", "var(--gn)")
        if age_s < 10800:  # < 3h — stale
            return (f"{int(age_s//3600)}h {int((age_s%3600)//60)}m ago", "#e3b341")
        return (f"{int(age_s//3600)}h ago", "var(--rd)")
    except Exception:
        return (str(last_run_iso), "var(--mu)")


def _earnings_projection(earn: dict) -> str:
    """Weekly earnings projection based on rolling history."""
    history = earn.get("history", [])
    if len(history) < 2:
        return ""
    avg = sum(history) / len(history)
    cycles_per_week = 168  # 24*7
    projected = round(avg * cycles_per_week, 2)
    this_week = earn.get("this_week_usd", 0)
    goal = 10.0
    pct = min(100, int(this_week / goal * 100)) if goal else 0
    bar_color = "var(--gn)" if pct >= 50 else ("#e3b341" if pct >= 20 else "var(--rd)")
    return (
        f'<div class="proj">'
        f'<div class="proj-row"><span>Weekly projection (avg {avg:.4f}/cycle × 168):</span>'
        f'<strong style="color:var(--gn)">${projected:.2f}/week</strong></div>'
        f'<div class="proj-row"><span>Progress to $10/week goal:</span>'
        f'<span style="color:{bar_color}">{pct}%</span></div>'
        f'<div class="prog-bar"><div class="prog-fill" style="width:{pct}%;background:{bar_color}"></div></div>'
        f'</div>'
    )


def _breakdown_bars(breakdown: dict) -> str:
    if not breakdown:
        return ""
    total = sum(breakdown.values()) or 1
    rows = ""
    for plat, amt in sorted(breakdown.items(), key=lambda x: -x[1]):
        pct = int(amt / total * 100)
        rows += (
            f'<div class="bd-row">'
            f'<span class="bd-lbl">{plat}</span>'
            f'<div class="bd-bar-wrap"><div class="bd-bar" style="width:{pct}%"></div></div>'
            f'<span class="bd-amt">${amt:.4f}</span>'
            f'</div>'
        )
    return f'<div class="bd">{rows}</div>'


def _render(s: dict[str, Any]) -> str:
    version  = s.get("version", "1.0.0")
    last_run = _fmt(s.get("last_run"))
    n_runs   = s.get("total_runs", 0)
    provider = s.get("llm_provider", "unknown")
    active   = s.get("active_features", [])
    inactive = s.get("inactive_features", [])
    earn     = s.get("earnings", {})
    suggs    = s.get("suggestions", [])
    evo      = s.get("last_evolution", {})
    last_ea  = s.get("last_earning", {})
    actions  = last_ea.get("actions", [])
    errors   = s.get("errors", [])

    age_label, age_color = _last_run_age(s.get("last_run"))
    proj_html    = _earnings_projection(earn)
    breakdown_html = _breakdown_bars(earn.get("breakdown", {}))
    cycle_secs   = s.get("last_cycle_seconds")
    cycle_str    = f"{cycle_secs}s" if cycle_secs else "—"

    # badges
    badges = "".join(f'<span class="b g">{f}</span>' for f in active) \
          or '<span class="b r">no active modules — add a secret</span>'

    # suggestions
    sug_html = ""
    icons = ["🥇","🥈","🥉","4️⃣","5️⃣"]
    for i, sg in enumerate(suggs[:5]):
        sec   = sg.get("secret_needed")
        est   = sg.get("estimated_weekly_usd", 0)
        s_blk = f'<div class="spill">Add secret: <code>{sec}</code></div>' if sec else ""
        e_blk = f'<div class="est">~${est:.0f}/week estimated</div>' if est else ""
        sug_html += (
            f'<div class="sc">'
            f'<span class="rank">{icons[i] if i < len(icons) else "•"}</span>'
            f'<div><strong>{sg.get("title","")}</strong>'
            f'<p>{sg.get("description","")}</p>{s_blk}{e_blk}</div></div>'
        )

    # evolution status badge (#10)
    evo_err      = evo.get("error")
    evo_err_type = evo.get("error_type", "")
    evo_summary  = evo.get("summary", "—")
    if not evo_err and evo.get("changes_applied"):
        evo_status = "ok"
    elif not evo_err and "skipped by owner" in evo_summary.lower():
        evo_status = "skipped"
    elif evo_err and evo_err_type in ("413", "json", "api"):
        evo_status = "llm_error"
    elif evo_err:
        evo_status = "apply_error"
    else:
        evo_status = "ok"

    _evo_badge_style = {
        "ok":          ("var(--gn)", "rgba(63,185,80,.15)",  "rgba(63,185,80,.4)"),
        "skipped":     ("var(--mu)", "rgba(139,148,158,.1)", "rgba(139,148,158,.3)"),
        "llm_error":   ("var(--rd)", "rgba(248,81,73,.1)",   "rgba(248,81,73,.35)"),
        "apply_error": ("#e3b341",   "rgba(227,179,65,.1)",  "rgba(227,179,65,.35)"),
    }
    _bc, _bg, _border = _evo_badge_style.get(evo_status, _evo_badge_style["ok"])
    evo_badge = (
        f'<span style="display:inline-block;padding:1px 8px;border-radius:20px;'
        f'font-size:.73rem;font-weight:700;color:{_bc};background:{_bg};'
        f'border:1px solid {_border};margin-left:8px">{evo_status}</span>'
    )

    # clean LLM error message (#7)
    if evo_err:
        import re as _re
        _msg_match = _re.search(r"'message':\s*'([^']{1,200})'", evo_err)
        clean_err  = _msg_match.group(1) if _msg_match else evo_err[:200]
        _type_label = {"413": "413 Too Large", "json": "JSON Parse Error", "api": "API Error"}.get(evo_err_type, "Error")
        evo_err_html = (
            f'<div style="margin-top:8px;padding:6px 10px;background:rgba(248,81,73,.08);'
            f'border:1px solid rgba(248,81,73,.25);border-radius:5px;font-size:.8rem;color:var(--rd)">'
            f'<strong>{_type_label}:</strong> {clean_err}</div>'
        )
    else:
        evo_err_html = ""

    # evo changes
    evo_items = "".join(
        f"<li><code>{c.get('file','')}</code> — {c.get('reason','')[:80]}</li>"
        for c in evo.get("changes_applied", [])
    ) or "<li>No file changes this cycle</li>"

    # action table
    rows = ""
    for a in actions[-20:]:
        ok   = a.get("success", False)
        plat = a.get("platform", "?")
        ic   = "✅" if ok else "❌"
        err  = (a.get("error") or "")[:80]
        if "title" in a:
            title = (a.get("title") or "").strip()
            url   = (a.get("url") or "").strip()
            if ok and title and url:
                detail = f'<a href="{url}" target="_blank">{title[:50]}</a>'
            else:
                detail = f'<span class="err">{plat} — {err or "unknown error"}</span>'
        elif "side" in a:
            detail = f'{a.get("side")} {a.get("symbol","")} ${a.get("value_usd",0):.2f}'
        elif "thread_length" in a:
            url   = (a.get("url") or "").strip()
            topic = (a.get("topic") or "thread")[:50]
            detail = f'<a href="{url}" target="_blank">{topic}</a>' if url else f'<span class="err">{topic} — {err}</span>'
        else:
            detail = (a.get("metadata_uri") or err or "")[:50]
        rows += f"<tr><td>{ic}</td><td>{plat}</td><td>{detail}</td></tr>"

    # inactive list
    inact_html = "".join(
        f'<div class="ic"><span class="dot"></span>{f}</div>' for f in inactive[:8]
    ) or '<p class="muted">All features active 🎉</p>'

    # errors
    err_html = ""
    if errors:
        items = "".join(f"<li>{e[:120]}</li>" for e in errors[-5:])
        err_html = f'<div class="ebox"><h3>⚠️ Recent Errors</h3><ul>{items}</ul></div>'

    history   = earn.get("history", [])
    spark     = _sparkline(history)
    spark_tip = " · ".join(f"${v:.4f}" for v in history) if history else "no data"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta http-equiv="refresh" content="3600"/>
<title>E-Evolve Dashboard</title>
<style>
:root{{--bg:#0d1117;--sf:#161b22;--br:#30363d;--tx:#c9d1d9;--mu:#8b949e;
      --ac:#58a6ff;--gn:#3fb950;--rd:#f85149;--pu:#bc8cff;--yw:#e3b341;
      --f:'Segoe UI',system-ui,sans-serif}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:var(--f);padding:20px;max-width:960px;margin:0 auto}}
a{{color:var(--ac)}}
h2{{font-size:.82rem;text-transform:uppercase;letter-spacing:.07em;color:var(--mu);margin-bottom:12px}}
header{{display:flex;align-items:flex-start;gap:14px;border-bottom:1px solid var(--br);padding-bottom:18px;margin-bottom:22px}}
.logo{{font-size:2.2rem;line-height:1}}
h1{{font-size:1.4rem;margin-bottom:6px}}
.pill{{display:inline-block;padding:2px 9px;border-radius:20px;font-size:.73rem;font-weight:700;margin-right:4px}}
.pa{{background:rgba(88,166,255,.15);border:1px solid var(--ac);color:var(--ac)}}
.pp{{background:rgba(188,140,255,.15);border:1px solid var(--pu);color:var(--pu)}}
.mu{{color:var(--mu);font-size:.8rem;margin-top:5px}}
.b{{display:inline-block;padding:2px 8px;border-radius:20px;font-size:.76rem;margin:2px}}
.g{{background:rgba(63,185,80,.15);border:1px solid var(--gn);color:var(--gn)}}
.r{{background:rgba(248,81,73,.1);border:1px solid var(--rd);color:var(--rd)}}
.sg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:26px}}
.st{{background:var(--sf);border:1px solid var(--br);border-radius:9px;padding:16px}}
.st .v{{font-size:1.8rem;font-weight:700;color:var(--gn)}}
.st .v.spark{{font-size:1.2rem;font-family:monospace;letter-spacing:2px;cursor:default}}
.st .v.neutral{{color:var(--tx)}}
.st .l{{color:var(--mu);font-size:.78rem;margin-top:2px}}
.st .sub{{font-size:.75rem;color:var(--mu);margin-top:4px}}
.sec{{margin-bottom:26px}}
.pan{{background:var(--sf);border:1px solid var(--br);border-radius:9px;padding:16px}}
.sc{{display:flex;gap:12px;padding:12px;border:1px solid var(--br);border-radius:7px;margin-bottom:8px}}
.rank{{font-size:1.4rem;flex-shrink:0;line-height:1}}
.sc p{{color:var(--mu);font-size:.86rem;margin-top:3px}}
.spill{{background:rgba(88,166,255,.1);border:1px solid rgba(88,166,255,.3);border-radius:4px;padding:3px 8px;margin-top:6px;font-size:.8rem;display:inline-block}}
.est{{color:var(--gn);font-size:.8rem;margin-top:4px}}
ul.ev{{padding-left:16px;color:var(--mu);font-size:.86rem}}
ul.ev li{{margin-bottom:4px}}
table{{width:100%;border-collapse:collapse;font-size:.86rem}}
th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid var(--br)}}
th{{color:var(--mu);font-weight:500}}
.ic{{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border:1px solid var(--br);border-radius:6px;margin:3px;font-size:.8rem}}
.dot{{width:6px;height:6px;border-radius:50%;background:var(--rd);flex-shrink:0}}
.ebox{{background:rgba(248,81,73,.08);border:1px solid rgba(248,81,73,.3);border-radius:7px;padding:12px;margin-top:14px}}
.ebox h3{{color:var(--rd)}}
.ebox li{{color:var(--mu);font-size:.83rem;margin-top:3px}}
.muted{{color:var(--mu)}}
.err{{color:var(--rd);font-size:.83rem}}
footer{{text-align:center;color:var(--mu);font-size:.76rem;margin-top:32px;padding-top:14px;border-top:1px solid var(--br)}}
.proj{{margin-top:12px;padding:12px;background:rgba(63,185,80,.06);border:1px solid rgba(63,185,80,.2);border-radius:7px}}
.proj-row{{display:flex;justify-content:space-between;align-items:center;font-size:.85rem;margin-bottom:6px}}
.prog-bar{{height:6px;background:var(--br);border-radius:3px;overflow:hidden;margin-top:2px}}
.prog-fill{{height:100%;border-radius:3px;transition:width .3s}}
.bd{{margin-top:10px}}
.bd-row{{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:.83rem}}
.bd-lbl{{width:80px;color:var(--mu);flex-shrink:0}}
.bd-bar-wrap{{flex:1;height:8px;background:var(--br);border-radius:4px;overflow:hidden}}
.bd-bar{{height:100%;background:var(--gn);border-radius:4px}}
.bd-amt{{width:70px;text-align:right;color:var(--gn)}}
.age-pill{{display:inline-block;padding:1px 7px;border-radius:10px;font-size:.72rem;font-weight:600;margin-left:6px}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:600px){{.two-col{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header>
  <div class="logo">🤖</div>
  <div>
    <h1>E-Evolve <span class="pill pa">v{version}</span><span class="pill pp">{provider}</span></h1>
    <div style="margin-top:5px">{badges}</div>
    <div class="mu">
      Last cycle: {last_run}
      <span class="age-pill" style="background:rgba(0,0,0,.3);color:{age_color};border:1px solid {age_color}">{age_label}</span>
      &nbsp;·&nbsp; Total cycles: {n_runs}
      &nbsp;·&nbsp; Cycle time: {cycle_str}
    </div>
  </div>
</header>

<div class="sg">
  <div class="st"><div class="v">${earn.get("total_usd",0):.2f}</div><div class="l">Total earned</div></div>
  <div class="st"><div class="v">${earn.get("this_week_usd",0):.2f}</div><div class="l">This week</div><div class="sub">last cycle: ${earn.get("last_cycle_usd",0):.4f}</div></div>
  <div class="st"><div class="v neutral">{n_runs}</div><div class="l">Cycles run</div></div>
  <div class="st"><div class="v neutral">{len(active)}</div><div class="l">Active modules</div><div class="sub">{len(inactive)} inactive</div></div>
  {"" if not spark else f'<div class="st"><div class="v spark" title="{spark_tip}">{spark}</div><div class="l">Last {len(history)} earning cycles</div></div>'}
</div>

{"" if not proj_html and not breakdown_html else f'''<div class="sec">
  <h2>📈 Earnings Analysis</h2>
  <div class="pan">
    {proj_html}
    {breakdown_html}
  </div>
</div>'''}

<div class="sec">
  <h2>🧠 Smart Growth Suggestions</h2>
  <div class="pan">{"<p class='muted'>Suggestions appear after the first evolution cycle.</p>" if not sug_html else sug_html}</div>
</div>

<div class="two-col">
  <div class="sec">
    <h2>⚡ Last Evolution</h2>
    <div class="pan">
      <p style="margin-bottom:9px"><strong>{evo_summary}</strong>{evo_badge}</p>
      <ul class="ev">{evo_items}</ul>
      {evo_err_html}
    </div>
  </div>

  <div class="sec">
    <h2>🔒 Inactive Modules</h2>
    <div class="pan">{inact_html}</div>
  </div>
</div>

<div class="sec">
  <h2>💰 Last Cycle Actions</h2>
  <div class="pan">
    {"<p class='muted'>No actions yet — add a secret to activate an earning module.</p>"
     if not rows else
     f'<table><thead><tr><th></th><th>Platform</th><th>Detail</th></tr></thead><tbody>{rows}</tbody></table>'
     f'<p class="muted" style="font-size:.78rem;margin-top:8px">Showing last {min(len(actions),20)} of {len(actions)} · <a href="earnings-log.md">full log</a></p>'}
  </div>
</div>

{err_html}

<footer>
  E-Evolve · hourly via GitHub Actions ·
  <a href="status.json">status.json</a> · <a href="earnings-log.md">earnings log</a>
</footer>
</body>
</html>"""


def _fmt(iso: Any) -> str:
    if not iso:
        return "never"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(iso)
