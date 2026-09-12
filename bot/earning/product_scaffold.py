"""
Product scaffold generator.

Creates a minimal, shippable Chrome extension (Manifest V3) template that
solves one specific annoyance. The scaffold is a complete, runnable product
that can be listed on the Chrome Web Store (one-time $5, covers 20 extensions)
and on itch.io (free). The wallet address from payout.py is embedded in the
popup and README so buyers can pay directly via USDT on Tron.

This module is called by code_techs when a high-scoring channel opportunity
is found and auto_scaffold is enabled in config.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import payout

log = logging.getLogger(__name__)

_SCAFFOLD_DIR = Path("product_scaffold")
_DIST_DIR = Path("dist")

# The annoyance this template solves: copying code blocks from pages that
# disable right-click or add tracking. It's a real, specific problem with a
# one-click fix, and the free tier (the extension itself) costs nothing per
# user to run -- marginal cost is zero.
_TEMPLATE_FILES = {
    "manifest.json": """{
  "manifest_version": 3,
  "name": "__EXTENSION_NAME__",
  "version": "1.0.0",
  "description": "__EXTENSION_DESCRIPTION__",
  "permissions": ["activeTab", "scripting", "clipboardWrite"],
  "action": {
    "default_popup": "popup.html",
    "default_title": "__EXTENSION_NAME__"
  },
  "icons": {
    "16": "icon16.png",
    "48": "icon48.png",
    "128": "icon128.png"
  }
}""",
    "popup.html": """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { width: 280px; font-family: system-ui, sans-serif; padding: 12px; margin: 0; }
    h3 { margin: 0 0 8px; font-size: 14px; color: #1a1a2e; }
    button { width: 100%; padding: 10px; font-size: 13px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; }
    button:hover { background: #1d4ed8; }
    button:disabled { background: #94a3b8; cursor: not-allowed; }
    .hint { font-size: 11px; color: #64748b; margin-top: 8px; text-align: center; }
    .support { font-size: 11px; color: #64748b; margin-top: 12px; padding-top: 8px; border-top: 1px solid #e2e8f0; text-align: center; }
    .support a { color: #2563eb; text-decoration: none; }
  </style>
</head>
<body>
  <h3>__EXTENSION_NAME__</h3>
  <button id="copyBtn">Copy Code Block</button>
  <div class="hint">Click on any page with a code block</div>
  <div class="support">
    Support this work: <a href="__WALLET_URL__" target="_blank">USDT (TRC-20)</a>
  </div>
  <script src="popup.js"></script>
</body>
</html>""",
    "popup.js": """// Content script injected into the active tab
const COPY_CODE = `(() => {
  // Find the code block under the cursor or the largest one on the page
  const blocks = document.querySelectorAll('pre code, pre > code, .highlight code, .code-block code');
  if (!blocks.length) return 'NO_CODE_BLOCKS';
  
  let target = null;
  let maxLen = 0;
  blocks.forEach(block => {
    const text = block.innerText.trim();
    if (text.length > maxLen) {
      maxLen = text.length;
      target = block;
    }
  });
  
  if (!target) return 'NO_CODE_BLOCKS';
  
  navigator.clipboard.writeText(target.innerText).then(() => 'COPIED', () => 'CLIPBOARD_FAILED');
})();`;

async function copyCode() {
  const btn = document.getElementById('copyBtn');
  btn.disabled = true;
  btn.textContent = 'Copying...';
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) return;
    
    const result = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: new Function(COPY_CODE)
    });
    
    const outcome = result[0]?.result;
    if (outcome === 'COPIED') {
      btn.textContent = 'Copied! ✓';
      setTimeout(() => { btn.textContent = 'Copy Code Block'; btn.disabled = false; }, 1500);
    } else if (outcome === 'NO_CODE_BLOCKS') {
      btn.textContent = 'No code block found';
      setTimeout(() => { btn.textContent = 'Copy Code Block'; btn.disabled = false; }, 2000);
    } else {
      btn.textContent = 'Failed - try again';
      setTimeout(() => { btn.textContent = 'Copy Code Block'; btn.disabled = false; }, 2000);
    }
  } catch (e) {
    btn.textContent = 'Error - try again';
    setTimeout(() => { btn.textContent = 'Copy Code Block'; btn.disabled = false; }, 2000);
  }
}

document.getElementById('copyBtn').addEventListener('click', copyCode);""",
    "README.md": """# __EXTENSION_NAME__

__EXTENSION_DESCRIPTION__

## Install

1. Download the latest `.zip` from the [releases](https://github.com/__GITHUB_REPO__/releases) page
2. Unzip it
3. Open Chrome and go to `chrome://extensions/`
4. Enable **Developer mode** (top right)
5. Click **Load unpacked** and select the unzipped folder

## Usage

1. Navigate to any page with a code block (GitHub, Stack Overflow, documentation, etc.)
2. Click the extension icon in the toolbar
3. Click **Copy Code Block** — the largest code block on the page is copied to your clipboard

## Why this exists

Many sites disable right-click, add tracking, or wrap code in complex components that make copying frustrating. This extension bypasses all of that with one click.

## Support

These tools are free and always will be. If this saved you time, a small tip keeps them coming:

**USDT (TRC-20 / Tron):** `__WALLET_ADDRESS__`

[Send via wallet](__WALLET_URL__)

## License

MIT — do whatever you want with it.
""",
    "icon16.png": None,  # Generated programmatically
    "icon48.png": None,
    "icon128.png": None,
}


def _generate_icons(scaffold_path: Path) -> None:
    """Create simple PNG icons (16, 48, 128) using pure Python — no Pillow dependency."""
    # Minimal valid PNG (1x1 transparent) scaled up by the browser.
    # Real icons would be better but this keeps deps at zero.
    png_1x1 = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
        "1f15c4890000000a49444154789c63000100000500010d0a2db400000000"
        "49454e44ae426082"
    )
    for size in (16, 48, 128):
        (scaffold_path / f"icon{size}.png").write_bytes(png_1x1)


def _wallet_info() -> tuple[str, str]:
    """Return (address, wallet_url) from payout config."""
    cfg = payout.config()
    addr = cfg.get("address", "")
    network = cfg.get("network", "TRC-20 (Tron)")
    if addr:
        url = f"https://tronscan.org/#/address/{addr}"
    else:
        addr = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"  # fallback from status
        url = f"https://tronscan.org/#/address/{addr}"
    return addr, url


def build_scaffold(
    name: str = "CopyCodeBlock",
    description: str = "One-click copy for code blocks on any site",
    github_repo: str = "owner/repo",
) -> Path:
    """
    Build a complete Chrome extension scaffold in product_scaffold/<name>/.
    Returns the path to the created directory.
    """
    scaffold_path = _SCAFFOLD_DIR / name
    if scaffold_path.exists():
        shutil.rmtree(scaffold_path)
    scaffold_path.mkdir(parents=True)

    wallet_addr, wallet_url = _wallet_info()
    replacements = {
        "__EXTENSION_NAME__": name,
        "__EXTENSION_DESCRIPTION__": description,
        "__GITHUB_REPO__": github_repo,
        "__WALLET_ADDRESS__": wallet_addr,
        "__WALLET_URL__": wallet_url,
    }

    for filename, content in _TEMPLATE_FILES.items():
        if content is None:
            continue
        for k, v in replacements.items():
            content = content.replace(k, v)
        (scaffold_path / filename).write_text(content, encoding="utf-8")

    _generate_icons(scaffold_path)
    log.info("[product_scaffold] built %s at %s", name, scaffold_path)
    return scaffold_path


def package_zip(scaffold_path: Path) -> Path:
    """Create a Chrome Web Store ready .zip in dist/."""
    _DIST_DIR.mkdir(exist_ok=True)
    zip_path = _DIST_DIR / f"{scaffold_path.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in scaffold_path.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(scaffold_path))
    log.info("[product_scaffold] packaged %s", zip_path)
    return zip_path


def run(status: dict[str, Any], opportunity: dict[str, Any] | None = None) -> list[dict]:
    """
    Product entry point: ``run(status, opportunity)``.
    
    If ``opportunity`` is provided, uses its title/description for the scaffold.
    Otherwise builds a generic "CopyCodeBlock" extension.
    Returns an action dict for the dashboard.
    """
    try:
        cfg = _config()
        if not cfg.get("enabled", True):
            return [{"platform": "product_scaffold", "success": False, "error": "disabled", "estimated_usd": 0.0}]

        name = "CopyCodeBlock"
        description = "One-click copy for code blocks on any site"
        if opportunity:
            name = str(opportunity.get("title", "Product"))[:50].replace(" ", "").replace("-", "")
            description = str(opportunity.get("reason", description))[:120]

        scaffold_path = build_scaffold(name, description)
        zip_path = package_zip(scaffold_path)

        return [{
            "platform": "product_scaffold",
            "success": True,
            "title": f"Scaffolded {name}",
            "url": str(zip_path),
            "scaffold_dir": str(scaffold_path),
            "zip_path": str(zip_path),
            "estimated_usd": 0.0,
        }]
    except Exception as exc:
        log.warning("[product_scaffold] failed: %s", exc)
        return [{"platform": "product_scaffold", "success": False, "error": str(exc)[:200], "estimated_usd": 0.0}]


def _config() -> dict[str, Any]:
    from ._shared import load_config
    return load_config("product_scaffold", {
        "enabled": True,
        "auto_scaffold_top_channel": False,
        "default_name": "CopyCodeBlock",
        "default_description": "One-click copy for code blocks on any site",
    })