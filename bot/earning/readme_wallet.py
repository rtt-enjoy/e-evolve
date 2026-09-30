"""
Script to embed the validated Tron wallet address into README and product pages.

Reads the environment variable USDT_WALLET_ADDRESS and replaces placeholders
like {WALLET_ADDRESS} in README.md and product_page.md (if present).
"""
import os
import re
from pathlib import Path
from typing import Optional

log_file = Path(__file__).parent / "readme_wallet.log"

def read_env_var(name: str) -> Optional[str]:
    value = os.getenv(name)
    if not value:
        print(f"[readme_wallet] ERROR: Environment variable {name} is not set.")
        return None
    return value

def replace_placeholder(file_path: Path, placeholder: str, replacement: str) -> bool:
    if not file_path.exists():
        print(f"[readme_wallet] SKIP: {file_path} does not exist.")
        return False
    content = file_path.read_text(encoding="utf-8")
    if placeholder not in content:
        print(f"[readme_wallet] INFO: Placeholder '{placeholder}' not found in {file_path}.")
        return False
    new_content = content.replace(placeholder, replacement)
    file_path.write_text(new_content, encoding="utf-8")
    print(f"[readme_wallet] UPDATED: {file_path}")
    return True

def main() -> None:
    wallet = read_env_var("USDT_WALLET_ADDRESS")
    if not wallet:
        return
    repo_root = Path.cwd()
    readme = repo_root / "README.md"
    product_page = repo_root / "product_page.md"
    placeholder = "{WALLET_ADDRESS}"
    updated = False
    if replace_placeholder(readme, placeholder, wallet):
        updated = True
    if replace_placeholder(product_page, placeholder, wallet):
        updated = True
    if updated:
        print(f"[readme_wallet] SUCCESS: Wallet address embedded.")
    else:
        print(f"[readme_wallet] INFO: No placeholders were updated.")

if __name__ == "__main__":
    main()