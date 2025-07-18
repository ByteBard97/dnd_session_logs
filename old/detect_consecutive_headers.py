#!/usr/bin/env python3
"""
Detect consecutive header lines in all markdown files in the project.
Reports file, line numbers, and the headers involved.
"""
import sys
from pathlib import Path
import re

def find_consecutive_headers(md_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    results = []
    for i in range(1, len(lines)):
        if lines[i-1].strip().startswith('#') and lines[i].strip().startswith('#'):
            # Ignore if the previous line is a horizontal rule (e.g. '# ---')
            if re.match(r'^#+\s*-{3,}\s*$', lines[i-1].strip()):
                continue
            results.append((i, lines[i-1].rstrip(), lines[i].rstrip()))
    return results

def main():
    root = Path('.')
    md_files = list(root.rglob('*.md'))
    found = False
    for md_file in sorted(md_files):
        consecutive = find_consecutive_headers(md_file)
        if consecutive:
            found = True
            print(f'\nFile: {md_file}')
            for line_num, prev_header, curr_header in consecutive:
                print(f'  Lines {line_num}/{line_num+1}:')
                print(f'    {prev_header}')
                print(f'    {curr_header}')
    if not found:
        print('No consecutive headers found!')

if __name__ == '__main__':
    main() 