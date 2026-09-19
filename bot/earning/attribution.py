'''Which published work earned the money.

Principle 5 of docs/passive-income-doctrine.md says to measure the funnel,
not the last stage, and it names this gap explicitly. Views are measured, but
what happens after a reader reaches the footer is not. That was acceptable
while the footer had never shipped; there was nothing downstream to measure.
It stops being acceptable the moment the receive path goes live, because the
first tip to arrive is also the first data point this project has ever had
about what people pay for, and an unattributed dollar teaches nothing.

The problem is that a TRC-20 transfer carries no memo tying it to an article.
Nobody tips through a tracked link; they read a post, copy an address, and
send from a wallet the bot cannot see. Exact per-post attribution is not
available, and pretending otherwise would be fabrication.

What is available is the publishing context at the moment money arrived:
which posts were live, which one was performing, and which archetype and
tags they carried. This module labels that evidence as correlated, never as
proof. A single receipt remains a single receipt, and repeated wallet polls
must not turn it into multiple dollars.

Design rules:

- Deterministic: no LLM call.
- Triggered by a real wallet receipt, never by a publish.
- Never raises: bookkeeping must not break a cycle.
- Idempotent: the same tx hash, or the same amount/time/network receipt, is
  recorded once even if the wallet poll repeats it.
'''
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from . import _shared

log = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
    'enabled': True,
    # Receipts are rare; keep a bounded history without discarding the only
    # evidence the project ever collects.
    'history_limit': 200,
}


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_amount(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _live_context(status: dict[str, Any]) -> dict[str, Any]:
    '''What was published and performing when money arrived.

    Read from snapshots the reach loop already wrote this cycle, so this costs
    no extra dev.to request. Every field is optional: a receipt during a dev.to
    outage still gets recorded, just with less context around it.
    '''
    stats = status.get('article_stats') or {}
    interest = status.get('article_interest') or {}
    payout = status.get('payout') or {}
    wallet = status.get('wallet') or {}
    if not isinstance(stats, dict):
        stats = {}
    if not isinstance(interest, dict):
        interest = {}
    if not isinstance(payout, dict):
        payout = {}
    if not isinstance(wallet, dict):
        wallet = {}

    tags = stats.get('winning_tags') or []
    if not isinstance(tags, list):
        tags = [tags]

    return {
        'posts_live': _as_int(stats.get('count')),
        'total_views': _as_int(stats.get('total_views')),
        'best_title': str(stats.get('best_title') or '') or None,
        'best_url': str(stats.get('best_url') or '') or None,
        'best_views': _as_int(stats.get('best_views')),
        'winning_tags': [str(tag) for tag in tags if str(tag).strip()][:6],
        'best_archetype': str(interest.get('best_archetype') or '') or None,
        'footer_network': (
            str(payout.get('network') or wallet.get('network') or '').strip()
            or None
        ),
        'footer_asset': (
            str(payout.get('asset') or wallet.get('asset') or '').strip()
            or None
        ),
    }


def _defaults() -> dict[str, Any]:
    return {
        'receipts': [],
        'receipt_count': 0,
        'total_attributed_usd': 0.0,
        'last_receipt_at': None,
        'by_archetype': [],
        'by_tag': [],
        # Says what this record is, so a later reader does not mistake it for
        # per-post tracking the chain cannot provide.
        'note': (
            'Correlated context at receipt time. A TRC-20 transfer carries no '
            'memo, so this records which posts were live when money landed, '
            'not proof of which one earned it.'
        ),
    }


def _newer_stamp(candidate: str, current: Any) -> str:
    candidate_dt = _shared.parse_dt(candidate)
    current_dt = _shared.parse_dt(current)
    if candidate_dt is None:
        return candidate
    if current_dt is None:
        return candidate
    return candidate if candidate_dt >= current_dt else str(current or '')


def _current_receipt_key(
    wallet: dict[str, Any],
    amount: float,
    at: str,
    network: str | None,
) -> str:
    tx_hash = next(
        (
            wallet.get(name)
            for name in (
                'last_received_tx',
                'last_received_tx_hash',
                'last_received_hash',
                'tx_hash',
            )
            if wallet.get(name)
        ),
        None,
    )
    if tx_hash:
        return f'tx:{str(tx_hash).strip()}'

    network_label = network or 'unknown'
    return f'{network_label}|{amount:.6f}|{at}'


def _record_receipt_key(record: dict[str, Any]) -> str | None:
    tx_hash = (
        record.get('tx_hash')
        or record.get('last_received_tx')
        or record.get('last_received_tx_hash')
        or record.get('last_received_hash')
    )
    if tx_hash:
        return f'tx:{str(tx_hash).strip()}'

    stored_key = record.get('receipt_key')
    if stored_key:
        return str(stored_key)

    amount = record.get('amount_usd')
    at = record.get('at') or record.get('last_received_at')
    network = record.get('network') or 'unknown'
    if amount is None or at is None:
        return None

    try:
        amount_text = f'{float(amount):.6f}'
    except (TypeError, ValueError):
        return None
    return f'{network}|{amount_text}|{str(at).strip()}'


def record_receipt(status: dict[str, Any]) -> dict[str, Any] | None:
    '''Log the publishing context for a real on-chain receipt.

    Returns the new record, or None when no new money arrived this cycle. A
    repeated wallet poll for the same transaction is intentionally ignored;
    the wallet endpoint is a observation point, not a new receipt producer.
    Called from the status phase after the wallet is polled, so the amount it
    reports is the one the chain confirmed -- this function never computes a
    dollar figure of its own.
    '''
    if not isinstance(status, dict):
        return None

    try:
        cfg = config()
        if not cfg.get('enabled'):
            return None

        wallet = status.get('wallet') or {}
        if not isinstance(wallet, dict):
            wallet = {}

        amount = _safe_amount(wallet.get('last_received_usd'))
        if amount <= 0:
            return None

        at_raw = wallet.get('last_received_at')
        at = str(at_raw).strip() or datetime.now(timezone.utc).isoformat()
        network_raw = wallet.get('network')
        network = str(network_raw).strip() or None

        tx_hash = next(
            (
                wallet.get(name)
                for name in (
                    'last_received_tx',
                    'last_received_tx_hash',
                    'last_received_hash',
                    'tx_hash',
                )
                if wallet.get(name)
            ),
            None,
        )
        key = _current_receipt_key(wallet, amount, at, network)

        book = status.get('attribution')
        if not isinstance(book, dict):
            book = _defaults()
            status['attribution'] = book

        receipts = book.get('receipts')
        if not isinstance(receipts, list):
            receipts = []
            book['receipts'] = receipts

        seen = {
            _record_receipt_key(record)
            for record in receipts
            if isinstance(record, dict)
        }
        if key in seen:
            log.info(
                '[attribution] duplicate receipt ignored: %s',
                str(tx_hash or f'{network or "unknown"}|{amount:.6f}|{at}'),
            )
            return None

        record = {
            'at': at,
            'amount_usd': round(amount, 6),
            'network': network,
            'tx_hash': str(tx_hash).strip() if tx_hash else None,
            # Correlated, not proven: this is the state of the shop when the
            # till moved, not a receipt naming the item.
            'confidence': 'correlated',
            'context': _live_context(status),
        }

        receipts.append(record)
        limit = int(cfg.get('history_limit') or DEFAULTS['history_limit'])
        if len(receipts) > limit:
            del receipts[: len(receipts) - limit]

        book['receipt_count'] = len(receipts)
        book['total_attributed_usd'] = round(
            sum(_safe_amount(record.get('amount_usd')) for record in receipts),
            6,
        )
        book['last_receipt_at'] = _newer_stamp(
            record['at'], book.get('last_receipt_at')
        )
        book['by_archetype'] = _by_archetype(receipts)
        book['by_tag'] = _by_tag(receipts)
        book.setdefault('note', _defaults()['note'])

        log.info(
            '[attribution] recorded +$%.6f against %d live posts (best: %s)',
            amount,
            record['context']['posts_live'],
            record['context']['best_title'] or 'unknown',
        )
        return record
    except Exception as exc:  # pragma: no cover - defensive
        log.warning('[attribution] receipt not recorded: %s', exc)
        return None


def _by_archetype(receipts: list[Any]) -> list[dict[str, Any]]:
    '''Total received while each archetype was the account's top performer.

    count rides along with every total: one receipt is not a trend, and
    showing the sample size is the only thing that stops a reader treating it
    as one.
    '''
    buckets: dict[str, dict[str, Any]] = {}
    for record in receipts:
        if not isinstance(record, dict):
            continue
        context = record.get('context') or {}
        if not isinstance(context, dict):
            context = {}
        key = str(context.get('best_archetype') or '') or 'unknown'
        slot = buckets.setdefault(
            key,
            {'archetype': key, 'count': 0, 'usd': 0.0},
        )
        slot['count'] += 1
        slot['usd'] = round(
            slot['usd'] + _safe_amount(record.get('amount_usd')), 6
        )
    return sorted(buckets.values(), key=lambda row: row['usd'], reverse=True)


def _by_tag(receipts: list[Any]) -> list[dict[str, Any]]:
    '''Same, per winning tag. A tag counts once per receipt it was live for.'''
    buckets: dict[str, dict[str, Any]] = {}
    for record in receipts:
        if not isinstance(record, dict):
            continue
        amount = _safe_amount(record.get('amount_usd'))
        context = record.get('context') or {}
        if not isinstance(context, dict):
            context = {}
        tags = context.get('winning_tags') or []
        if isinstance(tags, str):
            tags = [tags]
        for tag in tags:
            tag_text = str(tag).strip()
            if not tag_text:
                continue
            slot = buckets.setdefault(
                tag_text,
                {'tag': tag_text, 'count': 0, 'usd': 0.0},
            )
            slot['count'] += 1
            slot['usd'] = round(slot['usd'] + amount, 6)
    return sorted(buckets.values(), key=lambda row: row['usd'], reverse=True)[:12]


def summary(status: dict[str, Any]) -> dict[str, Any]:
    '''Attribution state, with the empty case spelled out rather than implied.'''
    book = status.get('attribution') or _defaults()
    if not isinstance(book, dict):
        book = _defaults()

    receipts = book.get('receipts') or []
    if not isinstance(receipts, list):
        receipts = []
    receipts = [record for record in receipts if isinstance(record, dict)]
    by_archetype = _by_archetype(receipts)
    by_tag = _by_tag(receipts)

    try:
        total = float(book.get('total_attributed_usd') or 0.0)
    except (TypeError, ValueError):
        total = sum(_safe_amount(record.get('amount_usd')) for record in receipts)

    return {
        'receipt_count': _as_int(book.get('receipt_count'), len(receipts)),
        'total_attributed_usd': total,
        'last_receipt_at': book.get('last_receipt_at'),
        'top_archetype': (
            by_archetype[0].get('archetype') if by_archetype else None
        ),
        'top_tag': by_tag[0].get('tag') if by_tag else None,
        'networks': sorted(
            {
                str(record.get('network'))
                for record in receipts
                if record.get('network')
            }
        ),
        'by_archetype': by_archetype,
        'by_tag': by_tag,
    }