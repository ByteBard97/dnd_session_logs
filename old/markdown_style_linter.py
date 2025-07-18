#!/usr/bin/env python3
"""
D&D Adventure Markdown Style Linter

Checks markdown files against style rules defined in style_rules.json
and generates detailed violation reports.
"""

import json
import re
import os
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Violation:
    """Represents a style rule violation."""
    file_path: str
    line_number: int
    rule_name: str
    severity: str
    message: str
    actual_value: Any
    expected_value: Any
    suggestion: str = ""


class MarkdownStyleLinter:
    """Main linter class that processes markdown files against style rules."""
    
    def __init__(self, rules_file: str = "style_rules.json"):
        """Initialize the linter with rules from JSON file."""
        self.rules = self._load_rules(rules_file)
        self.violations: List[Violation] = []
        
    def _load_rules(self, rules_file: str) -> Dict:
        """Load style rules from JSON file."""
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Rules file {rules_file} not found")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in rules file: {e}")
    
    def lint_file(self, file_path: str) -> List[Violation]:
        """Lint a single markdown file and return violations."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            violations.append(Violation(
                file_path=file_path,
                line_number=0,
                rule_name="file_encoding",
                severity="error",
                message="File is not UTF-8 encoded",
                actual_value="non-UTF-8",
                expected_value="UTF-8"
            ))
            return violations
        
        # Check each line
        for line_num, line in enumerate(lines, 1):
            violations.extend(self._check_line(file_path, line_num, line, lines))
        
        # Check document structure
        violations.extend(self._check_document_structure(file_path, lines))
        
        return violations
    
    def _check_line(self, file_path: str, line_num: int, line: str, all_lines: List[str]) -> List[Violation]:
        """Check a single line for violations."""
        violations = []
        stripped_line = line.strip()
        
        # Skip empty lines
        if not stripped_line:
            return violations
        
        # Check headers
        if stripped_line.startswith('#'):
            violations.extend(self._check_header(file_path, line_num, stripped_line))
        
        # Check dialogue formatting
        elif stripped_line.startswith('*') and '**' in stripped_line:
            violations.extend(self._check_dialogue(file_path, line_num, stripped_line))
        
        # Check read-aloud formatting
        elif stripped_line.startswith('>'):
            violations.extend(self._check_read_aloud(file_path, line_num, stripped_line))
        
        # Check line length
        violations.extend(self._check_line_length(file_path, line_num, line))
        
        # Check image formatting
        if '![' in stripped_line and '](' in stripped_line:
            violations.extend(self._check_image(file_path, line_num, stripped_line))
        
        return violations
    
    def _check_header(self, file_path: str, line_num: int, line: str) -> List[Violation]:
        """Check header formatting and length."""
        violations = []
        
        # Determine header level
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if not header_match:
            violations.append(Violation(
                file_path=file_path,
                line_number=line_num,
                rule_name="header_format",
                severity="error",
                message="Header must have space after # symbols",
                actual_value=line,
                expected_value="# Header Text"
            ))
            return violations
        
        header_level = len(header_match.group(1))
        header_text = header_match.group(2).strip()
        header_length = len(header_text)
        
        # Get rules for this header level
        header_key = f"h{header_level}"
        if header_key in self.rules["rules"]["headers"]:
            header_rules = self.rules["rules"]["headers"][header_key]
            
            # Check length violations
            if header_length > header_rules["absolute_max"]:
                over_limit = header_length - header_rules["absolute_max"]
                suggestion = self._suggest_header_fix(header_text)
                violations.append(Violation(
                    file_path=file_path,
                    line_number=line_num,
                    rule_name=f"{header_key}_absolute_max",
                    severity="error",
                    message=f"Header too long: {header_length} chars (max: {header_rules['absolute_max']})",
                    actual_value=header_length,
                    expected_value=header_rules["absolute_max"],
                    suggestion=suggestion
                ))
            elif header_length > header_rules["ideal_max"]:
                over_limit = header_length - header_rules["ideal_max"]
                suggestion = self._suggest_header_fix(header_text)
                violations.append(Violation(
                    file_path=file_path,
                    line_number=line_num,
                    rule_name=f"{header_key}_ideal_max",
                    severity="warning",
                    message=f"Header longer than ideal: {header_length} chars (ideal max: {header_rules['ideal_max']})",
                    actual_value=header_length,
                    expected_value=header_rules["ideal_max"],
                    suggestion=suggestion
                ))
            elif header_length < header_rules["ideal_min"]:
                violations.append(Violation(
                    file_path=file_path,
                    line_number=line_num,
                    rule_name=f"{header_key}_ideal_min",
                    severity="info",
                    message=f"Header very short: {header_length} chars (ideal min: {header_rules['ideal_min']})",
                    actual_value=header_length,
                    expected_value=header_rules["ideal_min"]
                ))
        
        return violations
    
    def _check_dialogue(self, file_path: str, line_num: int, line: str) -> List[Violation]:
        """Check dialogue formatting."""
        violations = []
        
        # Check if it follows dialogue pattern: * **Character:** (action) *"speech"*
        dialogue_pattern = r'^\*\s+\*\*([^*]+)\*\*:\s*(\([^)]*\))?\s*\*"([^"]*)".*'
        match = re.match(dialogue_pattern, line)
        
        if match:
            character_name = match.group(1)
            action = match.group(2) or ""
            speech = match.group(3)
            
            # Check character name length
            char_rules = self.rules["rules"]["content"]["dialogue_character_name"]
            if len(character_name) > char_rules["max_length"]:
                violations.append(Violation(
                    file_path=file_path,
                    line_number=line_num,
                    rule_name="dialogue_character_name",
                    severity="warning",
                    message=f"Character name too long: {len(character_name)} chars (max: {char_rules['max_length']})",
                    actual_value=len(character_name),
                    expected_value=char_rules["max_length"]
                ))
            
            # Check action description length
            if action:
                action_text = action.strip('()')
                action_rules = self.rules["rules"]["content"]["dialogue_action"]
                if len(action_text) > action_rules["max_length"]:
                    violations.append(Violation(
                        file_path=file_path,
                        line_number=line_num,
                        rule_name="dialogue_action",
                        severity="warning",
                        message=f"Action description too long: {len(action_text)} chars (max: {action_rules['max_length']})",
                        actual_value=len(action_text),
                        expected_value=action_rules["max_length"]
                    ))
            
            # Check speech length
            speech_rules = self.rules["rules"]["content"]["dialogue_speech"]
            if len(speech) > speech_rules["max_length"]:
                violations.append(Violation(
                    file_path=file_path,
                    line_number=line_num,
                    rule_name="dialogue_speech",
                    severity="error",
                    message=f"Dialogue speech too long: {len(speech)} chars (max: {speech_rules['max_length']})",
                    actual_value=len(speech),
                    expected_value=speech_rules["max_length"],
                    suggestion="Break long speeches into multiple dialogue entries"
                ))
            elif len(speech) > speech_rules["recommended_max"]:
                violations.append(Violation(
                    file_path=file_path,
                    line_number=line_num,
                    rule_name="dialogue_speech_recommended",
                    severity="warning",
                    message=f"Dialogue speech longer than recommended: {len(speech)} chars (recommended max: {speech_rules['recommended_max']})",
                    actual_value=len(speech),
                    expected_value=speech_rules["recommended_max"]
                ))
        
        elif line.strip().startswith('*') and '**' in line:
            # It's a bullet point with bold text but doesn't match dialogue pattern
            violations.append(Violation(
                file_path=file_path,
                line_number=line_num,
                rule_name="dialogue_format",
                severity="warning",
                message="Dialogue doesn't follow expected format: * **Character:** (action) *\"speech\"*",
                actual_value=line.strip(),
                expected_value="* **Character:** (action) *\"speech\"*"
            ))
        
        return violations
    
    def _check_read_aloud(self, file_path: str, line_num: int, line: str) -> List[Violation]:
        """Check read-aloud text formatting."""
        violations = []
        
        read_aloud_text = line[1:].strip()  # Remove '>' prefix
        read_aloud_rules = self.rules["rules"]["content"]["read_aloud_line"]
        
        if len(read_aloud_text) > read_aloud_rules["max_length"]:
            violations.append(Violation(
                file_path=file_path,
                line_number=line_num,
                rule_name="read_aloud_line",
                severity="warning",
                message=f"Read-aloud line too long: {len(read_aloud_text)} chars (max: {read_aloud_rules['max_length']})",
                actual_value=len(read_aloud_text),
                expected_value=read_aloud_rules["max_length"]
            ))
        
        return violations
    
    def _check_line_length(self, file_path: str, line_num: int, line: str) -> List[Violation]:
        """Check overall line length."""
        violations = []
        
        line_rules = self.rules["rules"]["content"]["line_length"]
        line_length = len(line.rstrip('\n\r'))
        
        if line_length > line_rules["max_length"]:
            violations.append(Violation(
                file_path=file_path,
                line_number=line_num,
                rule_name="line_length",
                severity="warning",
                message=f"Line too long: {line_length} chars (max: {line_rules['max_length']})",
                actual_value=line_length,
                expected_value=line_rules["max_length"]
            ))
        
        return violations
    
    def _check_image(self, file_path: str, line_num: int, line: str) -> List[Violation]:
        """Check image formatting."""
        violations = []
        
        # Extract alt text from ![alt text](url)
        img_pattern = r'!\[([^\]]*)\]'
        matches = re.findall(img_pattern, line)
        
        img_rules = self.rules["rules"]["content"]["image_caption"]
        
        for alt_text in matches:
            if len(alt_text) > img_rules["max_length"]:
                violations.append(Violation(
                    file_path=file_path,
                    line_number=line_num,
                    rule_name="image_caption",
                    severity="warning",
                    message=f"Image alt text too long: {len(alt_text)} chars (max: {img_rules['max_length']})",
                    actual_value=len(alt_text),
                    expected_value=img_rules["max_length"]
                ))
        
        return violations
    
    def _check_document_structure(self, file_path: str, lines: List[str]) -> List[Violation]:
        """Check overall document structure."""
        violations = []
        
        # Check for excessive consecutive empty lines
        max_empty = self.rules["rules"]["structure"]["max_consecutive_empty_lines"]
        empty_count = 0
        
        for line_num, line in enumerate(lines, 1):
            if line.strip() == "":
                empty_count += 1
            else:
                if empty_count > max_empty:
                    violations.append(Violation(
                        file_path=file_path,
                        line_number=line_num - empty_count,
                        rule_name="max_consecutive_empty_lines",
                        severity="info",
                        message=f"Too many consecutive empty lines: {empty_count} (max: {max_empty})",
                        actual_value=empty_count,
                        expected_value=max_empty
                    ))
                empty_count = 0
        
        return violations
    
    def _suggest_header_fix(self, header_text: str) -> str:
        """Suggest how to fix a long header."""
        suggestions = []
        
        # Try abbreviations
        abbreviated = header_text
        for full, abbrev in self.rules["abbreviations"].items():
            abbreviated = abbreviated.replace(full, abbrev)
        
        if len(abbreviated) < len(header_text):
            suggestions.append(f"Use abbreviations: '{abbreviated}'")
        
        # Suggest splitting
        if " - " in header_text:
            parts = header_text.split(" - ", 1)
            suggestions.append(f"Split into: '# {parts[0]}' + '## {parts[1]}'")
        
        return "; ".join(suggestions) if suggestions else "Consider shortening or splitting"
    
    def lint_directory(self, directory: str, pattern: str = "**/*.md") -> List[Violation]:
        """Lint all markdown files in a directory."""
        all_violations = []
        
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory {directory} not found")
        
        markdown_files = list(directory_path.glob(pattern))
        
        for file_path in markdown_files:
            file_violations = self.lint_file(str(file_path))
            all_violations.extend(file_violations)
        
        return all_violations
    
    def generate_report(self, violations: List[Violation], output_file: str = None) -> str:
        """Generate a detailed violation report."""
        if not violations:
            report = "✅ No style violations found!\n"
        else:
            # Group violations by severity
            errors = [v for v in violations if v.severity == "error"]
            warnings = [v for v in violations if v.severity == "warning"]
            info = [v for v in violations if v.severity == "info"]
            
            report = f"""D&D Adventure Markdown Style Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=====================================

