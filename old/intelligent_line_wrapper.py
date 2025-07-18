#!/usr/bin/env python3
"""
Intelligent Line Wrapper for D&D Session Logs
Breaks lines at natural speech boundaries, not arbitrary character limits.
Adapted for session logs with D&D-specific break patterns.
"""

import re
import argparse
from pathlib import Path

class DnDLineWrapper:
    def __init__(self, max_line_length=120):
        self.max_length = max_line_length
        
        # Natural break points in order of preference
        self.break_patterns = [
            # Dialogue breaks (highest priority)
            (r'(\. )"', r'\1"\n'),  # End of sentence in dialogue
            (r'([!?]) "', r'\1 "\n'),  # Exclamation/question in dialogue
            
            # Sentence boundaries
            (r'(\. +)([A-Z])', r'\1\n\2'),  # Sentence endings
            (r'([!?] +)([A-Z])', r'\1\n\2'),  # Strong punctuation
            
            # Clause boundaries
            (r'(, and )([a-z])', r',\nand \2'),  # Long conjunction
            (r'(, but )([a-z])', r',\nbut \2'),  # Contrasting clause
            (r'(, which )([a-z])', r',\nwhich \2'),  # Relative clause
            (r'(, while )([a-z])', r',\nwhile \2'),  # Temporal clause
            
            # D&D specific breaks
            (r'(\. +)(DC \d+)', r'\1\n\2'),  # Difficulty class on new line
            (r'(\. +)(\d+d\d+)', r'\1\n\2'),  # Dice rolls on new line
            (r'(\. +)(Make a)', r'\1\nMake a'),  # Skill checks
            (r'(\. +)(Roll a)', r'\1\nRoll a'),  # Random rolls
            
            # Session log specific breaks
            (r'(\. +)(Session \d+)', r'\1\n\2'),  # Session markers
            (r'(\. +)(The party)', r'\1\nThe party'),  # Party actions
            (r'(\. +)(After)', r'\1\nAfter'),  # Temporal transitions
            
            # List and description breaks
            (r'(:) +([A-Z])', r':\n\2'),  # After colons
            (r'(;) +([A-Z])', r';\n\2'),  # After semicolons (rare but useful)
        ]
    
    def wrap_line(self, line):
        """Intelligently wrap a single line at natural break points."""
        if len(line) <= self.max_length:
            return line
            
        # Don't wrap certain special lines
        if self._is_special_line(line):
            return line
            
        # Try natural break patterns
        for pattern, replacement in self.break_patterns:
            if re.search(pattern, line):
                wrapped = re.sub(pattern, replacement, line)
                # Check if this actually helped
                lines = wrapped.split('\n')
                if all(len(l) <= self.max_length for l in lines):
                    return wrapped
        
        # Fallback to smart word wrapping
        return self._smart_word_wrap(line)
    
    def _is_special_line(self, line):
        """Check if this line should not be wrapped."""
        special_patterns = [
            r'^#',           # Headers
            r'^\|',          # Table rows
            r'^```',         # Code blocks
            r'^>',           # Blockquotes
            r'^\*\*[A-Z]',   # Bold labels (like **DC 15**)
            r'^!\[',         # Images
            r'^\[',          # Links
            r'^---',         # Horizontal rules
            r'^\s*\*\s+',    # Bullet points
        ]
        
        return any(re.match(pattern, line.strip()) for pattern in special_patterns)
    
    def _smart_word_wrap(self, line):
        """Fallback word wrapping that prefers natural breaks."""
        if len(line) <= self.max_length:
            return line
            
        # Find the best break point within the limit
        words = line.split()
        wrapped_lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + (1 if current_line else 0)  # +1 for space
            
            if current_length + word_length <= self.max_length:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    wrapped_lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            wrapped_lines.append(' '.join(current_line))
            
        return '\n'.join(wrapped_lines)
    
    def process_file(self, file_path, output_path=None):
        """Process an entire markdown file."""
        if output_path is None:
            output_path = file_path
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        processed_lines = []
        in_code_block = False
        
        for line in lines:
            line = line.rstrip()
            
            # Track code blocks (don't wrap inside them)
            if line.startswith('```'):
                in_code_block = not in_code_block
                processed_lines.append(line)
                continue
                
            if in_code_block:
                processed_lines.append(line)
                continue
            
            # Process regular lines
            if line.strip():  # Non-empty line
                wrapped = self.wrap_line(line)
                processed_lines.extend(wrapped.split('\n'))
            else:  # Empty line
                processed_lines.append('')
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(processed_lines) + '\n')
        
        return output_path

def main():
    parser = argparse.ArgumentParser(description='Intelligent line wrapper for D&D session logs')
    parser.add_argument('files', nargs='+', help='Markdown files to process')
    parser.add_argument('--max-length', type=int, default=120, help='Maximum line length (default: 120)')
    parser.add_argument('--check', action='store_true', help='Check only, don\'t modify files')
    parser.add_argument('--output', help='Output file (for single file only)')
    
    args = parser.parse_args()
    
    wrapper = DnDLineWrapper(args.max_length)
    
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File {file_path} not found")
            continue
            
        print(f"Processing {file_path}...")
        
        if args.check:
            # Just report what would be changed
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > args.max_length]
            
            if long_lines:
                print(f"  Lines over {args.max_length} chars: {long_lines[:10]}{'...' if len(long_lines) > 10 else ''}")
            else:
                print(f"  ✅ All lines within {args.max_length} characters")
        else:
            # Process the file
            output_path = args.output if args.output and len(args.files) == 1 else path
            wrapper.process_file(path, output_path)
            print(f"  ✅ Wrapped and saved to {output_path}")

if __name__ == '__main__':
    main() 