# MkDocs Material collapsible navigation with awesome-pages: Why it's not working and how to fix it

The core issue with your setup is that **awesome-pages plugin's `collapse: true` feature only works for directories containing a single markdown file**, not folders with multiple files like your 'Recaps' and 'Quest Logs' sections. This is a fundamental design limitation of the plugin, not a configuration error.

## Why your current setup isn't working

The awesome-pages plugin (now renamed to `mkdocs-awesome-nav`) was designed to solve a specific problem: eliminating unnecessary nesting when a folder contains only one file. The `collapse` functionality was never intended to create accordion-style collapsible sections for multi-file folders. When the plugin documentation mentions "collapse," it means collapsing the folder structure entirely so single-file directories don't create redundant navigation levels.

**Your configuration with `navigation.sections` enabled and `navigation.expand` disabled is actually correct** for Material theme's navigation behavior. However, awesome-pages simply doesn't provide the collapsible multi-file folder functionality you're looking for. The `.pages` files with `collapse: true` are being ignored for multi-file folders because the plugin explicitly checks for single-file directories before applying this setting.

## The exact .pages file syntax (and why it won't help)

The correct syntax for `.pages` files would be:
```yaml
# .pages file in a directory
collapse: true
```

Or globally in `mkdocs.yml`:
```yaml
plugins:
  - awesome-pages:
      collapse_single_pages: true
```

However, **this will only work for folders containing exactly one markdown file**. For a folder structure like:
```
docs/
├─ Recaps/
│  ├─ session-01.md
│  ├─ session-02.md
│  └─ session-03.md
```
The collapse functionality simply won't activate, regardless of your configuration.

## Working configurations with current versions

Here's what actually works with MkDocs Material (v9.x) and awesome-pages/awesome-nav (v2.x) as of 2025:

### Configuration for clickable sections with manual expand/collapse
```yaml
# mkdocs.yml
theme:
  name: material
  features:
    - navigation.sections    # Groups top-level sections
    - navigation.indexes     # Makes sections clickable when they have index.md
    # Don't include navigation.expand to keep sections collapsed by default

plugins:
  - search
  - awesome-pages:
      filename: .pages      # or .nav.yml for newer syntax
```

With this setup and an `index.md` in each folder, sections become clickable headers that link to the index page, but they still won't have true accordion-style collapse behavior for the child pages.

## Why Material theme's navigation.sections conflicts with awesome-pages

Multiple GitHub issues confirm that `navigation.sections` and awesome-pages have architectural incompatibilities. Material theme's navigation system always expands the path to the currently active page and collapses other paths. This behavior is hardcoded and can't be overridden per folder. The theme treats navigation state as ephemeral - it's recalculated on each page load based on the current page location.

## Alternative approaches that actually work

### Option 1: Custom JavaScript solution
Add custom JavaScript to create true collapsible behavior:

```yaml
# mkdocs.yml
extra_javascript:
  - javascripts/custom-nav.js
```

```javascript
// docs/javascripts/custom-nav.js
document.addEventListener('DOMContentLoaded', function() {
    // Store collapse state in localStorage
    const navSections = document.querySelectorAll('.md-nav__item--section');
    
    navSections.forEach(section => {
        const toggle = section.querySelector('.md-nav__link');
        const key = `nav-collapsed-${toggle.textContent.trim()}`;
        
        // Restore saved state
        if (localStorage.getItem(key) === 'true') {
            section.classList.add('collapsed');
        }
        
        toggle.addEventListener('click', function(e) {
            if (e.target === toggle) {
                e.preventDefault();
                section.classList.toggle('collapsed');
                localStorage.setItem(key, section.classList.contains('collapsed'));
            }
        });
    });
});
```

### Option 2: Use manual navigation definition
Define your navigation structure explicitly in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - Recaps:
    - Overview: recaps/index.md
    - Session 1: recaps/session-01.md
    - Session 2: recaps/session-02.md
  - Quest Logs:
    - Overview: quest-logs/index.md
    - Quest 1: quest-logs/quest-01.md
    - Quest 2: quest-logs/quest-02.md
```

This gives you the structure but still relies on Material theme's default expand/collapse behavior.

### Option 3: Template override for custom navigation
Create a custom navigation template that implements true collapsible sections:

```yaml
# mkdocs.yml
theme:
  name: material
  custom_dir: overrides
```

Then override the navigation templates in `overrides/partials/` to implement custom collapse logic.

## Examples of working folder structures

For the best experience with current limitations, structure your content like this:

```
docs/
├── recaps/
│   ├── index.md          # Overview page (makes folder clickable)
│   ├── .pages            # For ordering only
│   ├── session-01.md
│   ├── session-02.md
│   └── session-03.md
├── quest-logs/
│   ├── index.md          # Overview page
│   ├── .pages            # For ordering only
│   ├── quest-01.md
│   └── quest-02.md
```

With `.pages` files containing only ordering directives:
```yaml
# .pages file
order: asc
arrange:
  - index.md
  - ...        # Other files in natural order
```

## GitHub discussions explaining the limitation

The awesome-pages maintainer and MkDocs Material maintainer have both acknowledged these limitations in various GitHub issues. The consensus is that true collapsible multi-file folders aren't supported by awesome-pages, and Material theme's navigation behavior is designed around always showing the path to the active page. Several users have requested this feature, but it would require fundamental changes to how both the plugin and theme handle navigation state.

The most viable solution for your use case is implementing custom JavaScript to add collapsible behavior on top of the existing navigation structure, or restructuring your content to work within the current limitations. Alternative themes like MkDocs Windmill have been reported to have more flexible navigation behavior if you're open to switching themes.