SUMMARY:
- 🔴 Errors: {len(errors)}
- ⚠️  Warnings: {len(warnings)}
- ℹ️  Info: {len(info)}
- Total Issues: {len(violations)}

"""
            
            # Report violations by severity
            for severity, icon, violation_list in [
                ("error", "🔴", errors),
                ("warning", "⚠️ ", warnings),
                ("info", "ℹ️ ", info)
            ]:
                if violation_list:
                    report += f"\n{icon} {severity.upper()} ({len(violation_list)}):\n"
                    report += "=" * 40 + "\n"
                    
                    for v in violation_list:
                        report += f"\nFile: {v.file_path}:{v.line_number}\n"
                        report += f"Rule: {v.rule_name}\n"
                        report += f"Issue: {v.message}\n"
                        if v.suggestion:
                            report += f"Suggestion: {v.suggestion}\n"
                        report += "-" * 40 + "\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report written to {output_file}")
        
        return report
    
    def generate_json_report(self, violations: List[Violation], output_file: str = None) -> Dict:
        """Generate a JSON format report for machine processing."""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_violations": len(violations),
                "errors": len([v for v in violations if v.severity == "error"]),
                "warnings": len([v for v in violations if v.severity == "warning"]),
                "info": len([v for v in violations if v.severity == "info"])
            },
            "violations": [
                {
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "rule_name": v.rule_name,
                    "severity": v.severity,
                    "message": v.message,
                    "actual_value": v.actual_value,
                    "expected_value": v.expected_value,
                    "suggestion": v.suggestion
                }
                for v in violations
            ]
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"JSON report written to {output_file}")
        
        return report_data


def main():
    """Command line interface for the markdown style linter."""
    parser = argparse.ArgumentParser(description="D&D Adventure Markdown Style Linter")
    parser.add_argument("path", help="File or directory to lint")
    parser.add_argument("--rules", default="style_rules.json", help="Rules file (default: style_rules.json)")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--json", help="Output JSON report file")
    parser.add_argument("--pattern", default="**/*.md", help="File pattern for directory scanning")
    parser.add_argument("--quiet", action="store_true", help="Only show summary")
    
    args = parser.parse_args()
    
    try:
        linter = MarkdownStyleLinter(args.rules)
        
        # Determine if path is file or directory
        path = Path(args.path)
        if path.is_file():
            violations = linter.lint_file(args.path)
        elif path.is_dir():
            violations = linter.lint_directory(args.path, args.pattern)
        else:
            print(f"Error: {args.path} is not a valid file or directory")
            return 1
        
        # Generate reports
        if args.json:
            linter.generate_json_report(violations, args.json)
        
        report = linter.generate_report(violations, args.output)
        
        if not args.quiet:
            print(report)
        else:
            errors = len([v for v in violations if v.severity == "error"])
            warnings = len([v for v in violations if v.severity == "warning"])
            info = len([v for v in violations if v.severity == "info"])
            print(f"Style check complete: {errors} errors, {warnings} warnings, {info} info")
        
        # Return non-zero exit code if errors found
        return 1 if any(v.severity == "error" for v in violations) else 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 