'''"""Generate a concise daily summary of earnings and backfill status.

The script reads `status.json` (the current status file) and writes a human‑readable
summary to `docs/summary.txt`. It can be run manually or scheduled via cron.
"""
import json
import os
from pathlib import Path

STATUS_FILE = Path("status.json")
SUMMARY_FILE = Path("docs/summary.txt")

def load_status():
    try:
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Failed to read status.json: {e}")

def generate_summary(status):
    earnings = status.get("earnings", {})
    total_usd = earnings.get("total_usd", 0.0)
    this_week_usd = earnings.get("this_week_usd", 0.0)
    last_cycle_usd = earnings.get("last_cycle_usd", 0.0)

    backfill = status.get("backfill", {})
    updated_total = backfill.get("updated_total", 0)
    remaining = backfill.get("remaining", 0)
    last_run = backfill.get("last_run", "N/A")

    lines = [
        "E-Evolve Daily Summary",
        "=" * 30,
        f"Date: {status.get('date', 'N/A')}",
        f"Total USD earned: ${total_usd:.2f}",
        f"This week USD: ${this_week_usd:.2f}",
        f"Last cycle USD: ${last_cycle_usd:.2f}",
        "",
        "Backfill Progress:",
        f"  Posts updated this cycle: {updated_total}",
        f"  Posts still needing footer: {remaining}",
        f"  Last backfill run: {last_run}",
        "",
        "Wallet status:",
        f"  USDT address: {status.get('wallet', {}).get('address_masked', 'N/A')}",
        f"  Network: {status.get('wallet', {}).get('network', 'N/A')}",
        f"  Last received: {status.get('wallet', {}).get('last_received_at', 'N/A')}",
        "",
        "Next steps:",
        "  • Review any posts marked as 'skipped' in backfill for manual fixes.",
        "  • Verify wallet address validity with `wallet_verification.py`.",
        "",
        "End of summary."
    ]
    return "\n".join(lines)

def main():
    status = load_status()
    summary = generate_summary(status)
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(summary, encoding="utf-8")
    print("Summary written to", SUMMARY_FILE)

if __name__ == "__main__":
    main()
'''