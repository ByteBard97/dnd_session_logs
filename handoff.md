# Handoff Document: MkDocs Refactoring Issues

## 1. Original Goal

The primary objective was to refactor the `mkdocs.yml` file to improve maintainability. The original file contained a very large, manually curated `nav` section that listed every single session log and recap file. The goal was to replace this with a more automated, modular system.

## 2. Changes Implemented

To achieve this, the following steps were taken:

1.  **New Conda Environment:** A new conda environment named `dnd-mkdocs` was created and the necessary packages (`mkdocs`, `mkdocs-material`) were installed.
2.  **Plugin Installation:** The `mkdocs-awesome-pages-plugin` was installed to handle navigation automation.
3.  **`mkdocs.yml` Refactor:**
    *   The `awesome-pages` plugin was added to the `plugins` section.
    *   The entire manual `nav` section was removed.
    *   The `use_directory_urls` setting was changed from `true` to `false` in an attempt to create cleaner URLs and fix linking issues.
4.  **File Reorganization:**
    *   For each campaign (`monday`, `wednesday`, `friday`), new subdirectories named `logs` and `recaps` were created inside `site_src`.
    *   All existing `log_session_*.md` and `recap_session_*.md` files were moved from the campaign root into these new respective subdirectories.
5.  **Navigation Configuration:** `.pages` files were created in the root of `site_src` and within each campaign directory to control the navigation structure.

## 3. Current Problems

Despite the refactoring, the local development server (`mkdocs serve`) is not functioning correctly. The key issues are:

1.  **404 Not Found Errors:** Critical pages, most notably the Player Character sheets (`players/pcs.md`) and Epic Paths (`players/epic_paths.md`), are consistently returning 404 errors. The server logs show repeated failed `GET` requests for these files.
2.  **Broken Navigation Links:** The navigation sidebar does not render correctly. Sections like "Recaps" and "Quest Logs" do not expand to show the session files and instead act as dead links.
3.  **URL Structure Confusion:** It is unclear if the combination of the `awesome-pages` plugin and the `use_directory_urls: false` setting is causing a pathing conflict, leading to the 404s.

## 4. Summary

The project is in a broken state after a significant refactoring attempt. The file structure in `site_src` is now well-organized, but the MkDocs configuration is failing to correctly map this structure to a functional website. The next step should be to diagnose and fix the configuration within `mkdocs.yml` and the various `.pages` files to correctly generate the site navigation and resolve the widespread 404 errors. 