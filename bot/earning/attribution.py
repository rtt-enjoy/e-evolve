'''
Which published work earned the money.

Principle 5 of ``docs/passive-income-doctrine.md`` says to measure the funnel,
not the last stage, and it names this gap explicitly: views are measured, but
what happens after a reader reaches the footer is not. That was acceptable
while the footer had never shipped -- there was nothing downstream to measure.
It stops being acceptable the moment the receive path goes live, because the
first tip to arrive is also the first data point this project has ever had
about *what people pay for*, and an unattributed dollar teaches nothing.

The problem is that a TRC-20 transfer carries no memo tying it to an article.
Nobody tips through a tracked link; they read a post, copy an address, and send
from a wallet the bot cannot see. So exact per-post attribution is not
available, and pretending otherwise would be the same fabrication this project
has already deleted twice.

What *is* available is the publishing context at the moment money arrived:
which posts were live, which one was performing, which archetype and tags they
carried. That is correlation, not proof, and this module labels it as such --
``confidence`` is never better than ``"correlated"``. Across enough receipts a
pattern in that record is real evidence; a single receipt is a single receipt,
which is exactly why ``count`` is reported alongside every total.

Design rules, matching the rest of the earning layer:

- **Deterministic. No LLM call.** This reads numbers the other loops already
  fetched and writes them down. A model asked to guess which post earned a tip
  would produce a confident answer with nothing behind it.
- **Triggered by the wallet, never by a publish.** A record is written only
  when ``wallet.last_received_usd`` is above zero -- i.e. real money moved
  on-chain. Nothing here can invent revenue, because nothing here decides that
  revenue happened.
- **Count each transfer once.** Wallet snapshots retain ``last_received_usd``
  and ``last_received_at`` between polls. Without a receipt key, every hourly
  cycle would append the same transfer and inflate both the receipt count and
  attributed total.
- **Never raises.** Attribution is bookkeeping. Losing a cycle over it would
  trade the working system for a note about the working system.
'''
from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Any

from . import _shared

log = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
    'enabled': True,
    # Receipts are the rarest event in this system; a low limit would discard
    # the only evidence it ever collects. 200 is small in bytes and long in
    # time -- at the observed tip rate it is effectively 'keep everything'.
    'history_limit': 200,
}

_TX_FIELDS = (
    'last_received_tx',
    'last_received_hash',
    'tx_hash',
    'transaction_hash',
    'transaction_id',
)
_BLOCK_FIELDS = (
    'last_received_block',
    'block_number',
    'transaction_index',
)


def config() -> dict[str, Any]:
    '''This module's slice of config/strategy.json, read at call time.'''
    return _shared.load_config('attribution', DEFAULTS)


def _as_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _finite_amount(value: Any) -> float:
    try:
        amount = float(str(value).replace(',', '').strip())
    except (TypeError, ValueError):
        return 0.0
    return amount if math.isfinite(amount) else 0.0


def _canonical_timestamp(value: Any) -> str | None:
    if value in (None, ''):
        return None
    parsed = _shared.parse_dt(value)
    if parsed is None:
        return None
    return parsed.astimezone(timezone.utc).isoformat(timespec='seconds')


def _wallet_receipt_key(wallet: dict[str, Any]) -> str | None:
    '''Build a stable key from public wallet receipt metadata.'''
    tx = next(
        (
            str(wallet.get(field)).strip().lower()
            for field in _TX_FIELDS
            if wallet.get(field) not in (None, '')
        ),
        '',
    )
    if tx:
        return f'tx:{tx}'

    at = _canonical_timestamp(wallet.get('last_received_at'))
    if not at:
        # A changing amount alone is not a safe identity. Refusing this rare
        # snapshot is safer than creating one bookkeeping row per poll.
        return None

    amount = _finite_amount(wallet.get('last_received_usd'))
    network = str(wallet.get('network') or '').strip().lower()
    anchor = next(
        (
            str(wallet.get(field)).strip()
            for field in _BLOCK_FIELDS
            if wallet.get(field) not in (None, '')
        ),
        '',
    )
    return f'time:{at}:{amount:.6f}:{network}:{anchor}'


def _stored_receipt_key(record: Any, index: int) -> str:
    '''Rebuild the identity for both new and pre-dedupe history rows.'''
    if isinstance(record, dict):
        source_key = str(record.get('source_key') or '').strip()
        if source_key:
            return source_key
        at = _canonical_timestamp(record.get('at'))
        if at:
            amount = _finite_amount(record.get('amount_usd'))
            network = str(record.get('network') or '').strip().lower()
            return f'time:{at}:{amount:.6f}:{network}:'
    return f'unidentified:{index}'


def _deduplicate_receipts(receipts: list[Any], limit: int) -> list[Any]:
    '''Keep the last copy of each receipt, then enforce the history cap.'''
    limit = max(1, int(limit))
    last_positions: dict[str, int] = {}
    for index, record in enumerate(receipts):
        last_positions[_stored_receipt_key(record, index)] = index
    ordered = [receipts[index] for index in sorted(last_positions.values())]
    return ordered[-limit:]


def _by_archetype(receipts: list[Any]) -> list[dict[str, Any]]:
    '''Total received while each archetype was the account's top performer.'''
    buckets: dict[str, dict[str, Any]] = {}
    for rec in receipts:
        if not isinstance(rec, dict):
            continue
        context = rec.get('context') or {}
        if not isinstance(context, dict):
            context = {}
        key = str(context.get('best_archetype') or 'unknown')
        slot = buckets.setdefault(key, {'archetype': key, 'count': 0, 'usd': 0.0})
        slot['count'] += 1
        slot['usd'] = round(slot['usd'] + _finite_amount(rec.get('amount_usd')), 6)
    return sorted(buckets.values(), key=lambda bucket: bucket['usd'], reverse=True)


