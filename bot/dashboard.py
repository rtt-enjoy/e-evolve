'''Dashboard data publisher.

The interactive dashboard UI lives in frontend/ and is built with Vite into
docs/ for GitHub Pages. Python owns the backend-facing data contract:

  - docs/status.json
  - docs/earnings-log.md

If the React build has not been generated yet, write a tiny fallback shell so
GitHub Pages still has a helpful index.html.
'''
from __future__ import annotations

import html
import json
import logging
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

log = logging.getLogger(__name__)

_LOG_FILE = Path('earnings-log.md')
_HTML_FILE = Path('docs/index.html')
_PUBLIC_STATUS_FILE = Path('docs/status.json')
_PUBLIC_LOG_FILE = Path('docs/earnings-log.md')
_FALLBACK_MARKER = '''<meta name='e-evolve-fallback' content='true'>'''
_FALLBACK_SIGNATURE = 'The React dashboard has not been built yet.'


def write_log(actions: list[dict]) -> None:
    '''Append this cycle's completed actions to earnings-log.md.'''
    if not actions:
        return

    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    lines = [f'\n### {ts}\n']

    for action in actions:
        ok = action.get('success', False)
        icon = '[ok]' if ok else '[fail]'
        platform = action.get('platform', '?')

        if 'title' in action:
            url = action.get('url', '')
            title = str(action.get('title', ''))[:60]
            link = f'[{title}]({url})' if url else title
            est = float(action.get('estimated_usd', 0) or 0)
            lines.append(f'- {icon} **{platform}**: {link} (est. ${est:.2f})')

        elif 'side' in action:
            side = action.get('side', '')
            symbol = action.get('symbol', '')
            if side in ('BUY', 'SELL'):
                val = float(action.get('value_usd', 0) or 0)
                lines.append(f'- {icon} **{platform}** {side} {symbol} - ${val:.2f}')
            elif side == 'HOLD':
                lines.append(f'- [hold] **{platform}** {symbol} - HOLD')
            else:
                err = str(action.get('error', ''))[:80]
                lines.append(f'- [fail] **{platform}** {symbol} - {err}')

        elif 'thread_length' in action:
            url = action.get('url', '#')
            topic = str(action.get('topic', 'thread'))[:50]
            n = action.get('thread_length', 0)
            lines.append(f'- {icon} **{platform}** [{topic}]({url}) ({n} tweets)')

        elif 'metadata_uri' in action:
            tx = action.get('tx_hash') or 'log-only'
            uri = str(action.get('metadata_uri', ''))[:60]
            lines.append(f'- {icon} **{platform}** NFT tx=`{tx}` uri={uri}')

        else:
            err = str(action.get('error', '')).strip()
            if not ok and err:
                lines.append(f'- {icon} **{platform}**: {err[:120]}')
            else:
                lines.append(f'- {icon} **{platform}** action recorded')

    with _LOG_FILE.open('a', encoding='utf-8') as handle:
        handle.write('\n'.join(lines) + '\n')

    log.info('earnings-log.md updated (%d actions)', len(actions))


def write_html(status: dict[str, Any]) -> None:
    '''Publish safe dashboard data files consumed by the React frontend.'''
    _HTML_FILE.parent.mkdir(parents=True, exist_ok=True)
    from bot.status import sanitize_for_git

    public_status = sanitize_for_git(status)
    github_repo = os.getenv('GITHUB_REPO', '').strip()
    if github_repo:
        public_status['github_repo'] = github_repo
    _PUBLIC_STATUS_FILE.write_text(
        json.dumps(public_status, indent=2, default=str),
        encoding='utf-8',
    )

    if _LOG_FILE.exists():
        _PUBLIC_LOG_FILE.write_text(
            _LOG_FILE.read_text(encoding='utf-8'),
            encoding='utf-8',
        )

    if _fallback_needed():
        _HTML_FILE.write_text(_fallback_index(public_status), encoding='utf-8')

    log.info('Dashboard data written -> docs/status.json')


def _fallback_needed() -> bool:
    '''Detect a missing, empty, or older Python-owned fallback page.'''
    if not _HTML_FILE.exists():
        return True
    try:
        if _HTML_FILE.stat().st_size == 0:
            return True
        with _HTML_FILE.open('r', encoding='utf-8', errors='ignore') as handle:
            preview = handle.read(2048)
    except OSError:
        return True
    return _FALLBACK_MARKER in preview or _FALLBACK_SIGNATURE in preview


