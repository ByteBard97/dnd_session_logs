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
    """Generate a hierarchical list of links grouped by campaign day."""
    import re
    
    # Group files by day (directory name)
    day_groups = {}
    root_files = []
    
    for f in html_files:
        rel_path = f.relative_to(docs_dir)
        
        # Check if file is in a subdirectory (campaign day)
        if len(rel_path.parts) > 1:
            day = rel_path.parts[0].lower()
            if day not in day_groups:
                day_groups[day] = []
            day_groups[day].append(f)
        else:
            root_files.append(f)
    
    def get_display_name(file_path):
        """Extract display name from file's first H1 or use filename."""
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"<h1[^>]*>(.*?)</h1>", text, flags=re.IGNORECASE | re.DOTALL)
            if m:
                return re.sub(r"<[^>]+>", "", m.group(1)).strip()
        except Exception:
            pass
        return file_path.stem.replace("_", " ").title()
    
    # Build HTML structure
    html_parts = []
    
    # Sort days in the desired order
    day_order = ["monday", "wednesday", "friday"]
    
    for day in day_order:
        if day in day_groups:
            files = day_groups[day]
            html_parts.append(f"<h2>{day.title()}</h2>")
            html_parts.append("<ul>")
            
            # Sort files within each day: player characters first, then quest log, then session recap
            def sort_key(f):
                name = f.name.lower()
                if "player" in name or "character" in name:
                    return 0
                elif "quest" in name:
                    return 1
                elif "session" in name or "recap" in name:
                    return 2
                else:
                    return 3
            
            for f in sorted(files, key=sort_key):
                display = get_display_name(f)
                rel_path = f.relative_to(docs_dir)
                html_parts.append(f"  <li><a href=\"{rel_path.as_posix()}\">{display}</a></li>")
            
            html_parts.append("</ul>")
    
    # Add any remaining days not in the standard order
    for day, files in day_groups.items():
        if day not in day_order:
            html_parts.append(f"<h2>{day.title()}</h2>")
            html_parts.append("<ul>")
            for f in sorted(files, key=lambda x: x.name):
                display = get_display_name(f)
                rel_path = f.relative_to(docs_dir)
                html_parts.append(f"  <li><a href=\"{rel_path.as_posix()}\">{display}</a></li>")
            html_parts.append("</ul>")
    
    # Add any root-level files at the end
    if root_files:
        html_parts.append("<h2>Other</h2>")
        html_parts.append("<ul>")
        for f in sorted(root_files, key=lambda x: x.name):
            display = get_display_name(f)
            rel_path = f.relative_to(docs_dir)
            html_parts.append(f"  <li><a href=\"{rel_path.as_posix()}\">{display}</a></li>")
        html_parts.append("</ul>")
    
    return "\n".join(html_parts)


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