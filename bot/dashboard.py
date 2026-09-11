'''
Dashboard data publisher.

The interactive dashboard UI lives in frontend/ and is built with Vite into
docs/ for GitHub Pages. Python owns the backend-facing data contract:

  - docs/status.json
  - docs/earnings-log.md

The fallback shell is marker-owned so a later React build can replace it
without Python overwriting a valid frontend bundle.
'''
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_LOG_FILE = Path('earnings-log.md')
_HTML_FILE = Path('docs/index.html')
_PUBLIC_STATUS_FILE = Path('docs/status.json')
_PUBLIC_LOG_FILE = Path('docs/earnings-log.md')
_FALLBACK_MARKER = '<!-- E-EVOLVE_DASHBOARD_FALLBACK -->'
_LEGACY_FALLBACK_TEXT = 'The React dashboard has not been built yet.'


def write_log(actions: list[dict]) -> None:
    '''Append this cycle's completed actions to earnings-log.md.'''
    if not actions:
        return

    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    newline = chr(10)
    lines = [newline + '### ' + ts + newline]

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
        handle.write(newline.join(lines) + newline)

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

    if _needs_fallback():
        _HTML_FILE.write_text(_fallback_index(public_status), encoding='utf-8')

    log.info('Dashboard data written -> docs/status.json')


def _needs_fallback() -> bool:
    '''Return whether docs/index.html is a marker-owned or legacy fallback.'''
    try:
        current = _HTML_FILE.read_text(encoding='utf-8')
    except FileNotFoundError:
        return True
    except OSError as exc:
        log.warning('Cannot inspect dashboard fallback: %s', exc)
        return False

    is_legacy = (
        _LEGACY_FALLBACK_TEXT in current
        and '<h1>E-Evolve Dashboard</h1>' in current
    )
    return _FALLBACK_MARKER in current or is_legacy


