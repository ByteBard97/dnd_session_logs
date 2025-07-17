#!/usr/bin/env python3
"""build_all_logs.py

High-level convenience runner that:
1. Converts ALL Monday/Wednesday/Friday quest logs and session recaps from
   Markdown → standalone HTML (PHB styling inline).
2. Converts ALL player character bios from Markdown → standalone HTML.
3. Drops the resulting *.html files into the project-level `docs/` folder,
   preserving the directory structure (e.g., `docs/monday/`, `docs/characters/`).
4. Regenerates a styled `docs/index.html` that links to everything.

Assumed filename convention inside *source_dir* (default: `quest_logs/`):
- `monday/quest_log.md`
- `monday/session_recap.md`
- `wednesday/quest_log.md`
- `wednesday/session_recap.md`
- `friday/quest_log.md`
- `friday/session_recap.md`
- `characters/bilbo.md`
- `characters/gandalf.md`
- ...etc.

Missing files are skipped with a warning, so you can build incrementally.

Example usage
-------------
python build_all_logs.py                       # uses defaults, PHB styling
python build_all_logs.py --source custom_logs  # custom source folder
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

try:
    from generate_session_logs_html import (
        convert_files_to_html,
        build_full_html,
    )  # type: ignore
except ImportError:  # pragma: no cover
    sys.stderr.write("[ERROR] Please run from the project root where generate_session_logs_html.py resides.\n")
    sys.exit(1)

# Look for subdirectories (e.g. quest_logs/monday/) and treat each dir name as the "day" identifier.
FILENAME_MAP = {
    "quest_log": "Quest Log",
    "session_recap": "Session Recap",
}
MD_EXTS = [".md", ".markdown", ".txt"]


def find_markdown_file(day_dir: Path, kind: str) -> Path | None:
    """Return the markdown file for *kind* inside *day_dir* (quest_log/session_recap)."""
    base = kind  # e.g., 'quest_log'
    for ext in MD_EXTS:
        candidate = day_dir / f"{base}{ext}"
        if candidate.exists():
            return candidate
    return None


def build_single(src_markdown: Path, title: str, docs_dir: Path, dnd_style: bool) -> Path:
    """Convert *src_markdown* → HTML in *docs_dir*, return output path."""
    body_html = convert_files_to_html([src_markdown], include_toc=False)
    full_html = build_full_html(body_html, title, dnd_style)

    out_path = docs_dir / f"{src_markdown.stem}.html"
    out_path.write_text(full_html, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate all day logs + index with PHB styling.")
    parser.add_argument("--source", type=Path, default=Path("quest_logs"), help="Directory containing markdown logs")
    parser.add_argument("--docs", type=Path, default=Path("docs"), help="Output docs directory")
    parser.add_argument("--no-dnd", action="store_true", help="Disable D&D PHB styling (uses minimal CSS)")
    args = parser.parse_args()

    src_dir: Path = args.source.resolve()
    docs_dir: Path = args.docs.resolve()
    docs_dir.mkdir(parents=True, exist_ok=True)

    dnd_style = not args.no_dnd

    generated: List[Path] = []

    # Enumerate subdirectories inside source dir (e.g. 'monday', 'wednesday', 'friday')
    for day_dir in sorted(p for p in src_dir.iterdir() if p.is_dir()):
        day = day_dir.name  # folder name becomes label

        # Handle session logs (Mon/Wed/Fri)
        if day in ["monday", "wednesday", "friday"]:
            for kind, label in FILENAME_MAP.items():
                src_md = find_markdown_file(day_dir, kind)
                if not src_md:
                    sys.stderr.write(f"[WARN] Missing markdown: {day}/{kind}.md (skipping)\n")
                    continue
                title = f"{day.title()} {label}"
                # Ensure corresponding output subdirectory exists under docs
                out_day_dir = docs_dir / day
                out_day_dir.mkdir(parents=True, exist_ok=True)
                out_html = build_single(src_md, title, out_day_dir, dnd_style)
                print(f" [OK] {src_md.relative_to(src_dir)} → {out_html.relative_to(Path.cwd()) if out_html.is_absolute() else out_html}")
                generated.append(out_html)

        # Handle Character bios
        elif day == "characters":
            out_char_dir = docs_dir / day
            out_char_dir.mkdir(parents=True, exist_ok=True)

            char_files = []
            for ext in MD_EXTS:
                char_files.extend(day_dir.glob(f"*{ext}"))

            if not char_files:
                sys.stderr.write(f"[WARN] No markdown files found in {day_dir}. Skipping.\n")
                continue

            for src_md in char_files:
                if src_md.name.lower() in ["readme.md", "placeholder.txt"]:
                    continue  # Don't convert READMEs or placeholders
                title = src_md.stem.replace("_", " ").replace("-", " ").title()
                out_html = build_single(src_md, title, out_char_dir, dnd_style)
                print(f" [OK] {src_md.relative_to(src_dir)} → {out_html.relative_to(Path.cwd()) if out_html.is_absolute() else out_html}")
                generated.append(out_html)

    if not generated:
        sys.stderr.write("[ERROR] No markdown files converted. Nothing to do.\n")
        sys.exit(1)

    # Regenerate landing page – call generate_index_html as a module to keep styling consistent
    try:
        import generate_index_html  # type: ignore

        # Monkey-patch sys.argv before calling its main()
        sys_argv_backup = sys.argv[:]
        sys.argv = ["generate_index_html", str(docs_dir), "--recursive"] + ( ["--dnd-style"] if dnd_style else [])
        generate_index_html.main()  # type: ignore
        sys.argv = sys_argv_backup
    except Exception as e:  # pragma: no cover
        sys.stderr.write(f"[WARN] Could not regenerate index.html automatically ({e}). Run generate_index_html.py manually.\n")


if __name__ == "__main__":
    main() 