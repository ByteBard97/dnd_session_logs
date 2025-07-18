#!/usr/bin/env python3
"""
Enhanced D&D Markdown Formatter
Integrates with markdownlint and provides format-on-save capability
"""

import sys
import json
import subprocess
from pathlib import Path
from auto_fix_markdown import MarkdownAutoFixer

class EnhancedMarkdownFormatter:
    def __init__(self):
        self.auto_fixer = MarkdownAutoFixer()
        
    def run_markdownlint(self, file_path):
        """Run markdownlint and return issues."""
        try:
            # Try to run markdownlint if available
            result = subprocess.run(
                ['markdownlint', '--json', str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return []
            
            # Parse markdownlint output
            try:
                issues = json.loads(result.stdout)
                return issues
            except json.JSONDecodeError:
                return []
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # markdownlint not available or timeout
            return []
    
    def format_file(self, file_path, fix_markdownlint_issues=True):
        """Format a file using both our custom fixer and markdownlint."""
        file_path = Path(file_path)
        
        if not file_path.exists() or file_path.suffix.lower() != '.md':
            return False
            
        # Step 1: Apply our custom D&D-specific fixes
        custom_fixes_applied = self.auto_fixer.fix_file(file_path)
        
        # Step 2: Run markdownlint to check for additional issues
        if fix_markdownlint_issues:
            issues = self.run_markdownlint(file_path)
            if issues:
                print(f"Markdownlint found {len(issues)} additional issues in {file_path}")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"  Line {issue.get('lineNumber', '?')}: {issue.get('ruleDescription', 'Unknown issue')}")
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more issues")
        
        return custom_fixes_applied
    
    def format_on_save(self, file_path):
        """Format a file when saved (silent mode)."""
        try:
            return self.format_file(file_path, fix_markdownlint_issues=False)
        except Exception as e:
            print(f"Error formatting {file_path}: {e}", file=sys.stderr)
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python enhanced_markdown_formatter.py <file.md> [--on-save]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    on_save_mode = '--on-save' in sys.argv
    
    formatter = EnhancedMarkdownFormatter()
    
    if on_save_mode:
        # Silent mode for format-on-save
        if formatter.format_on_save(file_path):
            print(f"Formatted: {file_path}")
    else:
        # Verbose mode for manual formatting
        if formatter.format_file(file_path):
            print(f"Formatted: {file_path}")
        else:
            print(f"No changes needed: {file_path}")

if __name__ == '__main__':
    main() 