def _safe_href(value: Any) -> str:
    '''Return an HTTP URL or same-directory relative path safe for an href.'''
    raw = str(value or '').strip()
    if not raw:
        return ''
    parsed = urlparse(raw)
    if parsed.scheme:
        if parsed.scheme.lower() not in {'http', 'https'}:
            return ''
        return raw if parsed.netloc else ''
    if raw.startswith('//') or chr(92) in raw:
        return ''
    if any(ord(char) < 32 for char in raw):
        return ''
    return raw[5:] if raw.startswith('docs/') else raw


def _finite_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _integer(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _display(value: Any, fallback: str) -> str:
    text = str(value or '').strip()
    return html.escape(text or fallback)


def _fallback_index(status: dict[str, Any]) -> str:
    '''Render a status-aware page without replacing a valid React bundle.'''
    earnings = status.get('earnings') if isinstance(status.get('earnings'), dict) else {}
    article_daily = status.get('article_daily') if isinstance(status.get('article_daily'), dict) else {}
    payout = status.get('payout') if isinstance(status.get('payout'), dict) else {}
    payout_public = status.get('payout_public') if isinstance(status.get('payout_public'), dict) else {}

    confirmed = _finite_float(earnings.get('confirmed_usd'))
    published = _integer(article_daily.get('published'))
    product_href = _safe_href(status.get('product_page_url') or 'product.md')
    support_link = (
        '''<a class='button' href='{}'>Support This Work</a>'''.format(product_href)
        if product_href
        else '''<span class='muted'>No support page is configured.</span>'''
    )
    last_run_text = _display(status.get('last_run'), 'not recorded yet')
    repo_name = _display(status.get('github_repo'), 'not recorded')
    network_name = _display(
        payout.get('network') or payout_public.get('network'),
        'not configured',
    )
    confirmed_text = '${:,.2f}'.format(confirmed)
    published_text = str(published)

    page = '''<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  __FALLBACK_MARKER__
  <title>E-Evolve Dashboard</title>
  <style>
    :root{color-scheme:dark;font-family:system-ui,-apple-system,sans-serif}
    body{margin:0;background:#0b0f14;color:#e5edf7}
    main{max-width:760px;margin:12vh auto;padding:0 24px}
    a{color:#6aa6ff}
    code{background:#17202c;padding:2px 6px;border-radius:6px}
    nav{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}
    .button{background:#2563eb;color:#fff;padding:10px 14px;border-radius:8px;text-decoration:none}
    .card{background:#121a24;border:1px solid #263444;border-radius:12px;padding:18px}
    dl{display:grid;grid-template-columns:minmax(150px,1fr) 2fr;gap:12px;margin:0}
    dt{color:#9fb0c3}
    dd{margin:0;overflow-wrap:anywhere}
    .muted{color:#9fb0c3}
  </style>
</head>
<body>
  <main>
    <h1>E-Evolve Dashboard</h1>
    <p>The React bundle is unavailable, but the current cycle data is readable.</p>
    <nav>
      <a href='status.json'>Status JSON</a>
      __SUPPORT_LINK__
    </nav>
    <section class='card' aria-label='Current cycle'>
      <h2>Current cycle</h2>
      <dl>
        <dt>Last completed cycle</dt><dd>__LAST_RUN__</dd>
        <dt>Repository</dt><dd>__REPOSITORY__</dd>
        <dt>Published articles today</dt><dd>__PUBLISHED__</dd>
        <dt>Confirmed on-chain USD</dt><dd>__CONFIRMED__</dd>
        <dt>Payout network</dt><dd>__NETWORK__</dd>
      </dl>
    </section>
    <p class='muted'>Listings, views, and pipeline are not revenue. Only confirmed on-chain receipts count.</p>
    <p>Run <code>npm install</code> and <code>npm run build</code> in <code>frontend/</code> to restore the interactive dashboard.</p>
  </main>
</body>
</html>
'''
    replacements = {
        '__FALLBACK_MARKER__': _FALLBACK_MARKER,
        '__SUPPORT_LINK__': support_link,
        '__LAST_RUN__': last_run_text,
        '__REPOSITORY__': repo_name,
        '__PUBLISHED__': published_text,
        '__CONFIRMED__': confirmed_text,
        '__NETWORK__': network_name,
    }
    for marker, value in replacements.items():
        page = page.replace(marker, value)
    return page