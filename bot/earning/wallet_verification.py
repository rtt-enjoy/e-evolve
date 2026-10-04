'''"""Validate the USDT wallet address used for payouts.

The script checks that the USDT_WALLET_ADDRESS environment variable is set
and matches the TRC-20 address pattern (starts with T, 33-42 base58 chars).
It logs a warning if the address is missing or malformed.
"""
import os
import re
import logging
import sys

log = logging.getLogger("wallet_verification")

TRC20_ADDRESS_PATTERN = re.compile(r"^T[1-5A-HJ-NP-Za-km-z]{33,41}$")

def validate():
    address = os.getenv("USDT_WALLET_ADDRESS")
    if not address:
        log.warning("USDT_WALLET_ADDRESS environment variable is not set.")
        return False
    if not TRC20_ADDRESS_PATTERN.match(address):
        log.warning("USDT_WALLET_ADDRESS '%s' does not match TRC-20 address pattern.", address)
        return False
    log.info("USDT_WALLET_ADDRESS '%s' is valid.", address)
    return True

if __name__ == "__main__":
    if not validate():
        sys.exit(1)
'''