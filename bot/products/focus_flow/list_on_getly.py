#!/usr/bin/env python3
"""
Script to guide the owner through listing the FocusFlow browser extension on Getly.

This script does not perform any external API calls; it prints the steps and
a checklist so the owner can manually complete the listing process.
"""

import os
import zipfile
import sys
from pathlib import Path

FOCUS_FLOW_DIR = Path(__file__).parent
MANIFEST = FOCUS_FLOW_DIR / "manifest.json"
POPUP = FOCUS_FLOW_DIR / "popup.html"
ZIP_NAME = "focusflow.zip"
GETLY_URL = "https://www.getly.store/sell/crypto"

def main():
    print("=== FocusFlow Extension Listing Guide ===\n")
    print(f"1. Ensure the extension files are ready in: {FOCUS_FLOW_DIR}")
    if not MANIFEST.exists():
        print(f"   ERROR: {MANIFEST} not found.")
        sys.exit(1)
    if not POPUP.exists():
        print(f"   ERROR: {POPUP} not found.")
        sys.exit(1)

    # Create zip
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(MANIFEST, arcname=MANIFEST.name)
        zf.write(POPUP, arcname=POPUP.name)
    print(f"2. Created zip archive: {ZIP_NAME}")

    print(f"3. Visit {GETLY_URL} and create a free seller account.")
    print("   - No ID verification required for crypto payouts.")
    print("   - Use the same Tron wallet address already published in the repo.")

    print("4. In Getly, upload the zip file and set a one-time license price.")
    print("   - Set payout destination to the validated Tron address (USDT_WALLET_ADDRESS).")
    print("   - Choose a price that matches your ask (e.g., $5.00).")

    print("5. Verify the listing is live and copy the product URL.")
    print("   - The extension will be available for download via the Getly storefront.")
    print("   - The wallet ask is already embedded in the README and --help output.")

    print("\nChecklist:")
    print("[ ] manifest.json and popup.html are present")
    print("[ ] focusflow.zip created")
    print("[ ] Getly account created")
    print("[ ] Extension uploaded with correct payout address")
    print("[ ] Price set and listing published")
    print("[ ] Product URL noted for documentation")

if __name__ == "__main__":
    main()