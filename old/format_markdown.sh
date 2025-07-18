#!/bin/bash
# Auto-format D&D markdown files
# Usage: ./format_markdown.sh file1.md file2.md
# Or: ./format_markdown.sh ../adventure/**/*.md

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOFIX_SCRIPT="$SCRIPT_DIR/auto_fix_markdown.py"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <markdown_files...>"
    echo "Example: $0 ../adventure/Queen_Vallus_Gratitude.md"
    echo "Example: $0 ../adventure/**/*.md"
    exit 1
fi

python "$AUTOFIX_SCRIPT" "$@" 