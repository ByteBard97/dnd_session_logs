#!/usr/bin/env python3
"""generate_index_html.py

Create an `index.html` landing page in the given *docs* directory that links to
all HTML files found there.  The page uses the same styling helper from
`generate_session_logs_html.py` so it matches the PHB look when `--dnd-style`
was used for the individual logs.

Usage (from project root)
------------------------
python generate_index_html.py               # scans ./docs
python generate_index_html.py /custom/docs  # custom folder

The script ignores an existing `index.html` when building the list but will
overwrite it on write.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

# Re-use the styling helper from the main generator script
try:
    from generate_session_logs_html import build_full_html  # type: ignore
except ImportError:  # pragma: no cover – should not happen in project root
    sys.stderr.write("[ERROR] Could not import build_full_html from generate_session_logs_html.py\n")
    sys.exit(1)


def collect_html_files(docs_dir: Path, recursive: bool = False) -> List[Path]:
    """Return list of .html files inside *docs_dir* (optionally recursive), excluding index.html."""
    pattern = "**/*.html" if recursive else "*.html"
    return sorted(
        p for p in docs_dir.glob(pattern) if p.name.lower() != "index.html"
    )


def build_index_body(html_files: List[Path], docs_dir: Path) -> str:
    """Generate an unordered list of links to *html_files*."""
    items = []
    for f in html_files:
        # Use the first H1 in the file as the display name if available
        display = None
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            import re
            m = re.search(r"<h1[^>]*>(.*?)</h1>", text, flags=re.IGNORECASE | re.DOTALL)
            if m:
                # strip inner tags
                display = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        except Exception:
            pass

        if not display:
            display = f.stem.replace("_", " ").title()

        rel_path = f.relative_to(docs_dir)
        items.append(f"<li><a href=\"{rel_path.as_posix()}\">{display}</a></li>")

    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a PHB-styled index.html in the docs directory.")
    parser.add_argument("docs_dir", nargs="?", type=Path, default=Path("docs"), help="Directory containing HTML logs (default: ./docs)")
    parser.add_argument("--title", "-t", default="D&D Session Logs", help="Title for the index page")
    parser.add_argument("--dnd-style", action="store_true", help="Use PHB styling (recommended if logs were made with --dnd-style)")
    parser.add_argument("--recursive", action="store_true", help="Include HTML files in subdirectories as well")
    args = parser.parse_args()

    docs_dir: Path = args.docs_dir.resolve()
    if not docs_dir.is_dir():
        sys.stderr.write(f"[ERROR] Docs directory not found: {docs_dir}\n")
        sys.exit(1)

    html_files = collect_html_files(docs_dir, recursive=args.recursive)
    if not html_files:
        sys.stderr.write(f"[WARN] No HTML files found in {docs_dir}; nothing to index.\n")
        sys.exit(0)

    body = build_index_body(html_files, docs_dir)
    full_html = build_full_html(body, args.title, args.dnd_style)

    out_path = docs_dir / "index.html"
    out_path.write_text(full_html, encoding="utf-8")
    print(f"[SUCCESS] Wrote {out_path.relative_to(Path.cwd()) if out_path.is_absolute() else out_path}")


if __name__ == "__main__":
    main() 