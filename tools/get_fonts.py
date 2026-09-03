#!/usr/bin/env python3
"""
Vendor the site's webfonts into assets/fonts/ and regenerate assets/css/fonts.css.

The site ships its own fonts so a visitor's browser never talks to a third
party. This script re-fetches the latin subsets from Google Fonts and rewrites
the @font-face block; run it only when the type stack changes.

    python3 tools/get_fonts.py
"""

from __future__ import annotations

import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
CSS_OUT = os.path.join(ROOT, "assets", "css", "fonts.css")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0 Safari/537.36")

# local basename -> Google Fonts css2 query
FAMILIES = {
    "Anton": "family=Anton",
    "BarlowCondensed": "family=Barlow+Condensed:wght@400;500;600",
    "Inter": "family=Inter:wght@400..600",
}

HEADER = """/* Locally hosted webfonts — no third-party requests at runtime.
 * Latin subsets pulled from Google Fonts (SIL Open Font License 1.1).
 * Regenerate with tools/get_fonts.py
 */
"""


def curl(url: str, out: str | None = None) -> str:
    cmd = ["curl", "-sS", "--fail", "-A", UA]
    if out:
        cmd += ["-o", out]
    cmd.append(url)
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout


def main() -> int:
    os.makedirs(FONT_DIR, exist_ok=True)
    faces: list[tuple[str, str, str]] = []

    for name, query in FAMILIES.items():
        css = curl(f"https://fonts.googleapis.com/css2?{query}&display=swap")
        for subset, block in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{[^}]*\})", css):
            if subset != "latin":
                continue
            url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
            weight = re.search(r"font-weight:\s*([\d\s]+);", block).group(1).strip()
            family = re.search(r"font-family:\s*'([^']+)'", block).group(1)
            filename = f"{name}-{weight.replace(' ', '-')}.woff2"
            curl(url, os.path.join(FONT_DIR, filename))
            faces.append((family, weight, filename))
            print(f"{family:18} {weight:9} -> assets/fonts/{filename}")

    with open(CSS_OUT, "w", encoding="utf-8") as fh:
        fh.write(HEADER)
        for family, weight, filename in faces:
            fh.write(
                f'\n@font-face {{\n  font-family: "{family}";\n  font-style: normal;\n'
                f"  font-weight: {weight};\n  font-display: swap;\n"
                f'  src: url("../fonts/{filename}") format("woff2");\n}}\n'
            )
    print(f"\nwrote {os.path.relpath(CSS_OUT, ROOT)} with {len(faces)} faces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