def _fallback_index(public_status: dict[str, Any]) -> str:
    '''Build a small, self-refreshing page for an unbuilt frontend bundle.'''
    initial = {
        'status': public_status,
        'generated_at': datetime.now(timezone.utc).isoformat(),
    }
    payload = _json_for_script(initial)
    template = '''<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <meta name='description' content='E-Evolve dashboard fallback'>
  <title>E-Evolve Dashboard</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0b0f14;
      color: #e5edf7;
      line-height: 1.5;
    }
    main {
      width: min(100% - 32px, 860px);
      margin: 0 auto;
      padding: 56px 0;
    }
    h1, h2, p { margin-top: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); letter-spacing: -0.04em; }
    h2 { font-size: 1.35rem; }
    .subtitle { color: #9fb0c3; max-width: 680px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin: 28px 0;
    }
    .card {
      background: #111923;
      border: 1px solid #223142;
      border-radius: 14px;
      padding: 16px;
    }
    .label {
      display: block;
      color: #8ea3b8;
      font-size: 0.78rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    .card strong { display: block; margin-top: 5px; font-size: 1.05rem; }
    .support {
      background: #111923;
      border: 1px solid #223142;
      border-radius: 14px;
      padding: 20px;
      margin: 12px 0 28px;
    }
    .support p { margin-bottom: 10px; }
    code {
      display: block;
      margin-top: 5px;
      overflow-wrap: anywhere;
      color: #b9dcff;
      background: #080d13;
      border: 1px solid #223142;
      border-radius: 8px;
      padding: 8px;
    }
    footer {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
      color: #8ea3b8;
      font-size: 0.9rem;
    }
    button, a {
      color: #b9dcff;
      text-decoration: none;
      border: 1px solid #35618c;
      border-radius: 9px;
      background: #12263a;
      padding: 8px 12px;
      cursor: pointer;
    }
    button:hover, a:hover { border-color: #6aa6ff; }
    #refresh-status { flex: 1 1 220px; }
    @media (max-width: 560px) {
      main { padding: 32px 0; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <p class='subtitle'>E-Evolve</p>
    <h1>Dashboard</h1>
    <p class='subtitle'>This is the lightweight fallback shown before the React dashboard is built. It reads the latest public status directly.</p>

    <section class='grid' aria-label='Current status'>
      <article class='card'><span class='label'>Last cycle</span><strong id='last-cycle'>Not reported</strong></article>
      <article class='card'><span class='label'>Confirmed</span><strong id='confirmed'>Not reported</strong></article>
      <article class='card'><span class='label'>Articles</span><strong id='articles'>Not reported</strong></article>
      <article class='card'><span class='label'>On-chain balance</span><strong id='wallet'>Not reported</strong></article>
    </section>

    <section class='support' aria-labelledby='support-heading'>
      <h2 id='support-heading'>Support this work</h2>
      <p id='support-note'>No support note is configured.</p>
      <p><span class='label'>Network</span><code id='support-network'>Not reported</code></p>
      <p><span class='label'>Address</span><code id='support-address'>No public receive address configured</code></p>
    </section>

    <footer>
      <button type='button' id='refresh'>Refresh now</button>
      <a href='status.json'>Open status.json</a>
      <span id='repo'>Local dashboard status</span>
      <span id='last-updated'>Not reported</span>
      <span id='refresh-status' aria-live='polite'>Loading public status...</span>
    </footer>
  </main>

  <script id='dashboard-data' type='application/json'>{PAYLOAD}</script>
  <script>
    'use strict';

    const initialData = JSON.parse(document.getElementById('dashboard-data').textContent);
    const fields = {
      'last-cycle': document.getElementById('last-cycle'),
      'confirmed': document.getElementById('confirmed'),
      'articles': document.getElementById('articles'),
      'wallet': document.getElementById('wallet'),
      'support-heading': document.getElementById('support-heading'),
      'support-note': document.getElementById('support-note'),
      'support-network': document.getElementById('support-network'),
      'support-address': document.getElementById('support-address'),
      'repo': document.getElementById('repo'),
      'last-updated': document.getElementById('last-updated'),
      'refresh-status': document.getElementById('refresh-status'),
      'refresh': document.getElementById('refresh'),
    };

    const money = new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

    function displayMoney(value) {
      const number = Number(value);
      return Number.isFinite(number) ? money.format(number) : 'Not reported';
    }

    function displayNumber(value) {
      const number = Number(value);
      return Number.isFinite(number) ? number.toLocaleString(undefined, {maximumFractionDigits: 2}) : 'Not reported';
    }

    function displayTime(value) {
      const date = new Date(value);
      return Number.isNaN(date.getTime()) ? 'Not reported' : date.toLocaleString();
    }

    function setText(id, value) {
      const element = fields[id];
      if (!element) return;
      element.textContent = value == null || value === '' ? 'Not reported' : String(value);
    }

    function update(data) {
      const status = data && typeof data === 'object' && data.status ? data.status : data;
      if (!status || typeof status !== 'object') return;

      const earnings = status.earnings || {};
      const wallet = status.wallet || {};
      const payout = status.payout_public || {};
      const articleStats = status.article_stats || {};

      setText('last-cycle', displayMoney(earnings.last_cycle_usd));
      setText('confirmed', displayMoney(earnings.confirmed_usd));
      setText('articles', displayNumber(articleStats.count));
      setText('wallet', displayMoney(wallet.confirmed_usd));
      setText('support-heading', String(payout.heading || 'Support this work'));
      setText('support-note', String(payout.note || 'No support note is configured.'));
      setText('support-network', String(payout.network || wallet.network || 'Not reported'));
      setText('support-address', String(payout.address || wallet.address || '') || 'No public receive address configured');
      setText('repo', String(status.github_repo || 'Local dashboard status'));
      setText('last-updated', displayTime(status.updated_at || status.last_run || initialData.generated_at));
    }

    async function refresh() {
      fields['refresh-status'].textContent = 'Updating...';
      try {
        const response = await fetch('status.json', {cache: 'no-store'});
        if (!response.ok) throw new Error('HTTP ' + response.status);
        const data = await response.json();
        update(data);
        fields['refresh-status'].textContent = 'Updated ' + new Date().toLocaleTimeString();
      } catch (error) {
        console.error('[dashboard] status refresh failed', error);
        fields['refresh-status'].textContent = 'Status refresh failed; retrying automatically.';
      }
    }

    fields['refresh'].addEventListener('click', refresh);
    window.addEventListener('online', refresh);
    update(initialData.status || initialData);
    refresh();
    setInterval(refresh, 60000);
  </script>

  {_FALLBACK_MARKER}
</body>
</html>
'''
    return template.replace('{PAYLOAD}', payload)


def _json_for_script(value: Any) -> str:
    '''Serialize dashboard data without allowing script termination.'''
    return (
        json.dumps(value, ensure_ascii=False, default=str)
        .replace('</', '<' + chr(92) + '/')
        .replace(chr(8232), chr(92) + 'u2028')
        .replace(chr(8233), chr(92) + 'u2029')
    )