# dnd_session_logs
stores my D&amp;D session logs to show to my players

## Third-Party Credits / Styling

This repo bundles two excellent open-source projects to give the logs an authentic D&amp;D Player’s Handbook feel:

1. **Foundry VTT – 5e PHB Journal Styling**  
   GitHub: <https://github.com/sneat/foundry-vtt-5e-phb-journal-styling>  
   License: MIT  
   Included under `web_frameworks/foundry-vtt-5e-phb-journal-styling/`

2. **Solbera D&amp;D Fonts**  
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
