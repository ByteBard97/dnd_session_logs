#!/usr/bin/env python3
"""
Auto-fix markdown script for D&D session logs.
Adapted from the adventure content linter for session log specific issues.
"""

import re
import sys
import argparse
from pathlib import Path

class SessionLogAutoFixer:
    def __init__(self):
        # D&D session log specific abbreviations
        self.abbreviations = {
            'Session': 'Sess.',
            'Character': 'Char',
            'Investigation': 'Invest',
            'Encounter': 'Enc',
            'Description': 'Desc',
            'Challenge': 'Chall',
            'Difficulty': 'Diff',
            'Information': 'Info',
            'Equipment': 'Equip',
            'Experience': 'Exp',
            'Intelligence': 'Int',
            'Perception': 'Perc',
            'Performance': 'Perf',
            'Constitution': 'Con',
            'Charisma': 'Cha',
            'Strength': 'Str',
            'Dexterity': 'Dex',
            'Wisdom': 'Wis',
            'Conversation': 'Conv',
            'Interaction': 'Inter',
            'Negotiation': 'Negot',
            'Intimidation': 'Intim',
            'Persuasion': 'Pers',
            'Deception': 'Decep',
            'Underground': 'Undergrd',
            'Mechanical': 'Mech',
            'Structural': 'Struct',
            'Architectural': 'Arch',
            'Dungeon Master': 'DM',
            'Non-Player Character': 'NPC',
            'Player Character': 'PC',
        }

    def fix_empty_headers(self, line):
        """Fix empty headers that appear as just '#' with no text."""
        if re.match(r'^#+\s*$', line.strip()):
            return ''  # Remove completely empty headers
        return line

    def fix_session_headers(self, line):
        """Standardize session header formatting."""
        # Fix "Session X:" patterns with trailing spaces
        match = re.match(r'^(#+)\s*Session\s+(\d+)\s*:?\s*(.*)$', line.strip())
        if match:
            level, number, extra = match.groups()
            if extra.strip():
                return f"{level} Session {number}: {extra.strip()}\n"
            else:
                return f"{level} Session {number}\n"
        return line

    def fix_corrupted_footnotes(self, content):
        """Remove corrupted footnote numbers like '171717171717'."""
        # Remove repeated digit patterns (footnote corruption)
        content = re.sub(r'(\d)\1{5,}', '', content)
        
        # Clean up malformed footnote references
        content = re.sub(r'([a-zA-Z])\d{2,}([.!?])', r'\1\2', content)
        
        return content

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

    def fix_spacing_issues(self, content):
        """Fix spacing around headers and paragraphs."""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix trailing whitespace
            line = line.rstrip()
            
            # Ensure proper spacing around headers
            if line.startswith('#'):
                # Add blank line before header (unless it's the first line)
                if i > 0 and fixed_lines and fixed_lines[-1].strip() != '':
                    fixed_lines.append('')
                fixed_lines.append(line)
                # Add blank line after header (unless next line is already blank)
                if i + 1 < len(lines) and lines[i + 1].strip() != '':
                    fixed_lines.append('')
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def fix_bullet_formatting(self, content):
        """Standardize bullet point formatting."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Standardize bullet points to use '*'
            if re.match(r'^\s*[\-\+]\s+', line):
                line = re.sub(r'^\s*[\-\+]\s+', '* ', line)
            
            # Fix numbered lists spacing
            elif re.match(r'^\s*\d+\.\s*', line):
                line = re.sub(r'^(\s*\d+\.)\s*', r'\1 ', line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def fix_emphasis_formatting(self, content):
        """Standardize emphasis formatting."""
        # Fix bold formatting
        content = re.sub(r'\*\*\s+([^*]+)\s+\*\*', r'**\1**', content)
        
        # Fix italic formatting  
        content = re.sub(r'\*\s+([^*]+)\s+\*', r'*\1*', content)
        
        # Standardize underscores to asterisks for emphasis
        content = re.sub(r'\b_([^_]+)_\b', r'*\1*', content)
        
        return content

    def auto_fix_content(self, content):
        """Apply all auto-fixes to content."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix empty headers
            line = self.fix_empty_headers(line)
            if not line:  # Skip if header was removed
                continue
                
            # Fix session headers
            line = self.fix_session_headers(line)
            
            # Fix header length (H1: 50, H2: 40, H3: 35, H4: 30)
            if line.strip().startswith('# '):
                line = self.fix_header_length(line, 50)
            elif line.strip().startswith('## '):
                line = self.fix_header_length(line, 40)
            elif line.strip().startswith('### '):
                line = self.fix_header_length(line, 35)
            elif line.strip().startswith('#### '):
                line = self.fix_header_length(line, 30)
            
            fixed_lines.append(line)
        
        # Join back together and apply content-level fixes
        content = '\n'.join(fixed_lines)
        content = self.fix_corrupted_footnotes(content)
        content = self.fix_spacing_issues(content)
        content = self.fix_bullet_formatting(content)
        content = self.fix_emphasis_formatting(content)
        
        # Remove excessive empty lines (max 2 consecutive)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
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
    parser = argparse.ArgumentParser(description='Auto-fix D&D session log markdown files')
    parser.add_argument('files', nargs='+', help='Markdown files to fix')
    parser.add_argument('--check', action='store_true', help='Check only, don\'t modify')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    fixer = SessionLogAutoFixer()
    
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