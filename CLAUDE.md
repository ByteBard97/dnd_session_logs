# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

This project requires the `dnd-mkdocs` conda environment:

```bash
conda activate dnd-mkdocs
```

## Build and Development Commands

### Build Static Site
```bash
mkdocs build
```
- Generates the complete static site in the `docs/` directory from `site_src/` markdown files
- Use this for deploying to GitHub Pages

### Development Server
NEVER run `mkdocs serve` - this is explicitly forbidden per project rules

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Project Architecture

This is a **MkDocs-based D&D campaign documentation site** with the following structure:

### Content Organization
- **`site_src/`** - Source markdown files organized by campaign day:
  - `monday/` - Monday campaign logs, player info, and recaps
  - `wednesday/` - Wednesday campaign logs, player info, and recaps  
  - `friday/` - Friday campaign logs, player info, and recaps
- **`docs/`** - Generated HTML output for GitHub Pages deployment
- **`quest_logs/`** - Raw session logs before processing
- **`site_html/`** - Alternative HTML output directory

### Key Components
- **Session Logs**: `log_session_XX.md` files contain detailed session transcripts
- **Recaps**: `recap_session_XX.md` files contain session summaries
- **Player Characters**: `pcs.md` files with character information and portraits
- **Styling**: Custom D&D 5e Player's Handbook theming via `custom_dd_style.css` and bundled fonts

### Processing Scripts
The `util_scripts/` directory contains Python utilities for content management:
- `split_sessions.py` - Split large markdown files into individual session files
- `generate_html_from_split.py` - Convert processed markdown to HTML
- `cleanup_markdown.py` - Fix formatting issues in markdown files
- `fix_bold_spacing.py` - Standardize bold text formatting
- `remove_session_anchors.py` - Clean up anchor links in session files

### Configuration
- **`mkdocs.yml`** - MkDocs configuration with Material theme and plugins
- **Navigation** - Automatically generated using awesome-pages plugin from file structure
- **Styling** - Integrates custom D&D fonts (Bookinsanity, Scaly Sans, etc.) and PHB styling

## Content Updates

1. **Add new session logs/recaps**: Place `.md` files in appropriate campaign folder under `site_src/`
2. **Update player information**: Edit `pcs.md` files in campaign folders
3. **Build and deploy**: Run `mkdocs build` then commit/push to trigger GitHub Pages update

## Key Project Rules

- **Always edit code directly** - Never instruct users to make changes
- **Use conda environment** - Always ensure `dnd-mkdocs` environment is active
- **Never run mkdocs serve** - Development server is explicitly forbidden
- **Maintain D&D theming** - Preserve authentic Player's Handbook styling and fonts