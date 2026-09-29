import os
import pathlib

WALLET_ADDRESS = os.getenv("USDT_WALLET_ADDRESS")
if not WALLET_ADDRESS:
    raise RuntimeError("USDT_WALLET_ADDRESS environment variable not set")

repo_root = pathlib.Path(__file__).parent.parent
readme_path = repo_root / "README.md"
product_page_path = repo_root / "product_page.md"  # adjust if needed

def replace_in_file(path):
    text = path.read_text(encoding="utf-8")
    new_text = text.replace("{WALLET_ADDRESS}", WALLET_ADDRESS)
    path.write_text(new_text, encoding="utf-8")
    print(f"Updated {path}")

if __name__ == "__main__":
    replace_in_file(readme_path)
    if product_page_path.exists():
        replace_in_file(product_page_path)