#!/usr/bin/env python3
"""
Convenience script to run markdown style checking on the D&D adventure content.
"""

import os
import sys
from pathlib import Path
from markdown_style_linter import MarkdownStyleLinter


def main():
    """Run style check on the adventure directory."""
    
    # Get the project root (parent of web_version)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    adventure_dir = project_root / "adventure"
    
    if not adventure_dir.exists():
        print(f"Error: Adventure directory not found at {adventure_dir}")
        return 1
    
    # Initialize the linter
    rules_file = script_dir / "style_rules.json"
    linter = MarkdownStyleLinter(str(rules_file))
    
    print("🔍 Running D&D Adventure Style Check...")
    print(f"📁 Scanning: {adventure_dir}")
    print(f"📋 Rules: {rules_file}")
    print("-" * 50)
    
    # Lint all markdown files in the adventure directory
    violations = linter.lint_directory(str(adventure_dir))
    
    # Generate output files
    output_dir = script_dir / "style_reports"
    output_dir.mkdir(exist_ok=True)
    
    text_report = output_dir / "style_report.txt"
    json_report = output_dir / "style_report.json"
    
    # Generate both reports
    linter.generate_report(violations, str(text_report))
    linter.generate_json_report(violations, str(json_report))
    
    # Print summary to console
    errors = len([v for v in violations if v.severity == "error"])
    warnings = len([v for v in violations if v.severity == "warning"])
    info = len([v for v in violations if v.severity == "info"])
    
    print(f"\n📊 STYLE CHECK RESULTS:")
    print(f"🔴 Errors: {errors}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"ℹ️  Info: {info}")
    print(f"📄 Total Issues: {len(violations)}")
    
    if violations:
        print(f"\n📝 Reports generated:")
        print(f"   Text: {text_report}")
        print(f"   JSON: {json_report}")
        
        # Show a few examples
        print(f"\n🔍 First few issues:")
        for i, v in enumerate(violations[:5]):
            icon = {"error": "🔴", "warning": "⚠️ ", "info": "ℹ️ "}[v.severity]
            print(f"   {icon} {v.file_path}:{v.line_number} - {v.message}")
        
        if len(violations) > 5:
            print(f"   ... and {len(violations) - 5} more (see reports for details)")
    else:
        print("\n✅ No style violations found! Great job!")
    
    # Return appropriate exit code
    return 1 if errors > 0 else 0


if __name__ == "__main__":
    exit(main()) 