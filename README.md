# D&D Session Logs Website

**View the published site:**  
https://bytebard97.github.io/dnd_session_logs/

## Conda Environment

This project requires a dedicated conda environment. Please ensure you are using the correct environment before working on this project.

**To activate the environment:**

```bash
conda activate dnd-mkdocs
```

If you have not created the environment yet, you can do so with:

```bash
conda create -n dnd-mkdocs python=3.11
```

---

# dnd_session_logs
stores my D&D session logs to show to my players

## Adding New Journal Entries and Pages

1. **Add New Journal Entries:**
   - Place new Markdown files for session logs, recaps, or player/NPC dossiers in the appropriate folder under `site_src/` (e.g., `monday/`, `wednesday/`, `friday/`).
   - Use consistent naming (e.g., `log_session_XX.md`, `recap_session_XX.md`, or `npcs/NPC_NAME.md`).
   - For new NPCs or locations, add a Markdown file in the relevant dossier/compendium folder (e.g., `monday/npcs/`).

2. **Update Navigation:**
   - Edit `mkdocs.yml` to add new pages to the navigation under the correct campaign/group.
   - For dossiers/compendiums, add an index file (e.g., `npcs/index.md`) that links to all individual entries for easy browsing.

3. **Build and Deploy:**
   - Run `mkdocs build` to generate the updated site in the `docs/` folder.
   - Commit and push changes to GitHub. GitHub Pages will automatically update the live site.

## Browsable Dossier/Compendium
- Organize dossiers (NPCs, locations, items) in subfolders like `site_src/monday/npcs/`.
- Each dossier entry should be a separate Markdown file for easy linking and searching.
- Maintain an `index.md` in each dossier folder with a list of all entries.
- MkDocs search will let players quickly find any dossier entry by name or keyword.

## Advanced Processing
- The `util_scripts/` folder contains Python scripts for advanced or one-off Markdown processing (e.g., formatting fixes, batch splitting, or cleanup).
- These are not needed for routine updates, but are available for future bulk changes or maintenance.

## Third-Party Credits / Styling

This repo bundles two excellent open-source projects to give the logs an authentic D&D Player’s Handbook feel:

1. **Foundry VTT – 5e PHB Journal Styling**  
   GitHub: <https://github.com/sneat/foundry-vtt-5e-phb-journal-styling>  
   License: MIT  
   Included under `web_frameworks/foundry-vtt-5e-phb-journal-styling/`

2. **Solbera D&D Fonts**  
   GitHub: <https://github.com/Solbera/dnd-fonts>  
   License: OFL / custom per-font licenses (see the project)  
   Included under `web_frameworks/solbera-dnd-fonts/`

These folders are tracked as *git submodules*, keeping this repo lightweight while letting you pull upstream updates:

```bash
# initialise submodules after cloning
git submodule update --init --recursive

# pick up upstream improvements later
git submodule foreach git pull origin main
```

Their CSS / font files are embedded directly (via `--dnd-style`) when you run `generate_session_logs_html.py`, so no extra hosting or CDN is required.
