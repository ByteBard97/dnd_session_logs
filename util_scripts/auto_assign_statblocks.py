#!/usr/bin/env python3
"""
Auto-assign JSON statblocks to markdown files.

This script matches JSON files in the npcs/json directory to corresponding
markdown files and automatically adds the statblock loading code.
"""

import os
import re
import json
from pathlib import Path

def normalize_name(name):
    """Normalize a name for matching by removing special characters and converting to lowercase."""
    # Remove file extensions
    name = re.sub(r'\.(json|md)$', '', name)
    # Convert to lowercase and replace underscores/hyphens with spaces
    name = name.lower().replace('_', ' ').replace('-', ' ')
    
    # Handle special cases
    if 'matron mother severine' in name or 'matron severine' in name:
        return 'severine'
    if 'matron glutthraz' in name or 'matron zephyra' in name:
        return 'zephyra'
    if 'grumble flesh golem' in name or 'grumble' in name:
        return 'grumble'
    
    # Remove common prefixes and suffixes
    name = re.sub(r'^(matron|mother|the|chief|master|director|acolyte)\s+', '', name)
    name = re.sub(r'\s+(talzar|glutthraz|brinebless|fire.beard)$', '', name)
    # Remove spaces and special characters for final comparison
    return re.sub(r'[^a-z0-9]', '', name)

def find_markdown_match(json_file, markdown_files):
    """Find the best matching markdown file for a JSON file."""
    json_normalized = normalize_name(json_file.stem)
    
    best_match = None
    best_score = 0
    
    for md_file in markdown_files:
        md_normalized = normalize_name(md_file.stem)
        
        # Calculate similarity score
        if json_normalized == md_normalized:
            return md_file  # Perfect match
        
        # Check if one is a substring of the other
        if json_normalized in md_normalized or md_normalized in json_normalized:
            score = min(len(json_normalized), len(md_normalized)) / max(len(json_normalized), len(md_normalized))
            if score > best_score:
                best_score = score
                best_match = md_file
    
    return best_match if best_score > 0.6 else None

def has_statblock_already(md_file):
    """Check if the markdown file already has a statblock."""
    try:
        content = md_file.read_text(encoding='utf-8')
        return 'statblock' in content.lower() or 'loadJsonStatblock' in content
    except Exception:
        return False

def get_npc_name_from_json(json_file):
    """Extract the NPC name from the JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('name', json_file.stem.replace('_', ' ').title())
    except Exception:
        return json_file.stem.replace('_', ' ').title()

def add_statblock_to_markdown(md_file, json_file, npc_name):
    """Add statblock loading code to a markdown file."""
    try:
        content = md_file.read_text(encoding='utf-8')
        
        # Create the statblock HTML and script
        statblock_id = f"{md_file.stem.replace('_', '-')}-statblock"
        json_relative_path = f"json/{json_file.name}"
        
        statblock_code = f'''
## Combat Statistics

<div id="{statblock_id}"></div>

<script>
// Wait for page load to ensure all scripts are available
document.addEventListener('DOMContentLoaded', function() {{
  setTimeout(function() {{
    // Load statblock from JSON file
    loadJsonStatblock('{json_relative_path}', '{statblock_id}');
  }}, 100);
}});
</script>
'''
        
        # Try to add before any existing "Relationships" or "Activities" section, or at the end
        insertion_patterns = [
            r'(## (?:Notable )?Relationships)',
            r'(## (?:Recent )?Activities)',
            r'(## Current Activities)',
            r'(## Equipment)',
            r'(## Lore)',
            r'(\Z)'  # End of file
        ]
        
        inserted = False
        for pattern in insertion_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, statblock_code + r'\n\1', content, flags=re.IGNORECASE)
                inserted = True
                break
        
        if not inserted:
            content += statblock_code
        
        # Write back to file
        md_file.write_text(content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"Error updating {md_file}: {e}")
        return False

def main():
    """Main function to auto-assign statblocks."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    npcs_dir = project_root / 'site_src' / 'monday' / 'npcs'
    json_dir = npcs_dir / 'json'
    
    if not json_dir.exists():
        print(f"JSON directory not found: {json_dir}")
        return
    
    # Get all JSON and markdown files
    json_files = list(json_dir.glob('*.json'))
    markdown_files = [f for f in npcs_dir.glob('*.md') if f.name != 'index.md']
    
    print(f"Found {len(json_files)} JSON files and {len(markdown_files)} markdown files")
    
    matched = 0
    skipped = 0
    failed = 0
    
    for json_file in json_files:
        print(f"\nProcessing: {json_file.name}")
        
        # Find matching markdown file
        md_match = find_markdown_match(json_file, markdown_files)
        
        if not md_match:
            print(f"  ❌ No matching markdown file found")
            continue
        
        print(f"  ✅ Matched with: {md_match.name}")
        
        # Check if it already has a statblock
        if has_statblock_already(md_match):
            print(f"  ⏭️  Already has statblock, skipping")
            skipped += 1
            continue
        
        # Get NPC name from JSON
        npc_name = get_npc_name_from_json(json_file)
        
        # Add statblock to markdown
        if add_statblock_to_markdown(md_match, json_file, npc_name):
            print(f"  ✅ Added statblock for {npc_name}")
            matched += 1
        else:
            print(f"  ❌ Failed to add statblock")
            failed += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Successfully added: {matched}")
    print(f"  ⏭️  Skipped (already had): {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📁 Total JSON files: {len(json_files)}")

if __name__ == '__main__':
    main()