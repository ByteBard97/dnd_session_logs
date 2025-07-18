# D&D Session Log Linting System

A lightweight markdown linting system specifically designed for D&D session logs, adapted from a
more comprehensive adventure content linter.

## Quick Start

```bash

# Check all session logs for issues

python lint_session_logs.py quest_logs/ --check --recursive

# Fix all issues automatically

python lint_session_logs.py quest_logs/ --fix --recursive

# Check specific file

python lint_session_logs.py quest_logs/friday/session_recap.md --check

# Fix specific file

python lint_session_logs.py quest_logs/friday/session_recap.md --fix
```

## What It Fixes

### Automatic Fixes

* **Empty headers**- Removes headers with no text (like `# `)* **Session header formatting**- Standardizes to `# Session X` or `# Session X: Title`* **Corrupted footnote numbers**- Removes patterns like `171717171717`* **Spacing issues**- Proper spacing around headers and paragraphs* **Bullet formatting** - Standardizes to use `*` for bullets
* **Emphasis formatting** - Standardizes bold/italic to use `**text**` and `*text*`
* **Long lines**- Intelligently wraps at natural break points (sentences, clauses, D&D terms)

### Detection (Issues Found)
* Lines over 100 characters
*Empty headers* Inconsistent formatting
*Missing spacing around headers

## Files in This System
* **`session_log_auto_fixer.py`**- Core auto-fixing logic* **`intelligent_line_wrapper.py`**- Smart line wrapping for D&D content* **`lint_session_logs.py`**- Main script that combines both tools* **`session_log_style_rules.json`**- Configuration rules* **`setup_session_log_linting.sh`**- Setup script with optional git hooks

## Example Issues Found

From your current session logs:* 562 long lines in Friday quest log
*433 long lines in Wednesday quest log* 110 long lines in Monday quest log
*Multiple empty headers across files* 1,400+ total formatting issues across all files

## Integration Options

### 1. Manual Usage

Run the linter when you finish writing session notes:
```bash
python lint_session_logs.py quest_logs/friday/session_recap.md --fix
```

### 2. Pre-commit Hook

Automatically check files before committing:
```bash
./setup_session_log_linting.sh

# Choose 'y' when prompted for git hook

```

### 3. Batch Processing

Fix all files at once:
```bash
python lint_session_logs.py quest_logs/ --fix --recursive
```

## D&D-Specific Features

### Smart Line Breaking

Breaks lines at natural points like:
*End of sentences in dialogue* Before dice rolls (`DC 15`, `2d6+3`)
*Before skill checks (`Make a Perception check`)* Before party actions (`The party decides...`)
*At clause boundaries (`and`, `but`, `which`)

### Session Log Formatting
* Standardizes session headers
*Handles bullet points for events* Preserves D&D terminology and abbreviations
*Maintains readability for long narrative sections

## Abbreviations Used

When headers are too long, these abbreviations are applied:* Session → Sess.
*Character → Char* Investigation → Invest
*Encounter → Enc* Dungeon Master → DM
*Non-Player Character → NPC* Player Character → PC

## Benefits

1. **Consistent formatting**across all session logs
2.**Better readability**with proper line wrapping
3.**Faster HTML generation**with cleaner markdown
4.**Reduced manual formatting**time
5.**Fewer display issues**in GitHub and HTML output

## Safety
* **Non-destructive by default**- Use `--check` to see what would be changed* **Backup recommended**- The `--fix` mode modifies files in place* **Selective fixing**- Can target specific files or directories* **Reversible** - Changes are standard markdown formatting improvements
This system will significantly improve the consistency and readability of your session logs while
saving time on manual formatting!
