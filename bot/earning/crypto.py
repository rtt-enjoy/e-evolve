"""
Earning Module — Crypto Trading (Binance)
Conservative spot trading using dual-EMA momentum signals.

Activates with: BINANCE_API_KEY  BINANCE_SECRET_KEY
Risk: RISK_PCT of free USDT per trade (default 2 %).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

log = logging.getLogger(__name__)

RISK_PCT       = 0.02    # 2 % of available USDT per trade
MIN_USDT       = 10.0    # don't trade below this balance
SYMBOLS        = ["BTCUSDT", "ETHUSDT"]


@dataclass
class Trade:
    platform: str
    symbol: str
    side: str              # BUY | SELL | HOLD | ERROR
    qty: float = 0.0
    price: float = 0.0
    value_usd: float = 0.0
    success: bool = True
    error: Optional[str] = None
    pnl_usd: float = 0.0


def run(llm: Any = None, status: dict[str, Any] = None) -> list[dict]:
    if not (os.getenv("BINANCE_API_KEY", "").strip()
            and os.getenv("BINANCE_SECRET_KEY", "").strip()):
        return []

    results = _run_binance()
    for r in results:
        if r.success and r.side not in ("HOLD", "ERROR"):
            log.info("[crypto] %s %s @ %.2f  value=$%.2f",
                     r.side, r.symbol, r.price, r.value_usd)
        elif not r.success:
            log.warning("[crypto] %s error: %s", r.symbol, r.error)
    return [vars(r) for r in results]


def _run_binance() -> list[Trade]:
    try:
        from binance.client import Client
    except ImportError:
        log.warning("[binance] python-binance not installed")
        return []

    key    = os.getenv("BINANCE_API_KEY",    "").strip()
    secret = os.getenv("BINANCE_SECRET_KEY", "").strip()

    try:
        client  = Client(key, secret)
        account = client.get_account()
    except Exception as exc:
        return [Trade("binance", "ACCOUNT", "ERROR",
                      success=False, error=str(exc)[:200])]

    trades: list[Trade] = []

    for sym in SYMBOLS:
        base = sym.replace("USDT", "")
        try:
            usdt = _bal(account, "USDT")
            base_bal = _bal(account, base)

            if usdt < MIN_USDT and base_bal == 0:
                trades.append(Trade("binance", sym, "HOLD"))
                continue

            klines = client.get_klines(
                symbol=sym,
                interval=Client.KLINE_INTERVAL_1HOUR,
                limit=26,
            )
            closes = [float(k[4]) for k in klines]
            price  = closes[-1]
            signal = _signal(closes)
            log.info("[binance] %s signal=%s price=%.2f", sym, signal, price)

            if signal == "BUY" and usdt >= MIN_USDT:
                val = usdt * RISK_PCT
                qty = _round_qty(val / price, sym)
                if qty > 0:
                    client.order_market_buy(symbol=sym, quantity=qty)
                    trades.append(Trade("binance", sym, "BUY",
                                        qty=qty, price=price, value_usd=val))
                    continue

            elif signal == "SELL" and base_bal > 0:
                qty = _round_qty(base_bal * 0.5, sym)
                if qty > 0:
                    client.order_market_sell(symbol=sym, quantity=qty)
                    trades.append(Trade("binance", sym, "SELL",
                                        qty=qty, price=price,
                                        value_usd=qty * price))
                    continue

            trades.append(Trade("binance", sym, "HOLD", price=price))

        except Exception as exc:
            trades.append(Trade("binance", sym, "ERROR",
                                success=False, error=str(exc)[:200]))

    return trades


# ── Helpers ───────────────────────────────────────────────────────────────────

def _bal(account: dict, asset: str) -> float:
    for b in account.get("balances", []):
        if b["asset"] == asset:
            return float(b["free"])
    return 0.0


def _signal(closes: list[float]) -> str:
    """Dual-EMA crossover: EMA-6 vs EMA-24 on 1-hour candles."""
    if len(closes) < 26:
        return "HOLD"

    def ema(data: list[float], period: int) -> float:
        k, v = 2 / (period + 1), data[0]
        for x in data[1:]:
            v = x * k + v * (1 - k)
        return v

    fast_now  = ema(closes[-6:],   6)
    slow_now  = ema(closes[-24:], 24)
    fast_prev = ema(closes[-7:-1], 6)
    slow_prev = ema(closes[-25:-1], 24)

    if fast_prev <= slow_prev and fast_now > slow_now:
        return "BUY"
    if fast_prev >= slow_prev and fast_now < slow_now:
        return "SELL"
    return "HOLD"


def _round_qty(qty: float, sym: str) -> float:
    return round(qty, 5) if "BTC" in sym else round(qty, 4)
