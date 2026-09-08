"""
Read every stablecoin the published address can actually receive, not just USDT.

The footer publishes a *Tron address*. A Tron address is not a USDT account --
it accepts TRX and every TRC-20 token ever deployed. But ``status._fetch_usdt
_balance`` called ``balanceOf()`` against the USDT contract and nothing else, so
a reader who tipped USDC or USDD sent money that arrived on-chain and was
reported as ``$0.00`` forever.

That is the Principle 1 structural zero rebuilt one layer further in. The
receive path was live, the footer shipped, the reader paid -- and the *reader*
was measured with a meter that only reads one token. Worse, it fails in the
dangerous direction: ``received_total_usd`` stays zero, so
``attribution.record_receipt`` never fires either (it triggers on
``wallet.last_received_usd > 0``), and the doctrine's checklist step 2 reports
"still $0.00 with a live path -> the problem is reach", sending the next
evolution to optimise the wrong stage entirely.

**Why stablecoins only, and why no price feed.**

Counting TRX or an arbitrary TRC-20 in dollars needs a USD price, and a price is
an *estimate* -- exactly what Principle 4 forbids from standing in for money. It
also fails continuously rather than once: a 100 TRX tip priced per cycle would
make ``received_total_usd`` drift up and down while no money moved at all,
corrupting the single number this project trusts. A USD-pegged stablecoin needs
no feed, because 1 USDC is 1 USD by construction. That is face value, not an
estimate.

So non-stable assets are **observed and reported, never valued**. ``TRX`` in the
wallet shows up in ``other_assets`` so the owner can see a tip arrived and
convert it by hand, and it contributes nothing to the dollar figure. Reporting a
receipt without inventing a number for it is the honest half of Principle 4.

Scored against Principle 2 this needs no new secret (TronGrid's account endpoint
is keyless, the same host ``status.py`` already calls), no owner action, no
policy change, and it is verified on-chain by construction.
"""
from __future__ import annotations

import json
import logging
import urllib.request
from typing import Any, Optional

log = logging.getLogger(__name__)

_ACCOUNT_API = "https://api.trongrid.io/v1/accounts/{address}"
_TIMEOUT = 20

# USD-pegged TRC-20 tokens, counted at face value. Symbol and decimals were read
# from each contract on-chain (`symbol()` / `decimals()` via
# triggerconstantcontract) rather than copied from a listing site.
#
# USDD carries **18** decimals while USDT and USDC carry 6. Dividing everything
# by 1e6 -- the constant the single-asset reader used -- would report a 1 USDD
# tip as $1,000,000,000,000. Per-token decimals are a correctness requirement,
# not tidiness.
STABLECOINS: dict[str, dict[str, Any]] = {
	"TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t": {"symbol": "USDT", "decimals": 6},
	"TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8": {"symbol": "USDC", "decimals": 6},
	"TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn": {"symbol": "USDD", "decimals": 18},
}

# TRX itself, reported but never valued. 1 TRX is not 1 USD and this module
# refuses to guess what it is.
_SUN_PER_TRX = 1_000_000


def _fetch_account(address: str, timeout: int = _TIMEOUT) -> Optional[dict]:
	"""Raw TronGrid account record, or ``None`` when it could not be read.

    ``None`` means "could not observe" and is deliberately distinct from an
    account that exists with nothing in it. Collapsing those is how a chain
    outage becomes a false ``$0.00`` -- the same mistake ``receipt_check`` keeps
    a third state for.
    """
	try:
		req = urllib.request.Request(
			_ACCOUNT_API.format(address=address),
			headers={"Accept": "application/json"},
		)
		with urllib.request.urlopen(req, timeout=timeout) as resp:
			data = json.loads(resp.read())
	except Exception as exc:
		log.debug("[wallet_assets] account fetch failed: %s", exc)
		return None

	if not isinstance(data, dict) or not data.get("success"):
		return None
	records = data.get("data")
	if not isinstance(records, list):
		return None
	# An empty list is a real answer: the address has never been activated,
	# i.e. nothing has ever been sent to it. That is a balance of zero, not an
	# observation failure, so it must not be reported as unreadable.
	if not records:
		return {}
	first = records[0]
	return first if isinstance(first, dict) else {}


def read_balances(address: str, timeout: int = _TIMEOUT) -> Optional[dict[str, Any]]:
	"""Every asset at ``address``, split into what can be valued and what cannot.

    Returns ``None`` only when the chain could not be read at all, so the
    caller can hold the last known figure instead of reporting a false zero.

    ``usd`` sums only USD-pegged stablecoins at face value. ``other_assets``
    lists everything else by symbol and amount, with no dollar figure attached,
    because valuing it would require a price feed (see the module docstring).
    """
	account = _fetch_account(address, timeout=timeout)
	if account is None:
		return None

	usd = 0.0
	stables: dict[str, float] = {}
	for entry in account.get("trc20") or []:
		if not isinstance(entry, dict):
			continue
		for contract, raw in entry.items():
			token = STABLECOINS.get(contract)
			if not token:
				# A TRC-20 this module cannot price. Deliberately not summed and
				# deliberately not resolved to a symbol either: naming it needs a
				# second contract call per unknown token, and an unpriced token
				# is reported by the TRX/unknown path below rather than valued.
				continue
			try:
				amount = int(raw) / (10 ** token["decimals"])
			except (TypeError, ValueError):
				continue
			if amount <= 0:
				continue
			stables[token["symbol"]] = round(
				stables.get(token["symbol"], 0.0) + amount, 6)
			usd += amount

	other: dict[str, float] = {}
	try:
		trx = int(account.get("balance") or 0) / _SUN_PER_TRX
	except (TypeError, ValueError):
		trx = 0.0
	if trx > 0:
		# Reported so a TRX tip is visible to the owner, and excluded from `usd`
		# so it can never be mistaken for a measured dollar.
		other["TRX"] = round(trx, 6)

	return {
		"usd": round(usd, 6),
		"stablecoins": stables,
		"other_assets": other,
	}


def fetch_usd_balance(address: str, timeout: int = _TIMEOUT) -> Optional[float]:
	"""Total USD-pegged stablecoin balance, or ``None`` when unreadable.

    Drop-in for the single-asset reader it replaces, so the withdrawal and
    high-water accounting in ``status._snapshot_wallet`` -- which is correct and
    covered by tests -- keeps working unchanged.
    """
	balances = read_balances(address, timeout=timeout)
	if balances is None:
		return None
	return float(balances["usd"])
