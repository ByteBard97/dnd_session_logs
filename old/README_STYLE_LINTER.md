# D&D Adventure Markdown Style Linter

A comprehensive style checking system for D&D adventure content that ensures consistent formatting
and prevents layout issues in generated HTML.

## Quick Start

```bash

# Run style check on all adventure content

python run_style_check.py

# Check a specific file

python markdown_style_linter.py ../adventure/central_pumping_station/central_pumping_station.md

# Check with custom rules file

python markdown_style_linter.py ../adventure --rules custom_rules.json
```

## System Components

### 1. **`style_rules.json`**- Configuration File

Defines all style rules including:* Header length limits (H1, H2, H3, H4)
*Content guidelines (dialogue, read-aloud text, images)* Formatting patterns
*Mobile responsiveness limits* Common abbreviations

### 2. **`markdown_style_linter.py`**- Main Linter

Core Python script that:* Parses markdown files line by line
*Checks against configurable rules* Generates detailed violation reports
*Provides intelligent suggestions for fixes

### 3.**`run_style_check.py`**- Convenience Script

Simple script that:* Scans the entire `../adventure/` directory
*Generates both text and JSON reports* Shows summary statistics
*Creates reports in `style_reports/` directory

### 4.**Style Guide Documentation**

* **`STYLE_GUIDE.md`**- Complete formatting guidelines* **`STYLE_QUICK_REFERENCE.md`** - At-a-glance limits and fixes

## Command Line Usage

### Basic Commands

```bash

# Check all adventure files

python run_style_check.py

# Check specific file

python markdown_style_linter.py path/to/file.md

# Check directory with pattern

python markdown_style_linter.py ../adventure --pattern "**/*.md"

# Generate JSON report only

python markdown_style_linter.py ../adventure --json violations.json --quiet

# Use custom rules

python markdown_style_linter.py ../adventure --rules my_rules.json
```

### Output Options

```bash

# Save text report to file

python markdown_style_linter.py ../adventure --output style_report.txt

# Generate both text and JSON reports

python markdown_style_linter.py ../adventure --output report.txt --json report.json

# Quiet mode (summary only)

python markdown_style_linter.py ../adventure --quiet
```

## Rule Configuration

### Header Length Limits

```json
{
  "rules": {
    "headers": {
      "h1": {
        "ideal_max": 45,
        "absolute_max": 60,
        "mobile_max": 40
      }
    }
  }
}
```

### Content Rules

```json
{
  "content": {
    "dialogue_character_name": {"max_length": 15},
    "dialogue_speech": {"max_length": 200, "recommended_max": 120},
    "read_aloud_line": {"max_length": 100}
  }
}
```

### Custom Abbreviations

```json
{
  "abbreviations": {
    "Guide": "G.",
    "Reference": "Ref.",
    "Game Master": "GM"
  }
}
```

## Violation Types

### 🔴 Errors (Break Layout)

*Headers exceeding absolute maximums* Severely overlong dialogue
*Missing required formatting

### ⚠️ Warnings (Style Issues)
* Headers exceeding ideal limits
*Long lines that affect readability* Inconsistent formatting

### ℹ️ Info (Minor Issues)

*Very short headers* Excessive empty lines
*Style suggestions

## Example Output

```
📊 STYLE CHECK RESULTS:
🔴 Errors: 5
⚠️  Warnings: 23
ℹ️  Info: 12
📄 Total Issues: 40
🔍 First few issues:
   🔴 adventure/cistern_spillways/cistern_puzzle_guide.md:1 - Header too long: 58 chars (max: 60)
   ⚠️  adventure/central_pumping_station/central_pumping_station.md:35 - Dialogue speech longer than recommended: 145 chars
```

## Common Fixes

### Long Headers
**Problem:**```markdown

# Cistern & Spillways - Puzzle Solutions Guide (GM Reference)

```**Solutions:**```markdown

# Option 1: Split headers

# Cistern & Spillways

## Puzzle Solutions Guide (GM Reference)

# Option 2: Abbreviate

# Cistern & Spillways - Puzzle Guide (GM Ref.)

# Option 3: Restructure

# Cistern & Spillways
*GM Reference: Puzzle Solutions Guide*```

### Long Dialogue
**Problem:**```markdown*   **Petros:** *"This is an extremely long piece of dialogue that goes on and on about the technical details of the pumping system and really should be broken up into smaller, more manageable chunks for better readability and player engagement."*```**Fix:**```markdown*   **Petros:** *"This is getting technical. The pumping system is complex."*
* **Petros:** *"Let me break it down for you step by step."*```

### Long Lines
**Problem:**```markdown
> This is a very long read-aloud description that extends far beyond the recommended line length and should probably be broken into shorter, more digestible sentences.
```**Fix:**```markdown
> This is a shorter read-aloud description. It uses multiple sentences for better pacing.
> Each sentence is more digestible and maintains dramatic tension.
```

## Integration with Build Process

### Pre-commit Hook

```bash

#!/bin/bash

# .git/hooks/pre-commit

cd web_version
python run_style_check.py
if [ $? -ne 0 ]; then
    echo "Style violations found. Run 'python run_style_check.py' to see details."
    exit 1
fi
```

### CI/CD Integration

```yaml

# GitHub Actions example
* name: Run Style Check
  run: |
    cd web_version
    python run_style_check.py
    if [ $? -ne 0 ]; then
      echo "Style violations found"
      exit 1
    fi
```

## Customizing Rules

### Adding New Rules

1. Edit `style_rules.json` to add new rule definitions
2. Modify `markdown_style_linter.py` to implement the checking logic
3. Test with sample content
4. Update documentation

### Example: Adding Table Size Limits

```json
{
  "rules": {
    "content": {
      "table_width": {
        "max_columns": 6,
        "description": "Tables should not exceed 6 columns for readability"
      }
    }
  }
}
```

## Reports

### Text Report (`style_report.txt`)

*Human-readable format* Grouped by severity level
*Includes suggestions for fixes* Perfect for development review

### JSON Report (`style_report.json`)

*Machine-readable format* Structured data for automation
*Suitable for CI/CD integration* Can be processed by other tools

## Best Practices

1. **Run checks regularly**during content creation
2.**Fix errors first**before warnings
3.**Use abbreviations**from the approved list
4.**Split long headers**rather than using awkward abbreviations
5.**Break up long dialogue**for better readability
6.**Test on mobile**for responsive design issues

## Troubleshooting

### Common Issues
* **"Rules file not found"**- Ensure `style_rules.json` is in the correct directory* **"No violations found"**- Check that markdown files exist in the specified path* **"Permission denied"** - Ensure write permissions for report output directory

### Debug Mode

Add debug output by modifying the linter to print rule matching:
```python

# Add to _check_header method for debugging

print(f"Checking header: {header_text} (length: {header_length})")
```
This style linter system ensures your D&D adventure content maintains consistent, professional formatting while preventing layout issues in the generated HTML.
