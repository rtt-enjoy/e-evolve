"""
The link from reach to the wallet.

This project had two working halves that were never connected. One publishes
articles that people actually read -- 1838 views across 10 posts at the time
this was written. The other polls a USDT receive address and reports the
balance. Nothing in the published output ever mentioned that the address
existed, so lifetime earnings after 1754 cycles were $0.00 and the comment in
``devto.publish`` had settled for "publishing is reach, not revenue".

dev.to pays nothing, which is true. But dev.to *readers* can pay, and a receive
address printed in the article is the only channel that needs no payment
processor, no platform account, no new secret, and no owner action between the
reader deciding to give something and the money arriving. That makes it the one
monetization path this stack can actually run unattended, which is why it is
the first one built.

What this is not: it is not social posting, trading, minting, or a payout. It
adds text to an article, and article publishing is explicitly allowed policy.
The bot never sends funds, never asks for a specific amount, and never touches
a key -- ``USDT_WALLET_ADDRESS`` is a *receive* address and reading it is all
this module does.

Two rules hold this module together:

- **No LLM call, ever.** The footer is a template. A model asked to write a
  payment footer can transpose a character in an address, and money sent to a
  transposed address is gone. Determinism here is a correctness requirement,
  not a cost saving.
- **A malformed address is never published.** This is the only irreversible
  failure mode in the feature, so the address passes a real base58check or
  EIP-55 validation before it reaches a reader, not a regex that a truncated
  env var would satisfy. When validation fails the footer is omitted and the
  article publishes without it: a post with no footer earns nothing, but a
  post with a broken address costs a reader real money.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from typing import Any, Optional

from . import _shared

log = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
	# Opt-in. An owner who has not read the footer text should not discover it
	# on their own byline, so this ships false and the owner turns it on.
	"enabled": False,
	"address_env": "USDT_WALLET_ADDRESS",
	# The heading readers see. Deliberately plain: "Support this work" asks,
	# where "Donate now" demands, and this audience scrolls past a demand.
	"heading": "Support this work",
	"note": (
		"These write-ups are researched and published with no paywall, "
		"sponsor, or tracking. If one saved you an afternoon, a small USDT tip "
		"keeps them coming."
	),
	# No suggested amount. Naming a figure reads as a price for something the
	# reader has already been given for free, and it caps what a generous
	# reader would otherwise send.
	"show_network": True,
}

_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def config() -> dict[str, Any]:
	"""This module's slice of config/strategy.json, read at call time."""
	return _shared.load_config("payout", DEFAULTS)


