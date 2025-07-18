#!/usr/bin/env python3
"""
Lint D&D session logs for common formatting issues.
Combines auto-fixing and intelligent line wrapping.
"""

import argparse
import sys
from pathlib import Path
from session_log_auto_fixer import SessionLogAutoFixer
from intelligent_line_wrapper import DnDLineWrapper

def lint_session_log(file_path: Path, fix: bool = False, verbose: bool = False) -> bool:
    """Lint a single session log file."""
    if not file_path.exists():
        print(f"Error: File {file_path} not found")
        return False
    
    if not file_path.suffix.lower() == '.md':
        if verbose:
            print(f"Skipping non-markdown file: {file_path}")
        return False
    
    changes_made = False
    
    if fix:
        # Step 1: Apply auto-fixes
        fixer = SessionLogAutoFixer()
        if fixer.fix_file(file_path):
            changes_made = True
            if verbose:
                print(f"Applied auto-fixes to: {file_path}")
        
        # Step 2: Apply intelligent line wrapping
        wrapper = DnDLineWrapper(max_line_length=100)  # Slightly shorter for session logs
        try:
            # Check if any lines need wrapping
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
            
            if long_lines:
                wrapper.process_file(file_path)
                changes_made = True
                if verbose:
                    print(f"Applied line wrapping to: {file_path} (lines: {long_lines[:5]}{'...' if len(long_lines) > 5 else ''})")
        except Exception as e:
            print(f"Error applying line wrapping to {file_path}: {e}")
    
    else:
        # Check mode - report what would be fixed
        fixer = SessionLogAutoFixer()
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()
        
        fixed = fixer.auto_fix_content(original)
        issues = []
        
        if fixed != original:
            issues.append("auto-fixes available")
        
        # Check for long lines
        lines = original.split('\n')
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            issues.append(f"{len(long_lines)} long lines")
        
        # Check for empty headers
        empty_headers = [i+1 for i, line in enumerate(lines) if re.match(r'^#+\s*$', line)]
        if empty_headers:
            issues.append(f"{len(empty_headers)} empty headers")
        
        if issues:
            print(f"📄 {file_path}: {', '.join(issues)}")
            return True
        elif verbose:
            print(f"✅ {file_path}: No issues found")
    
    return changes_made

def main():
    parser = argparse.ArgumentParser(description='Lint D&D session log markdown files')
    parser.add_argument('paths', nargs='*', default=['.'], help='Files or directories to lint')
    parser.add_argument('--fix', action='store_true', help='Apply fixes automatically')
    parser.add_argument('--check', action='store_true', help='Check only, don\'t modify files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recursively process directories')
    
    args = parser.parse_args()
    
    # If both fix and check are specified, prefer check mode
    fix_mode = args.fix and not args.check
    
    # Collect markdown files
    md_files = []
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_file() and path.suffix.lower() == '.md':
            md_files.append(path)
        elif path.is_dir():
            if args.recursive:
                md_files.extend(path.rglob('*.md'))
            else:
                md_files.extend(path.glob('*.md'))
        else:
            print(f"Warning: {path} is not a valid file or directory")
    
    if not md_files:
        print("No markdown files found")
        return 0
    
    print(f"Processing {len(md_files)} markdown files...")
    
    issues_found = 0
    changes_made = 0
    
    for md_file in sorted(md_files):
        # Skip certain files
        if md_file.name.lower() in ['readme.md', 'license.md']:
            continue
            
        if lint_session_log(md_file, fix=fix_mode, verbose=args.verbose):
            if fix_mode:
                changes_made += 1
            else:
                issues_found += 1
    
    print(f"\n📊 Summary:")
    print(f"  Files processed: {len(md_files)}")
    if fix_mode:
        print(f"  Files modified: {changes_made}")
    else:
        print(f"  Files with issues: {issues_found}")
        if issues_found > 0:
            print(f"  Run with --fix to apply automatic fixes")
    
    return 0

if __name__ == '__main__':
    import re  # Import for the empty header check
    exit(main()) 