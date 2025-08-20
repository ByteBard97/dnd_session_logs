#!/usr/bin/env python3
"""
Remove old manual statblock content from NPCs that now have JSON statblocks.
Keeps the JSON loading script and any narrative content.
"""

import re
from pathlib import Path

def clean_statblock_file(file_path):
    """Remove ONLY the old manual statblock tables, keeping all narrative content."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Find where the JSON statblock script ends
        script_end_pattern = r'(</script>\s*\n)'
        script_match = re.search(script_end_pattern, content)
        
        if not script_match:
            print(f"  ⚠️  No JSON statblock found in {file_path.name}")
            return False
            
        # Keep everything up to and including the script
        keep_until = script_match.end()
        new_content = content[:keep_until]
        
        # Get the remaining content after the script
        remaining_content = content[keep_until:]
        
        # Remove only the statblock table sections
        statblock_sections = [
            r'## Core Statistics.*?(?=##|\Z)',
            r'## Ability Scores.*?(?=##|\Z)',
            r'## Additional Statistics.*?(?=##|\Z)',
            r'> \| \*\*Size\*\*.*?\n.*?\n',  # Size/Type/Alignment table
            r'> \| \*\*Armor Class\*\*.*?\n.*?\n',  # AC/HP/Speed table
            r'> \| \*\*STR\*\*.*?\n.*?\n',  # Ability scores table
            r'\*\*Saving Throws:\*\*.*?\n',
            r'\*\*Skills:\*\*.*?\n',
            r'\*\*Senses:\*\*.*?\n',
            r'\*\*Languages:\*\*.*?\n',
        ]
        
        # Remove each statblock section
        cleaned_content = remaining_content
        for pattern in statblock_sections:
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL | re.MULTILINE)
        
        # Clean up multiple newlines
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
        
        # Add the cleaned content back
        if cleaned_content.strip():
            new_content += '\n' + cleaned_content
        
        # Ensure file ends with single newline
        new_content = new_content.rstrip() + '\n'
        
        # Only write if content changed
        if new_content != original_content:
            file_path.write_text(new_content, encoding='utf-8')
            return True
        return False
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def main():
    """Clean all Cinderfork Foundry NPC files."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    foundry_dir = project_root / 'site_src' / 'monday' / 'npcs' / 'cinderfork_foundry'
    
    if not foundry_dir.exists():
        print(f"Directory not found: {foundry_dir}")
        return
    
    # Get all markdown files in the directory
    md_files = list(foundry_dir.glob('*.md'))
    
    print(f"Found {len(md_files)} files in Cinderfork Foundry directory")
    print("-" * 50)
    
    cleaned = 0
    skipped = 0
    failed = 0
    
    for md_file in md_files:
        if md_file.name == 'index.md':
            print(f"⏭️  Skipping index.md")
            skipped += 1
            continue
            
        print(f"Processing: {md_file.name}")
        
        if clean_statblock_file(md_file):
            print(f"  ✅ Cleaned old statblock content")
            cleaned += 1
        else:
            print(f"  ⏭️  No changes needed")
            skipped += 1
    
    print("-" * 50)
    print(f"📊 Summary:")
    print(f"  ✅ Cleaned: {cleaned}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📁 Total files: {len(md_files)}")

if __name__ == '__main__':
    main()