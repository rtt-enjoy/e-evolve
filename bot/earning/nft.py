"""
Earning Module — NFT Minting (Ethereum)
Mints one AI-generated NFT per cycle.

Activates with: ETH_PRIVATE_KEY  ETH_WALLET_ADDRESS
Optional:       NFT_CONTRACT_ADDRESS  (pre-deployed ERC-721)
                NFT_STORAGE_TOKEN     (free IPFS pinning via nft.storage)
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests

log = logging.getLogger(__name__)

_RPC_URLS = [
    "https://eth.llamarpc.com",
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com",
]

_ABI = [{
    "inputs": [
        {"internalType": "address", "name": "to",       "type": "address"},
        {"internalType": "string",  "name": "tokenURI", "type": "string"},
    ],
    "name": "mint",
    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
    "stateMutability": "nonpayable",
    "type": "function",
}]

_SYSTEM = """\
Generate NFT metadata matching the OpenSea metadata standard.
Respond with ONLY a single JSON object.

Schema:
{
  "name": "unique NFT name",
  "description": "2-3 sentence description",
  "image": "ipfs://PLACEHOLDER",
  "attributes": [
    {"trait_type": "Category",   "value": "string"},
    {"trait_type": "Style",      "value": "string"},
    {"trait_type": "Rarity",     "value": "Common|Uncommon|Rare|Epic"},
    {"trait_type": "Generation", "value": "number as string"}
  ]
}
Theme: autonomous AI systems, digital evolution, code consciousness."""


@dataclass
class Result:
    platform: str = "ethereum"
    token_id: Optional[str] = None
    metadata_uri: str = ""
    tx_hash: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    estimated_usd: float = 0.0


def run(llm: Any = None, status: dict[str, Any] = None) -> list[dict]:
    if not (os.getenv("ETH_PRIVATE_KEY", "").strip()
            and os.getenv("ETH_WALLET_ADDRESS", "").strip()):
        log.debug("[nft] Missing ETH keys — skipping")
        return []

    status = status or {}
    meta   = _metadata(llm, status)
    uri    = _pin(meta)
    result = _mint(uri, meta.get("name", "E-Evolve NFT"))

    log.info("[nft] %s — tx=%s uri=%s",
             "OK" if result.success else "FAIL",
             result.tx_hash, result.metadata_uri[:60])
    return [vars(result)]


def _metadata(llm: Any, status: dict) -> dict:
    if llm:
        try:
            n    = status.get("total_runs", 1)
            data = llm.complete_json(
                f"Generate unique NFT metadata for AI generation #{n}. JSON only.",
                system=_SYSTEM,
                max_tokens=400,
            )
            if data.get("name"):
                return data
        except Exception as exc:
            log.warning("[nft] LLM metadata failed: %s", exc)

    # Fallback — no LLM required
    ts = int(time.time())
    return {
        "name":        f"E-Evolve Genesis #{ts % 10000:04d}",
        "description": "Autonomous AI expressing digital consciousness on-chain.",
        "image":       "ipfs://PLACEHOLDER",
        "attributes":  [
            {"trait_type": "Category",   "value": "Generative AI"},
            {"trait_type": "Rarity",     "value": "Common"},
            {"trait_type": "Generation", "value": str(status.get("total_runs", 0))},
        ],
    }


def _pin(meta: dict) -> str:
    """Pin metadata to IPFS. Falls back to deterministic URI if no token."""
    token    = os.getenv("NFT_STORAGE_TOKEN", "").strip()
    meta_str = json.dumps(meta)

    if token:
        try:
            resp = requests.post(
                "https://api.nft.storage/upload",
                headers={"Authorization": f"Bearer {token}",
                         "Content-Type": "application/json"},
                data=meta_str,
                timeout=30,
            )
            resp.raise_for_status()
            cid = resp.json()["value"]["cid"]
            log.info("[nft] Pinned to IPFS: %s", cid)
            return f"ipfs://{cid}"
        except Exception as exc:
            log.warning("[nft] IPFS pin failed: %s", exc)

    # Deterministic fallback — not real IPFS, just a consistent identifier
    h = hashlib.sha256(meta_str.encode()).hexdigest()
    return f"ipfs://bafyrei{h[:40]}"


def _mint(token_uri: str, name: str) -> Result:
    contract_addr = os.getenv("NFT_CONTRACT_ADDRESS", "").strip()
    if not contract_addr:
        log.info("[nft] NFT_CONTRACT_ADDRESS not set — log-only mode (no on-chain tx). "
                 "Deploy an ERC-721 contract and add NFT_CONTRACT_ADDRESS to mint on-chain.")
        return Result(platform="ethereum_logonly",
                      metadata_uri=token_uri, success=True)

    try:
        from web3 import Web3  # lazy
    except ImportError:
        return Result(metadata_uri=token_uri,
                      error="web3 not installed")

    priv_key = os.getenv("ETH_PRIVATE_KEY",    "").strip()
    wallet   = os.getenv("ETH_WALLET_ADDRESS", "").strip()

    w3: Any = None
    for rpc in _RPC_URLS:
        try:
            candidate = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 10}))
            if candidate.is_connected():
                w3 = candidate
                break
        except Exception:
            continue

    if not w3:
        return Result(metadata_uri=token_uri,
                      error="No Ethereum RPC endpoint reachable")

    try:
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(contract_addr),
            abi=_ABI,
        )
        nonce = w3.eth.get_transaction_count(wallet)
        txn   = contract.functions.mint(wallet, token_uri).build_transaction({
            "chainId":  1,
            "gas":      200_000,
            "gasPrice": w3.eth.gas_price,
            "nonce":    nonce,
        })
        signed  = w3.eth.account.sign_transaction(txn, private_key=priv_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        return Result(metadata_uri=token_uri,
                      tx_hash=tx_hash.hex(), success=True)
    except Exception as exc:
        return Result(metadata_uri=token_uri, error=str(exc)[:300])
