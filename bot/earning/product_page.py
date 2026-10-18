'''Product landing page generator.

Writes docs/product.md: a single page that introduces the bot's work, lists
recent articles, and publishes the receive address. The owner can link to it
from a README, a FUNDING.yml, or any channel that needs a product page.

No LLM call, no network access. Reads the wallet address from the environment
or from a status file if one exists, so it can be run by hand or from a
GitHub Action.
'''
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

OUTPUT_FILE = Path('docs/product.md')
STATUS_FILE = Path('docs/status.json')

_TEMPLATE = '''# Support This Work

## What This Project Does

This is an automated research and publishing bot that writes daily technical
articles for developers on dev.to. It explores trending topics, writes original
pieces, and appends a support footer to every post.

## How to Support

If an article saved you time, a small tip keeps the research running. There is
no paywall, no subscription, and no platform taking a cut.

Send **{asset}** on **{network}** to:

```
{address}
```

## Recent Articles

{articles}

Generated: {ts}
'''


def _wallet_address() -> str:
    '''Return the published Tron address, or '' when none is configured.'''
    env_address = os.getenv('USDT_WALLET_ADDRESS', '').strip()
    if env_address:
        return env_address
    try:
        data = json.loads(STATUS_FILE.read_text(encoding='utf-8'))
        return str((data.get('payout') or {}).get('address', '')).strip()
    except Exception:
        return ''


def _recent_articles(status: dict[str, Any]) -> str:
    '''Return markdown list of top articles from the status snapshot.'''
    articles = status.get('article_stats') or {}
    best_title = articles.get('best_title', '')
    best_url = articles.get('best_url', '')
    if not best_title:
        return '_No articles yet._'
    return f'- [{best_title}]({best_url})'


def generate(status: dict[str, Any] | None = None) -> str:
    '''Return the markdown content for the product page.'''
    address = _wallet_address()
    if not address:
        log.warning('[product_page] no wallet address found; writing page without it')
    
    payout = (status or {}).get('payout_public') or {}
    network = payout.get('network', 'TRC-20 (Tron)')
    asset = payout.get('asset', 'USDT, USDC or USDD')
    
    articles_md = _recent_articles(status or {})
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    
    return _TEMPLATE.format(
        asset=asset,
        network=network,
        address=address or 'Address not configured',
        articles=articles_md,
        ts=ts,
    )


def write(status: dict[str, Any] | None = None) -> None:
    '''Generate and write the product page.'''
    content = generate(status)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content, encoding='utf-8')
    log.info('[product_page] wrote %s', OUTPUT_FILE)


if __name__ == '__main__':
    _status: dict[str, Any] = {}
    if STATUS_FILE.exists():
        try:
            _status = json.loads(STATUS_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    write(_status)