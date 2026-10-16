#!/usr/bin/env python3
"""
Create a zip package for the FocusFlow Chrome extension and upload to Getly.

This script creates the necessary extension files (manifest.json, popup.html)
and packages them into focusflow.zip, ready for manual upload to Getly.
It does not perform any network operations; the owner must run it locally
and then follow the steps in the suggestion to list the product on Getly.
"""

import json
import os
from pathlib import Path
import zipfile

def create_extension_files():
    # Directory for extension files
    ext_dir = Path("bot/products/focus_flow")
    ext_dir.mkdir(parents=True, exist_ok=True)

    # manifest.json
    manifest = {
        "manifest_version": 3,
        "name": "FocusFlow",
        "version": "1.0.0",
        "description": "A simple browser extension for focus tracking.",
        "action": {
            "default_popup": "popup.html"
        },
        "icons": {
            "48": "icon48.png"
        }
    }
    (ext_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # popup.html (simple placeholder)
    popup_html = """<!DOCTYPE html>
<html>
<head>
    <title>FocusFlow</title>
    <style>
        body { font-family: sans-serif; padding: 10px; }
        h1 { margin-top: 0; }
    </style>
</head>
<body>
    <h1>FocusFlow Extension</h1>
    <p>This extension is a prototype for the E-Evolve bot.</p>
</body>
</html>"""
    (ext_dir / "popup.html").write_text(popup_html)

    # icon48.png (tiny 1x1 transparent pixel placeholder)
    # We'll create a minimal PNG using raw bytes (1x1 black pixel)
    # For simplicity, we'll skip actual image and just create a placeholder file.
    # In a real extension, you'd provide a proper icon.
    (ext_dir / "icon48.png").write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00\x00\x00\x02\x00\x01\xe5\x1d\x0b\x00\x00\x00\x00IEND\xaeB`\x82')

def create_zip():
    ext_dir = Path("bot/products/focus_flow")
    zip_path = Path("focusflow.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in ext_dir.iterdir():
            zf.write(file, arcname=file.name)
    print(f"Created {zip_path} with contents:")
    for file in ext_dir.iterdir():
        print(f"  - {file.name}")

if __name__ == "__main__":
    create_extension_files()
    create_zip()