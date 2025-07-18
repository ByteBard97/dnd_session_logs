#!/usr/bin/env python3
"""
Auto-fix markdown script for D&D adventures.
This script automatically fixes common markdown issues that can be safely corrected.
Can be used as a format-on-save tool in editors.
"""

import re
import sys
import argparse
from pathlib import Path

class MarkdownAutoFixer:
    def __init__(self):
        # Common D&D abbreviations for shortening headers
        self.abbreviations = {
            'Understanding': 'Underst&',
            'Character': 'Char',
            'Investigation': 'Invest',
            'Encounter': 'Enc',
            'Description': 'Desc',
            'Adventure': 'Adv',
            'Challenge': 'Chall',
            'Difficulty': 'Diff',
            'Information': 'Info',
            'Equipment': 'Equip',
            'Treasure': 'Treas',
            'Experience': 'Exp',
            'Intelligence': 'Int',
            'Perception': 'Perc',
            'Performance': 'Perf',
            'Constitution': 'Con',
            'Charisma': 'Cha',
            'Strength': 'Str',
            'Dexterity': 'Dex',
            'Wisdom': 'Wis',
            'Explanation': 'Expl',
            'Conversation': 'Conv',
            'Interaction': 'Inter',
            'Negotiation': 'Negot',
            'Intimidation': 'Intim',
            'Persuasion': 'Pers',
            'Deception': 'Decep',
            'Engineering': 'Eng',
            'Maintenance': 'Maint',
            'Significant': 'Sig',
            'Important': 'Imp',
            'Additional': 'Add\'l',
            'Alternative': 'Alt',
            'Emergency': 'Emerg',
            'Dangerous': 'Danger',
            'Mysterious': 'Myst',
            'Underground': 'Undergrd',
            'Construction': 'Constr',
            'Mechanical': 'Mech',
            'Structural': 'Struct',
            'Architectural': 'Arch',
        }

    def fix_header_length(self, line, max_length):
        """Fix header length by applying abbreviations."""
        if not line.strip().startswith('#'):
            return line
            
        # Extract header level and text
        match = re.match(r'^(#+)\s*(.+)$', line.strip())
        if not match:
            return line
            
        header_level, header_text = match.groups()
        
        if len(header_text) <= max_length:
            return line
            
        # Apply abbreviations
        fixed_text = header_text
        for full, abbrev in self.abbreviations.items():
            if full in fixed_text:
                fixed_text = fixed_text.replace(full, abbrev)
                if len(fixed_text) <= max_length:
                    break
                    
        return f"{header_level} {fixed_text}\n"

    def fix_line_length(self, line, max_length=120):
        """Break long lines at natural break points."""
        if len(line.strip()) <= max_length:
            return line
            
        # Don't break headers, code blocks, or tables
        if (line.strip().startswith('#') or 
            line.strip().startswith('```') or 
            line.strip().startswith('|') or
            line.strip().startswith('    ')):
            return line
            
        # Break at sentence boundaries
        sentences = re.split(r'(\. )', line)
        if len(sentences) > 2:
            current_line = ""
            result_lines = []
            
            for i, part in enumerate(sentences):
                if len(current_line + part) <= max_length:
                    current_line += part
                else:
                    if current_line:
                        result_lines.append(current_line + '\n')
                    current_line = part
                    
            if current_line:
                result_lines.append(current_line)
                
            return ''.join(result_lines)
            
        return line

    def fix_dialogue_format(self, line):
        """Fix dialogue formatting to standard D&D format."""
        # Match dialogue patterns: * Character: (action) "speech"
        dialogue_pattern = r'^\s*\*\s*\*\*([^*]+)\*\*:?\s*(.*)$'
        match = re.match(dialogue_pattern, line)
        
        if match:
            character, rest = match.groups()
            
            # Parse action and speech
            action_match = re.match(r'\(([^)]+)\)\s*(.*)$', rest)
            if action_match:
                action, speech = action_match.groups()
                return f"* **{character}:** ({action}) {speech}\n"
            else:
                return f"* **{character}:** {rest}\n"
                
        return line

    def fix_empty_lines(self, content):
        """Fix excessive empty lines (max 2 consecutive)."""
        lines = content.split('\n')
        result = []
        empty_count = 0
        
        for line in lines:
            if line.strip() == '':
                empty_count += 1
                if empty_count <= 2:  # Allow max 2 consecutive empty lines
                    result.append(line)
            else:
                empty_count = 0
                result.append(line)
                
        return '\n'.join(result)

    def fix_trailing_spaces(self, line):
        """Remove trailing spaces."""
        return line.rstrip() + '\n' if line.endswith('\n') else line.rstrip()

    def auto_fix_content(self, content):
        """Apply all auto-fixes to content."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix trailing spaces first
            line = self.fix_trailing_spaces(line)
            
            # Fix header length (H1: 50, H2: 40, H3: 35, H4: 30)
            if line.strip().startswith('# '):
                line = self.fix_header_length(line, 50)
            elif line.strip().startswith('## '):
                line = self.fix_header_length(line, 40)
            elif line.strip().startswith('### '):
                line = self.fix_header_length(line, 35)
            elif line.strip().startswith('#### '):
                line = self.fix_header_length(line, 30)
            
            # Fix dialogue format
            line = self.fix_dialogue_format(line)
            
            # Fix line length (but not for headers we just fixed)
            if not line.strip().startswith('#'):
                line = self.fix_line_length(line)
                
            fixed_lines.append(line)
            
        # Join and fix empty lines
        content = ''.join(fixed_lines)
        content = self.fix_empty_lines(content)
        
        return content

    def fix_file(self, file_path):
        """Fix a single markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            fixed_content = self.auto_fix_content(original_content)
            
            # Only write if changes were made
            if fixed_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                return True
            return False
            
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Auto-fix D&D markdown files')
    parser.add_argument('files', nargs='+', help='Markdown files to fix')
    parser.add_argument('--check', action='store_true', help='Check only, don\'t modify')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    fixer = MarkdownAutoFixer()
    
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"File not found: {file_path}")
            continue
            
        if not path.suffix.lower() == '.md':
            print(f"Skipping non-markdown file: {file_path}")
            continue
            
        if args.check:
            # Check mode - just report what would be fixed
            with open(path, 'r', encoding='utf-8') as f:
                original = f.read()
            fixed = fixer.auto_fix_content(original)
            if fixed != original:
                print(f"Would fix: {file_path}")
            elif args.verbose:
                print(f"No fixes needed: {file_path}")
        else:
            # Fix mode
            if fixer.fix_file(path):
                print(f"Fixed: {file_path}")
            elif args.verbose:
                print(f"No changes: {file_path}")

if __name__ == '__main__':
    main() 