def _b58decode(value: str) -> Optional[bytes]:
	"""Decode base58 to raw bytes. None when a character is outside the alphabet.

    Written out rather than pulled from a dependency: ``requirements.txt`` is
    installed on every Actions run, and a base58 library is not worth a wheel
    download for twenty lines that cannot change.
    """
	num = 0
	for char in value:
		index = _BASE58_ALPHABET.find(char)
		if index < 0:
			return None
		num = num * 58 + index
	raw = num.to_bytes((num.bit_length() + 7) // 8, "big")
	# Leading '1's are leading zero bytes and are lost by the integer maths.
	pad = len(value) - len(value.lstrip("1"))
	return b"\x00" * pad + raw


def valid_tron_address(address: str) -> bool:
	"""True for a checksum-valid TRC-20 (Tron) address.

    The checksum is the point. A regex on ``^T[1-9A-HJ-NP-Za-km-z]{33}$`` also
    accepts an address with two characters swapped, and that address belongs to
    nobody -- USDT sent to it is burned. Tron encodes a double-SHA256 checksum
    in the last four bytes precisely so a typo is detectable, so we check it.
    """
	if not address.startswith("T") or len(address) != 34:
		return False
	raw = _b58decode(address)
	if raw is None or len(raw) != 25:
		return False
	body, checksum = raw[:21], raw[21:]
	if body[0] != 0x41:          # Tron mainnet version byte
		return False
	digest = hashlib.sha256(hashlib.sha256(body).digest()).digest()[:4]
	return digest == checksum


_KECCAK_ROUND_CONSTANTS = (
	0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
	0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
	0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
	0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
	0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
	0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
)
_KECCAK_ROTATIONS = (
	(0, 36, 3, 41, 18), (1, 44, 10, 45, 2), (62, 6, 43, 15, 61),
	(28, 55, 25, 21, 56), (27, 20, 39, 8, 14),
)


def keccak256(data: bytes) -> bytes:
	"""Keccak-256 as Ethereum uses it, in the standard library only.

    ``hashlib.sha3_256`` is *not* this. NIST changed the padding byte between
    Keccak's submission and the final SHA-3 standard, so the two produce
    different digests for the same input. EIP-55 predates the standard and
    specifies original Keccak with the 0x01 pad, which is why an EIP-55 check
    built on ``sha3_256`` silently rejects every valid checksummed address --
    it did here, caught by testing against a known-good address from the EIP
    itself before this shipped.

    Implemented rather than pulled in as a dependency: ``pycryptodome`` or
    ``eth-utils`` is a wheel on every Actions run to verify one address format
    the owner does not currently use. The permutation is frozen by the spec, so
    this code has no upgrade path to track.
    """
	rate = 136                                  # 1088-bit rate for 256-bit output
	state = [[0] * 5 for _ in range(5)]

	padded = bytearray(data)
	padded.append(0x01)                         # Keccak pad, not SHA-3's 0x06
	while len(padded) % rate != 0:
		padded.append(0x00)
	padded[-1] |= 0x80

	def absorb(block: bytes) -> None:
		for i in range(rate // 8):
			word = int.from_bytes(block[i * 8:i * 8 + 8], "little")
			state[i % 5][i // 5] ^= word
		permute()

	def permute() -> None:
		mask = (1 << 64) - 1
		for rc in _KECCAK_ROUND_CONSTANTS:
			# theta
			c = [state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4]
				 for x in range(5)]
			d = [c[(x - 1) % 5] ^ (((c[(x + 1) % 5] << 1) | (c[(x + 1) % 5] >> 63)) & mask)
				 for x in range(5)]
			for x in range(5):
				for y in range(5):
					state[x][y] ^= d[x]
			# rho + pi
			b = [[0] * 5 for _ in range(5)]
			for x in range(5):
				for y in range(5):
					r = _KECCAK_ROTATIONS[x][y]
					v = state[x][y]
					b[y][(2 * x + 3 * y) % 5] = ((v << r) | (v >> (64 - r))) & mask if r else v
			# chi
			for x in range(5):
				for y in range(5):
					state[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y] & mask) & b[(x + 2) % 5][y])
			# iota
			state[0][0] ^= rc

	for offset in range(0, len(padded), rate):
		absorb(bytes(padded[offset:offset + rate]))

	out = bytearray()
	for i in range(4):                          # 4 lanes = 32 bytes
		out += state[i % 5][i // 5].to_bytes(8, "little")
	return bytes(out)


def valid_eth_address(address: str) -> bool:
	"""True for a well-formed ERC-20 address, checksum-verified when mixed-case.

    An all-lower or all-upper address carries no checksum to verify, so shape
    is all there is. A mixed-case one is EIP-55 encoded and the capitalisation
    *is* the checksum, so it gets verified -- which is the case that catches a
    hand-copied address with a dropped or swapped character.
    """
	if not re.fullmatch(r"0x[0-9a-fA-F]{40}", address):
		return False
	body = address[2:]
	if body == body.lower() or body == body.upper():
		return True
	digest = keccak256(body.lower().encode()).hex()
	for char, nibble in zip(body, digest):
		if char.isdigit():
			continue
		if char.isupper() != (int(nibble, 16) >= 8):
			return False
	return True


def resolve_address(cfg: dict[str, Any] | None = None) -> tuple[str, str]:
	"""Return ``(address, network)`` for the configured receive address.

    ``("", "")`` when the footer must be omitted: not set, or not
    checksum-valid. Every rejection is logged with a *masked* address -- a
    receive address is not a secret, but the logs are public build output and
    there is no reason to hand a scraper a clean copy.
    """
	cfg = cfg or config()
	env_name = str(cfg.get("address_env") or "USDT_WALLET_ADDRESS").strip()
	address = os.getenv(env_name, "").strip() if env_name else ""
	if not address:
		return "", ""

	if valid_tron_address(address):
		return address, "TRC-20 (Tron)"
	if valid_eth_address(address):
		return address, "ERC-20 (Ethereum)"

	# Reaching here means the owner set something that is not a spendable
	# address. Publishing it would send a reader's money nowhere, so the footer
	# is dropped and the article goes out without it.
	log.warning(
		"[payout] %s failed address validation (%s) -- footer omitted",
		env_name, mask(address),
	)
	return "", ""


def mask(address: str) -> str:
	"""``TFTNsf...9KbY``-style short form for logs and status."""
	if len(address) <= 10:
		return "…"
	return f"{address[:6]}…{address[-4:]}"


_HEADING_RE = re.compile(r"^#{2,3}\s*support this work\s*$", re.IGNORECASE | re.MULTILINE)


def has_footer(body: str) -> bool:
	"""True when a support footer is already present.

    Guards against a double footer on the paths that revise a body after the
    footer was added, and against the model spontaneously writing one.
    """
	return bool(_HEADING_RE.search(body or ""))


def footer(cfg: dict[str, Any] | None = None) -> str:
	"""The markdown footer, or '' when it must not be published."""
	cfg = cfg or config()
	if not cfg.get("enabled"):
		return ""
	address, network = resolve_address(cfg)
	if not address:
		return ""

	heading = str(cfg.get("heading") or DEFAULTS["heading"]).strip()
	note = str(cfg.get("note") or DEFAULTS["note"]).strip()
	label = f"USDT · {network}" if cfg.get("show_network", True) else "USDT"

	# The address goes in a fenced block, not inline prose. dev.to leaves a
	# fence untouched, while inline text can be line-wrapped or smart-quoted by
	# a renderer, and a wrapped address is a mistyped address. A fence also
	# gives the reader a copy button.
	return (
		f"\n\n## {heading}\n\n"
		f"{note}\n\n"
		f"{label}\n\n"
		"```\n"
		f"{address}\n"
		"```\n"
	)


def add_footer(article: dict, cfg: dict[str, Any] | None = None) -> dict:
	"""Append the support footer to ``article['body_markdown']``.

    Returns the article unchanged when the footer is disabled, unconfigured,
    invalid, or already present. Never raises: a footer is an enhancement, and
    losing the day's article over it would trade real reach for nothing.
    """
	try:
		block = footer(cfg)
		if not block:
			return article
		body = str(article.get("body_markdown", ""))
		if has_footer(body):
			return article
		article["body_markdown"] = body.rstrip() + block
	except Exception as exc:                       # pragma: no cover - defensive
		log.warning("[payout] footer skipped: %s", exc)
	return article


def status_snapshot(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
	"""What the owner needs to see to know whether the earning path is live.

    ``$0.00`` lifetime earnings looks identical whether the footer is running
    and nobody has tipped yet, or the footer was never published at all. Those
    need different responses from the owner, so the difference is recorded
    rather than left to be inferred from a zero.
    """
	cfg = cfg or config()
	enabled = bool(cfg.get("enabled"))
	env_name = str(cfg.get("address_env") or "USDT_WALLET_ADDRESS").strip()
	raw = os.getenv(env_name, "").strip() if env_name else ""
	address, network = resolve_address(cfg) if enabled else ("", "")
	if not enabled:
		reason = "disabled in config/strategy.json (payout.enabled)"
	elif not raw:
		reason = f"{env_name} is not set"
	elif not address:
		reason = f"{env_name} is not a checksum-valid USDT address"
	else:
		reason = None
	return {
		"enabled":        enabled,
		"live":           bool(address),
		"network":        network or None,
		"address_masked": mask(address) if address else None,
		"blocked_reason": reason,
	}


def public_snapshot(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
	"""The receive address in the form the public dashboard can actually use.

    This is the one place the *full* address is deliberately published, and it
    is separate from ``status_snapshot`` on purpose. That one is a diagnostic
    and stays masked, because a masked address is all the owner needs to
    recognise which wallet is configured. A dashboard tip box is not a
    diagnostic: a reader cannot pay a masked address, so publishing
    ``TFTNsf…9KbY`` there would rebuild the exact structural zero this module
    exists to close -- a receive path that looks present and cannot receive.

    The address is only exposed when ``footer()`` would already publish that
    same address to dev.to readers. So this never widens exposure: it puts the
    address where the project's own audience already sees it, on a page the
    owner already serves. It returns ``{}`` when the footer is not shipping,
    which keeps the two surfaces from disagreeing about whether the path is
    live.
    """
	cfg = cfg or config()
	if not cfg.get("enabled"):
		return {}
	address, network = resolve_address(cfg)
	if not address:
		return {}
	return {
		"address": address,
		"network": network,
		"heading": str(cfg.get("heading") or DEFAULTS["heading"]).strip(),
		"note": str(cfg.get("note") or DEFAULTS["note"]).strip(),
		"asset": "USDT",
	}
