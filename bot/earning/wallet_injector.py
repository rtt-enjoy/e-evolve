import os
from pathlib import Path

def main():
    wallet = os.getenv("USDT_WALLET_ADDRESS")
    if not wallet:
        raise RuntimeError("USDT_WALLET_ADDRESS environment variable not set")

    readme_path = Path("README.md")
    if not readme_path.is_file():
        raise RuntimeError("README.md not found in repository root")

    text = readme_path.read_text(encoding="utf-8")
    if wallet not in text:
        new_text = text.rstrip() + f"\n\nWallet address for payments: {wallet}\n"
        readme_path.write_text(new_text, encoding="utf-8")
        print("Wallet address injected into README.md")
    else:
        print("Wallet address already present in README.md")

if __name__ == "__main__":
    main()