def _by_tag(receipts: list[Any]) -> list[dict[str, Any]]:
    '''Total received while each winning tag was live; one count per receipt.'''
    buckets: dict[str, dict[str, Any]] = {}
    for rec in receipts:
        if not isinstance(rec, dict):
            continue
        context = rec.get('context') or {}
        if not isinstance(context, dict):
            continue
        amount = _finite_amount(rec.get('amount_usd'))
        for raw_tag in context.get('winning_tags') or []:
            tag = str(raw_tag).strip()
            if not tag:
                continue
            slot = buckets.setdefault(tag, {'tag': tag, 'count': 0, 'usd': 0.0})
            slot['count'] += 1
            slot['usd'] = round(slot['usd'] + amount, 6)
    return sorted(buckets.values(), key=lambda bucket: bucket['usd'], reverse=True)[:12]


def _refresh_book(book: dict[str, Any], receipts: list[Any], limit: int) -> None:
    defaults = _defaults()
    trimmed = _deduplicate_receipts(receipts, limit)
    last = trimmed[-1] if trimmed else {}

    book['receipts'] = trimmed
    book['receipt_count'] = len(trimmed)
    book['total_attributed_usd'] = round(
        sum(_finite_amount(item.get('amount_usd')) for item in trimmed if isinstance(item, dict)),
        6,
    )
    book['last_receipt_at'] = last.get('at') if isinstance(last, dict) else None
    book['by_archetype'] = _by_archetype(trimmed)
    book['by_tag'] = _by_tag(trimmed)
    book['note'] = str(book.get('note') or defaults['note'])


def _live_context(status: dict[str, Any]) -> dict[str, Any]:
    '''What was published and performing when money arrived.'''
    stats = status.get('article_stats') or {}
    interest = status.get('article_interest') or {}
    payout = status.get('payout') or {}
    return {
        'posts_live': _as_int(stats.get('count')),
        'total_views': _as_int(stats.get('total_views')),
        'best_title': str(stats.get('best_title') or '') or None,
        'best_url': str(stats.get('best_url') or '') or None,
        'best_views': _as_int(stats.get('best_views')),
        'winning_tags': [str(tag) for tag in (stats.get('winning_tags') or [])][:6],
        'best_archetype': interest.get('best_archetype') or None,
        'footer_network': payout.get('network') or None,
    }


def _defaults() -> dict[str, Any]:
    return {
        'receipts': [],
        'receipt_count': 0,
        'total_attributed_usd': 0.0,
        'last_receipt_at': None,
        'by_archetype': [],
        'by_tag': [],
        'note': (
            'Correlated context at receipt time. A TRC-20 transfer carries no '
            'memo, so this records which posts were live when money landed, '
            'not proof of which one earned it.'
        ),
    }


def record_receipt(status: dict[str, Any]) -> dict[str, Any] | None:
    '''Log one unique on-chain receipt and its correlated publishing context.'''
    try:
        cfg = config()
        enabled = cfg.get('enabled', True)
        if isinstance(enabled, str):
            enabled = enabled.strip().lower() not in {'0', 'false', 'no', 'off'}
        if not enabled:
            return None

        wallet = status.get('wallet')
        if not isinstance(wallet, dict):
            return None
        amount = _finite_amount(wallet.get('last_received_usd'))
        if amount <= 0:
            return None

        source_key = _wallet_receipt_key(wallet)
        if source_key is None:
            log.warning(
                '[attribution] receipt skipped: wallet supplied no transaction '
                'hash or stable last_received_at timestamp'
            )
            return None

        record: dict[str, Any] = {
            'at': _canonical_timestamp(wallet.get('last_received_at'))
                  or datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'amount_usd': round(amount, 6),
            'network': str(wallet.get('network') or '').strip() or None,
            'source_key': source_key,
            # Correlated, not proven: this is the state of the shop when the
            # till moved, not a receipt naming the item.
            'confidence': 'correlated',
            'context': _live_context(status),
        }

        book = status.setdefault('attribution', {})
        raw_receipts = book.get('receipts', [])
        receipts = raw_receipts if isinstance(raw_receipts, list) else []
        limit = max(1, int(cfg.get('history_limit') or DEFAULTS['history_limit']))
        receipts = _deduplicate_receipts(receipts, limit)

        known_keys = {
            _stored_receipt_key(existing, index)
            for index, existing in enumerate(receipts)
        }
        if source_key in known_keys:
            # The wallet snapshot is still reporting the previous transfer.
            # Refresh derived fields without appending it a second time.
            _refresh_book(book, receipts, limit)
            log.info('[attribution] duplicate receipt ignored: %s', source_key)
            return None

        receipts.append(record)
        _refresh_book(book, receipts, limit)

        context = record['context']
        log.info(
            '[attribution] recorded +$%.6f against %d live posts (best: %s)',
            amount,
            context['posts_live'],
            context['best_title'] or 'unknown',
        )
        return record
    except Exception as exc:  # pragma: no cover - defensive
        log.warning('[attribution] receipt not recorded: %s', exc)
        return None


def summary(status: dict[str, Any]) -> dict[str, Any]:
    '''Attribution state, with the empty case spelled out rather than implied.'''
    book = status.get('attribution')
    if not isinstance(book, dict):
        book = {}
    by_arch = book.get('by_archetype')
    if not isinstance(by_arch, list):
        by_arch = []
    top = by_arch[0] if by_arch and isinstance(by_arch[0], dict) else {}
    return {
        'receipt_count': _as_int(book.get('receipt_count')),
        'total_attributed_usd': _finite_amount(book.get('total_attributed_usd')),
        'last_receipt_at': book.get('last_receipt_at'),
        'top_archetype': top.get('archetype') or None,
    }