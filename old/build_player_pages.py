#!/usr/bin/env python3
"""build_player_pages.py

Generate HTML character pages for each campaign (Monday/Wednesday/Friday)
that showcase player characters with their descriptions and images.

Expected structure in quest_logs/<day>/players/:
  - pcs.md, PC_descriptions.md, or similar markdown files with character info
  - <character_name>.webp images for each PC
  - Other supporting .md files (epic_paths.md, etc.)

Usage:
  python build_player_pages.py                    # all days with PHB styling
  python build_player_pages.py --no-dnd          # minimal styling
  python build_player_pages.py --day wednesday   # specific day only
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    from generate_session_logs_html import (
        convert_files_to_html,
        build_full_html,
    )  # type: ignore
except ImportError:
    sys.stderr.write("[ERROR] Please run from the project root where generate_session_logs_html.py resides.\n")
    sys.exit(1)


def find_player_markdown_files(players_dir: Path) -> List[Path]:
    """Find markdown files containing player character information."""
    # Prioritize PC descriptions first, then epic paths, then other files
    priority_files = [
        "PC_descriptions.md", "pcs.md", "player_characters.md"  # Character info first
    ]
    epic_files = [
        "epic_paths.md", "epic_path_progress.md"  # Epic path info second
    ]
    other_files = [
        "player_character_quests.md"  # Other supporting info last
    ]
    
    found = []
    
    # Add files in priority order
    for file_list in [priority_files, epic_files, other_files]:
        for candidate in file_list:
            path = players_dir / candidate
            if path.exists():
                found.append(path)
    
    return found


def find_character_images(players_dir: Path) -> Dict[str, Path]:
    """Find all character image files and map them by character name."""
    images = {}
    for img_path in players_dir.glob("*.webp"):
        # Use filename (without extension) as character key
        char_name = img_path.stem.lower()
        images[char_name] = img_path
    return images


def embed_character_images(html_content: str, images: Dict[str, Path], players_dir: Path) -> str:
    """Convert markdown image references to embedded base64 data URLs."""
    import base64
    
    # Find all <img> tags with relative src paths and convert to base64
    def replace_img_src(match):
        full_tag = match.group(0)
        src_value = match.group(1)
        
        # Skip if already a data URL or external URL
        if src_value.startswith(('data:', 'http:', 'https:')):
            return full_tag
        
        # Try to find the image file
        img_path = players_dir / src_value
        if not img_path.exists():
            print(f"[WARN] Image not found: {img_path}")
            return full_tag
        
        try:
            # Read and encode image as base64
            img_data = img_path.read_bytes()
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            
            # Determine MIME type from extension
            ext = img_path.suffix.lower()
            mime_type = {
                '.webp': 'image/webp',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif'
            }.get(ext, 'image/webp')
            
            # Replace src with data URL
            data_url = f"data:{mime_type};base64,{img_b64}"
            return full_tag.replace(f'src="{src_value}"', f'src="{data_url}"')
            
        except Exception as e:
            print(f"[WARN] Could not embed image {src_value}: {e}")
            return full_tag
    
    # Replace all img src attributes
    html_content = re.sub(r'<img[^>]+src="([^"]+)"[^>]*>', replace_img_src, html_content)
    
    return html_content


def build_player_page(day: str, quest_logs_dir: Path, docs_dir: Path, dnd_style: bool) -> Optional[Path]:
    """Build a player character page for the given day."""
    players_dir = quest_logs_dir / day / "players"
    if not players_dir.exists():
        print(f"[WARN] No players directory found for {day}")
        return None
    
    # Find character info markdown files
    md_files = find_player_markdown_files(players_dir)
    if not md_files:
        print(f"[WARN] No player character markdown files found for {day}")
        return None
    
    # Find character images
    images = find_character_images(players_dir)
    
    # Convert markdown to HTML
    body_html = convert_files_to_html(md_files, include_toc=True)
    
    # Convert any image references to embedded base64 data URLs
    body_html = embed_character_images(body_html, images, players_dir)
    
    # Add some custom styling for character pages
    custom_css = """
    <style>
    .character-image {
        text-align: center;
        margin: 1em 0;
    }
    .character-image img {
        max-width: 300px;
        max-height: 400px;
        width: auto;
        height: auto;
        object-fit: cover;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border: 2px solid #c9ad6a;
        border-radius: 8px;
        margin: 0.5em;
        display: inline-block;
    }
    
    /* For multiple character images (like Astraeus), display them in a row */
    .character-image:has(img + img) {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 1em;
    }
    
    .character-image:has(img + img) img {
        max-width: 250px;
        max-height: 300px;
        flex: 0 0 auto;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .character-image img {
            max-width: 250px;
            max-height: 300px;
        }
        
        .character-image:has(img + img) img {
            max-width: 200px;
            max-height: 250px;
        }
    }
    </style>
    """
    
    # Build full HTML
    title = f"{day.title()} Player Characters"
    full_html = build_full_html(body_html, title, dnd_style)
    
    # Inject custom CSS before closing </head>
    full_html = full_html.replace("</head>", custom_css + "</head>")
    
    # Write to docs
    day_dir = docs_dir / day
    day_dir.mkdir(parents=True, exist_ok=True)
    out_path = day_dir / "player_characters.html"
    out_path.write_text(full_html, encoding="utf-8")
    
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate player character pages for D&D campaigns.")
    parser.add_argument("--quest-logs", type=Path, default=Path("quest_logs"), help="Directory containing campaign folders")
    parser.add_argument("--docs", type=Path, default=Path("docs"), help="Output docs directory")
    parser.add_argument("--no-dnd", action="store_true", help="Disable D&D PHB styling")
    parser.add_argument("--day", help="Generate for specific day only (monday/wednesday/friday)")
    args = parser.parse_args()
    
    quest_logs_dir = args.quest_logs.resolve()
    docs_dir = args.docs.resolve()
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    dnd_style = not args.no_dnd
    
    # Determine which days to process
    if args.day:
        days = [args.day.lower()]
    else:
        # Find all day directories
        days = [p.name for p in quest_logs_dir.iterdir() if p.is_dir()]
    
    generated = []
    for day in sorted(days):
        out_path = build_player_page(day, quest_logs_dir, docs_dir, dnd_style)
        if out_path:
            print(f"[OK] Generated {day} player page: {out_path.relative_to(Path.cwd())}")
            generated.append(out_path)
    
    if not generated:
        print("[WARN] No player pages generated")
        return
    
    # Regenerate main index to include player pages
    try:
        import generate_index_html
        sys_argv_backup = sys.argv[:]
        sys.argv = ["generate_index_html", str(docs_dir), "--recursive"] + (["--dnd-style"] if dnd_style else [])
        generate_index_html.main()
        sys.argv = sys_argv_backup
        print("[OK] Updated main index.html")
    except Exception as e:
        print(f"[WARN] Could not update index.html: {e}")


if __name__ == "__main__":
    main() 