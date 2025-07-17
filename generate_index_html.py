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
    """Generate a grouped list of links to *html_files*, organized by subdirectory."""
    grouped_files = {}
    for f in html_files:
        # Group by immediate parent directory relative to docs_dir
        # e.g. docs/monday/foo.html -> 'monday'
        # e.g. docs/bar.html -> '.' (root)
        try:
            parent_dir = f.relative_to(docs_dir).parts[0]
            if parent_dir == f.name:  # File is in the root of docs_dir
                parent_dir = "General"
        except IndexError:
            parent_dir = "General"  # Should not happen if f is in docs_dir, but for safety

        if parent_dir not in grouped_files:
            grouped_files[parent_dir] = []
        grouped_files[parent_dir].append(f)

    output_html = ""
    # Sort groups alphabetically, but maybe put "General" first if it exists
    sorted_groups = sorted(grouped_files.keys())

    for group_name in sorted_groups:
        files_in_group = grouped_files[group_name]
        if group_name == "index.html" or not files_in_group:
            continue
        # Use a more descriptive title if it's a known folder
        if group_name == "characters":
            output_html += "<h2>Player Characters</h2>\n"
        elif group_name != "General":
            output_html += f"<h2>{group_name.title()}</h2>\n"

        items = []
        for f in sorted(files_in_group):
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
                display = f.stem.replace("_", " ").replace("-", " ").title()

            rel_path = f.relative_to(docs_dir)
            items.append(f"<li><a href=\"{rel_path.as_posix()}\">{display}</a></li>")

        if items:
            output_html += "<ul>\n" + "\n".join(items) + "\n</ul>\n"

    return output_html


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

    # Force recursive if not specified, as the new structure depends on it.
    if not args.recursive:
        print("[INFO] --recursive not specified, but enabling it to find all logs in subdirectories.")
        html_files = collect_html_files(docs_dir, recursive=True)

    body = build_index_body(html_files, docs_dir)
    full_html = build_full_html(body, args.title, args.dnd_style)

    out_path = docs_dir / "index.html"
    out_path.write_text(full_html, encoding="utf-8")
    print(f"[SUCCESS] Wrote {out_path.relative_to(Path.cwd()) if out_path.is_absolute() else out_path}")


if __name__ == "__main__":
    main() 