#!/usr/bin/env python3
"""lint_markdown.py

Lint and format D&D session logs markdown files to ensure consistent formatting,
proper structure, and enhanced readability.

Features:
- Standardize heading structures
- Fix spacing and line breaks
- Clean up list formatting
- Standardize emphasis and strong text
- Remove duplicate whitespace
- Add proper paragraph breaks
- Validate image references
- Check for common markdown issues

Usage:
    python lint_markdown.py --check                    # Check all files for issues
    python lint_markdown.py --fix quest_logs/          # Fix all files in directory  
    python lint_markdown.py --fix file.md              # Fix specific file
    python lint_markdown.py --validate                 # Validate all files and report
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import difflib

class MarkdownLinter:
    def __init__(self):
        self.issues = []
        self.fixes_applied = 0
        
    def lint_file(self, file_path: Path, fix: bool = False) -> Tuple[str, List[str]]:
        """Lint a markdown file and optionally apply fixes."""
        self.issues = []
        self.fixes_applied = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.issues.append(f"Error reading file: {e}")
            return content, self.issues
            
        original_content = content
        
        # Apply linting rules
        content = self._fix_heading_structure(content)
        content = self._fix_spacing_and_breaks(content) 
        content = self._fix_list_formatting(content)
        content = self._fix_emphasis_formatting(content)
        content = self._fix_image_references(content, file_path)
        content = self._remove_duplicate_whitespace(content)
        content = self._fix_paragraph_breaks(content)
        content = self._fix_session_headers(content)
        content = self._remove_corrupted_numbers(content)
        
        # Write back if fixing and changes were made
        if fix and content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.issues.append(f"✅ Applied {self.fixes_applied} fixes")
            except Exception as e:
                self.issues.append(f"Error writing file: {e}")
        elif not fix and content != original_content:
            self.issues.append(f"⚠️  {self.fixes_applied} potential fixes available")
            
        return content, self.issues
    
    def _fix_heading_structure(self, content: str) -> str:
        """Fix heading structure and hierarchy."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix headers with trailing spaces
            if line.startswith('#'):
                # Remove trailing spaces and normalize
                header_match = re.match(r'^(#+)\s*(.+?)\s*$', line)
                if header_match:
                    level, text = header_match.groups()
                    # Remove any trailing colons or extra punctuation
                    text = re.sub(r':+\s*$', '', text)
                    fixed_line = f"{level} {text}"
                    if fixed_line != line:
                        self.fixes_applied += 1
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
                
        return '\n'.join(fixed_lines)
    
    def _fix_spacing_and_breaks(self, content: str) -> str:
        """Fix spacing around headers and paragraphs."""
        # Ensure headers have proper spacing
        content = re.sub(r'\n(#+[^\n]+)\n(?!\n)', r'\n\1\n\n', content)
        
        # Ensure proper spacing before headers  
        content = re.sub(r'(?<!\n)\n(#+[^\n]+)', r'\n\n\1', content)
        
        self.fixes_applied += len(re.findall(r'(#+[^\n]+)', content))
        return content
    
    def _fix_list_formatting(self, content: str) -> str:
        """Fix list formatting and indentation."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix bullet points
            if re.match(r'^\s*[\*\-\+]\s*', line):
                # Normalize to use '*' and ensure single space
                line = re.sub(r'^\s*[\*\-\+]\s*', '* ', line)
                self.fixes_applied += 1
            
            # Fix numbered lists
            elif re.match(r'^\s*\d+\.\s*', line):
                # Ensure proper spacing after number
                line = re.sub(r'^(\s*\d+\.)\s*', r'\1 ', line)
                
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
    
    def _fix_emphasis_formatting(self, content: str) -> str:
        """Fix emphasis and strong text formatting."""
        # Standardize bold to **text**
        content = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', content)
        
        # Standardize italic to *text*
        content = re.sub(r'\b_([^_]+)_\b', r'*\1*', content)
        
        # Fix spacing around emphasis
        content = re.sub(r'\*\*\s+([^*]+)\s+\*\*', r'**\1**', content)
        content = re.sub(r'\*\s+([^*]+)\s+\*', r'*\1*', content)
        
        self.fixes_applied += 3
        return content
    
    def _fix_image_references(self, content: str, file_path: Path) -> str:
        """Fix and validate image references."""
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        def fix_image_ref(match):
            alt_text, image_path = match.groups()
            
            # Check if image file exists
            if not image_path.startswith(('http://', 'https://', 'data:')):
                full_path = file_path.parent / image_path
                if not full_path.exists():
                    self.issues.append(f"Missing image: {image_path}")
                    
            # Ensure alt text is present
            if not alt_text.strip():
                # Generate alt text from filename
                alt_text = Path(image_path).stem.replace('_', ' ').replace('-', ' ').title()
                self.fixes_applied += 1
                
            return f"![{alt_text}]({image_path})"
        
        return re.sub(image_pattern, fix_image_ref, content)
    
    def _remove_duplicate_whitespace(self, content: str) -> str:
        """Remove excessive whitespace and normalize line breaks."""
        # Remove trailing whitespace
        content = re.sub(r' +$', '', content, flags=re.MULTILINE)
        
        # Normalize multiple empty lines to maximum 2
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove spaces before punctuation
        content = re.sub(r' +([,.!?;:])', r'\1', content)
        
        self.fixes_applied += 3
        return content
    
    def _fix_paragraph_breaks(self, content: str) -> str:
        """Ensure proper paragraph breaks."""
        # Add line breaks before new sentences that start a line
        content = re.sub(r'\.(\s*)([A-Z])', r'.\1\n\n\2', content)
        
        # Clean up excessive breaks created above
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        self.fixes_applied += 1
        return content
    
    def _fix_session_headers(self, content: str) -> str:
        """Fix session headers and ensure consistent formatting."""
        # Fix "Session X:" patterns with trailing spaces or improper formatting
        content = re.sub(r'^(#+)\s*Session\s+(\d+)\s*:?\s*(.*)$', 
                        r'\1 Session \2\3', content, flags=re.MULTILINE)
        
        # Ensure proper spacing after session headers
        content = re.sub(r'^(#+\s+Session\s+\d+.*)\n(?!\n)', 
                        r'\1\n\n', content, flags=re.MULTILINE)
        
        self.fixes_applied += 2
        return content
    
    def _remove_corrupted_numbers(self, content: str) -> str:
        """Remove corrupted footnote numbers and references."""
        # Remove repeated numbers like "171717171717"
        content = re.sub(r'(\d)\1{5,}', '', content)
        
        # Remove single trailing numbers that look like footnote artifacts
        content = re.sub(r'([a-zA-Z])\d{1,3}([.!?])', r'\1\2', content)
        
        # Clean up number sequences at end of words
        content = re.sub(r'([a-zA-Z]+)\d+([.!?]?\s)', r'\1\2', content)
        
        self.fixes_applied += 3
        return content

    def validate_markdown(self, file_path: Path) -> List[str]:
        """Validate markdown file and return list of issues."""
        validation_issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [f"Cannot read file: {e}"]
        
        lines = content.split('\n')
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 120:
                validation_issues.append(f"Line {i}: Line too long ({len(line)} chars)")
            
            # Trailing whitespace
            if line.endswith(' '):
                validation_issues.append(f"Line {i}: Trailing whitespace")
                
            # Mixed heading styles
            if line.startswith('#') and '**' in line:
                validation_issues.append(f"Line {i}: Mixed heading and bold formatting")
                
        # Check overall structure
        if not content.strip():
            validation_issues.append("File is empty")
            
        heading_count = len(re.findall(r'^#+', content, re.MULTILINE))
        if heading_count == 0:
            validation_issues.append("No headings found")
            
        return validation_issues


def main():
    parser = argparse.ArgumentParser(description="Lint and format D&D markdown files")
    parser.add_argument('path', nargs='?', default='.', help='File or directory to lint')
    parser.add_argument('--fix', action='store_true', help='Apply fixes automatically')
    parser.add_argument('--check', action='store_true', help='Check all files for issues')
    parser.add_argument('--validate', action='store_true', help='Validate files and report issues')
    
    args = parser.parse_args()
    
    linter = MarkdownLinter()
    path = Path(args.path)
    
    # Collect markdown files
    md_files = []
    if path.is_file() and path.suffix.lower() in ['.md', '.markdown']:
        md_files = [path]
    elif path.is_dir():
        md_files = list(path.rglob('*.md')) + list(path.rglob('*.markdown'))
    else:
        print(f"Invalid path: {path}")
        sys.exit(1)
    
    if not md_files:
        print("No markdown files found")
        sys.exit(0)
        
    print(f"Found {len(md_files)} markdown files")
    
    total_issues = 0
    total_fixes = 0
    
    for md_file in md_files:
        print(f"\n📄 {md_file}")
        
        if args.validate:
            issues = linter.validate_markdown(md_file)
            if issues:
                print(f"  ❌ {len(issues)} validation issues:")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"    • {issue}")
                if len(issues) > 5:
                    print(f"    ... and {len(issues) - 5} more")
                total_issues += len(issues)
            else:
                print("  ✅ No validation issues")
        else:
            content, issues = linter.lint_file(md_file, fix=args.fix)
            
            if issues:
                for issue in issues:
                    print(f"  {issue}")
                total_issues += len([i for i in issues if i.startswith('⚠️')])
                total_fixes += linter.fixes_applied
            else:
                print("  ✅ No issues found")
    
    print(f"\n📊 Summary:")
    print(f"  Files processed: {len(md_files)}")
    if args.validate:
        print(f"  Total validation issues: {total_issues}")
    else:
        print(f"  Total issues found: {total_issues}")
        if args.fix:
            print(f"  Total fixes applied: {total_fixes}")
        else:
            print(f"  Run with --fix to apply {total_fixes} potential fixes")

if __name__ == "__main__":
    main() 