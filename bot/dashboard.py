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

    # evo changes
    evo_items = "".join(
        f"<li><code>{c.get('file','')}</code> — {c.get('reason','')[:80]}</li>"
        for c in evo.get("changes_applied", [])
    ) or "<li>No file changes this cycle</li>"

    # action table
    rows = ""
    for a in actions[-12:]:
        ok   = a.get("success", False)
        plat = a.get("platform", "?")
        ic   = "✅" if ok else "❌"
        if "title" in a:
            detail = f'<a href="{a.get("url","#")}" target="_blank">{a["title"][:50]}</a>'
        elif "side" in a:
            detail = f'{a.get("side")} {a.get("symbol","")} ${a.get("value_usd",0):.2f}'
        elif "thread_length" in a:
            detail = f'<a href="{a.get("url","#")}" target="_blank">{a.get("topic","thread")[:50]}</a>'
        else:
            detail = (a.get("metadata_uri") or a.get("error") or "")[:50]
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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta http-equiv="refresh" content="3600"/>
<title>E-Evolve Dashboard</title>
<style>
:root{{--bg:#0d1117;--sf:#161b22;--br:#30363d;--tx:#c9d1d9;--mu:#8b949e;
      --ac:#58a6ff;--gn:#3fb950;--rd:#f85149;--pu:#bc8cff;
      --f:'Segoe UI',system-ui,sans-serif}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:var(--f);padding:20px}}
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
.sg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:26px}}
.st{{background:var(--sf);border:1px solid var(--br);border-radius:9px;padding:16px}}
.st .v{{font-size:1.8rem;font-weight:700;color:var(--gn)}}
.st .l{{color:var(--mu);font-size:.78rem;margin-top:2px}}
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
footer{{text-align:center;color:var(--mu);font-size:.76rem;margin-top:32px;padding-top:14px;border-top:1px solid var(--br)}}
</style>
</head>
<body>
<header>
  <div class="logo">🤖</div>
  <div>
    <h1>E-Evolve <span class="pill pa">v{version}</span><span class="pill pp">{provider}</span></h1>
    <div style="margin-top:5px">{badges}</div>
    <div class="mu">Last cycle: {last_run} &nbsp;·&nbsp; Total cycles: {n_runs}</div>
  </div>
</header>

<div class="sg">
  <div class="st"><div class="v">${earn.get("total_usd",0):.2f}</div><div class="l">Total earned</div></div>
  <div class="st"><div class="v">${earn.get("this_week_usd",0):.2f}</div><div class="l">This week</div></div>
  <div class="st"><div class="v">{n_runs}</div><div class="l">Cycles run</div></div>
  <div class="st"><div class="v">{len(active)}</div><div class="l">Active modules</div></div>
</div>

<div class="sec">
  <h2>🧠 Smart Growth Suggestions</h2>
  <div class="pan">{"<p class='muted'>Suggestions appear after the first evolution cycle.</p>" if not sug_html else sug_html}</div>
</div>

<div class="sec">
  <h2>⚡ Last Evolution</h2>
  <div class="pan">
    <p style="margin-bottom:9px"><strong>{evo.get("summary","—")}</strong></p>
    <ul class="ev">{evo_items}</ul>
  </div>
</div>

<div class="sec">
  <h2>💰 Last Cycle Actions</h2>
  <div class="pan">
    {"<p class='muted'>No actions yet — add a secret to activate an earning module.</p>"
     if not rows else
     f"<table><thead><tr><th></th><th>Platform</th><th>Detail</th></tr></thead><tbody>{rows}</tbody></table>"}
  </div>
</div>

<div class="sec">
  <h2>🔒 Inactive Modules (add secrets to unlock)</h2>
  <div class="pan">{inact_html}</div>
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
