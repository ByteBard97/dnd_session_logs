#!/usr/bin/env python3
"""generate_session_logs_html.py

Convert one or many Markdown session log / recap files into a single self-contained
HTML file that can be uploaded directly to a static hosting service.

The script is intentionally lightweight – it does **not** attempt to inline images,
fonts, or custom D&D styling.  It simply performs Markdown → HTML conversion and
wraps the result in a minimal HTML scaffold.  The generated file works offline and
renders well on modern browsers.

Usage examples
--------------
# Convert a single markdown file
python generate_session_logs_html.py ../game_transcripts_for_reference/session22_may6.txt

# Convert all .md / .txt files inside a folder (alphabetical order)
python generate_session_logs_html.py ../game_transcripts_for_reference/ --output session_logs.html

Optional arguments
------------------
--output <file>      Set custom output filename (default: session_logs.html)
--title  <string>    Set custom document <title>  (default: "D&D Session Logs")
--toc                Include a generated Table of Contents linking to each session
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

try:
    import markdown  # type: ignore
except ImportError:
    sys.stderr.write(
        "The 'markdown' package is required. Install with: pip install markdown\n"
    )
    sys.exit(1)

CSS_RESET = """
/* Simple, readable defaults */
body {
  margin: 2rem auto;
  max-width: 800px;
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.6;
  color: #222;
  background: #fafafa;
}
h1, h2, h3, h4, h5, h6 {
  font-family: "Palatino Linotype", "Book Antiqua", Palatino, serif;
  margin-top: 1.5em;
}
code, pre {
  background: #f4f4f4;
  padding: 2px 4px;
  border-radius: 4px;
}
pre {
  overflow-x: auto;
  padding: 1em;
}
a {
  color: #0066cc;
}
"""

def collect_markdown_files(path: Path) -> List[Path]:
    """Return a list of markdown/text files to process.

    If *path* is a file, return [path].
    If *path* is a directory, return all .md/.markdown/.txt files inside (sorted).
    """
    if path.is_file():
        return [path]

    md_exts = {".md", ".markdown", ".txt"}
    files = [p for p in sorted(path.iterdir()) if p.suffix.lower() in md_exts]
    if not files:
        raise FileNotFoundError(f"No markdown/text files found in directory: {path}")
    return files


def convert_files_to_html(files: List[Path], include_toc: bool = False) -> str:
    """Convert each markdown file and concatenate to a single HTML string."""
    html_parts: List[str] = []
    toc_entries: List[str] = []

    md = markdown.Markdown(extensions=["extra", "toc", "tables", "sane_lists"])

    for f in files:
        session_id = f.stem.replace("_", " ").replace("-", " ")
        heading_html = f"<h2 id=\"{f.stem}\">{session_id.title()}</h2>"
        toc_entries.append(f"<li><a href=\"#{f.stem}\">{session_id.title()}</a></li>")

        with f.open("r", encoding="utf-8") as fp:
            md_text = fp.read()
            # Remove inline anchor tags of the form {#anchor-id}
            import re
            md_text = re.sub(r"\s*\{#[-a-zA-Z0-9_:.]+\}", "", md_text)

            # DEBUG: Report any raw '####' markdown headers before conversion
            for line_no, line in enumerate(md_text.splitlines(), start=1):
                if line.lstrip().startswith("#### "):
                    print(f"[DEBUG] Raw #### header in {f.name} line {line_no}: {line.strip()[:120]}")

        body_html = md.convert(md_text)

        # DEBUG: Detect remaining literal '####' sequences in rendered HTML (should not happen)
        if '####' in body_html:
            print(f"[DEBUG] Literal #### found in rendered HTML for {f.name}; applying fallback conversion.")

        # Handle headings missed and wrapped in <p> tags
        header_patterns = [
            (r'<p>####\s+(.+?)</p>', r'<h4>\1</h4>'),
            (r'<p>###\s+(.+?)</p>', r'<h3>\1</h3>'),
            (r'<p>##\s+(.+?)</p>', r'<h2>\1</h2>'),
            (r'<p>#\s+(.+?)</p>', r'<h1>\1</h1>'),
            (r'^####\s+(.+)$', r'<h4>\1</h4>'),
            (r'^###\s+(.+)$', r'<h3>\1</h3>'),
            (r'^##\s+(.+)$', r'<h2>\1</h2>'),
            (r'^#\s+(.+)$', r'<h1>\1</h1>'),
        ]
        for pattern, repl in header_patterns:
            body_html = re.sub(pattern, repl, body_html, flags=re.MULTILINE)

        # Demote oversized <h1> headings (often used as paragraph markers in original markdown) to normal paragraphs.
        # We determine "oversized" after stripping any nested HTML tags (e.g., <em>, <strong>).  If the plain text
        # exceeds ~120 characters or ~25 words, we treat it as a paragraph, not a heading.
        def _demote_if_long(match: "re.Match[str]") -> str:  # type: ignore[name-defined]
            full_tag, attrs, inner = match.group(0), match.group(1), match.group(2)
            plain = re.sub(r"<[^>]+>", "", inner)  # strip nested tags
            if len(plain) > 120 or len(plain.split()) > 25:
                return f"<p>{inner}</p>"
            return full_tag

        body_html = re.sub(r"<h1([^>]*)>(.*?)</h1>", _demote_if_long, body_html, flags=re.DOTALL)

        # DEBUG: After fallback, double-check that no #### remain
        if '####' in body_html:
            print(f"[WARN] #### still present in HTML for {f.name} after fallback conversion – manual inspection recommended.")

        html_parts.append(heading_html)
        html_parts.append(body_html)

        # Reset markdown instance state between documents
        md.reset()

    if include_toc:
        toc_html = "<nav><h2>Table of Contents</h2><ul>" + "\n".join(toc_entries) + "</ul></nav>"
        html_parts.insert(0, toc_html)

    return "\n\n".join(html_parts)


def build_full_html(body_html: str, title: str, use_dnd: bool) -> str:
    """Wrap *body_html* inside a basic HTML5 scaffold with optional D&D PHB styling."""
    if use_dnd:
        try:
            from web_version.generate_offline_adventure_enhanced import get_dnd_phb_css  # type: ignore
            phb_css = get_dnd_phb_css()
        except ModuleNotFoundError:
            # Attempt dynamic import using file path (handles running script directly)
            enh_path = Path(__file__).parent / "generate_offline_adventure_enhanced.py"
            if enh_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("generate_offline_adventure_enhanced", enh_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)  # type: ignore
                    phb_css = module.get_dnd_phb_css()  # type: ignore
                else:
                    phb_css = CSS_RESET
            else:
                sys.stderr.write("[WARN] Could not locate enhanced generator for D&D styling; falling back to minimal CSS.\n")
                phb_css = CSS_RESET
        except Exception as e:  # pragma: no cover
            sys.stderr.write(f"[WARN] Error loading D&D styling ({e}); falling back to default.\n")
            phb_css = CSS_RESET

        # Modern interactive features JavaScript
        interactive_js = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Theme toggle functionality
            const themeToggle = document.getElementById('theme-toggle');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const currentTheme = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');
            
            document.documentElement.setAttribute('data-theme', currentTheme);
            
            if (themeToggle) {
                themeToggle.textContent = currentTheme === 'dark' ? '☀️ Light' : '🌙 Dark';
                themeToggle.addEventListener('click', function() {
                    const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                    document.documentElement.setAttribute('data-theme', newTheme);
                    localStorage.setItem('theme', newTheme);
                    this.textContent = newTheme === 'dark' ? '☀️ Light' : '🌙 Dark';
                });
            }
            
            // Back to top button
            const backToTop = document.getElementById('back-to-top');
            if (backToTop) {
                window.addEventListener('scroll', function() {
                    if (window.scrollY > 300) {
                        backToTop.classList.add('visible');
                    } else {
                        backToTop.classList.remove('visible');
                    }
                });
                
                backToTop.addEventListener('click', function() {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                });
            }
            
            // Search functionality
            const searchBox = document.getElementById('search-box');
            if (searchBox) {
                searchBox.addEventListener('input', function() {
                    const query = this.value.toLowerCase();
                    const allText = document.querySelectorAll('.phb-container h1, .phb-container h2, .phb-container h3, .phb-container p');
                    
                    allText.forEach(element => {
                        const text = element.textContent.toLowerCase();
                        if (query && text.includes(query)) {
                            element.style.backgroundColor = 'var(--phb-border-primary)';
                            element.style.padding = '0.2em';
                            element.style.borderRadius = '4px';
                        } else {
                            element.style.backgroundColor = '';
                            element.style.padding = '';
                            element.style.borderRadius = '';
                        }
                    });
                });
                
                // Clear search on escape
                searchBox.addEventListener('keydown', function(e) {
                    if (e.key === 'Escape') {
                        this.value = '';
                        this.dispatchEvent(new Event('input'));
                    }
                });
            }
            
            // Collapsible sections
            document.querySelectorAll('h2, h3').forEach(header => {
                header.classList.add('collapsible');
                header.addEventListener('click', function() {
                    const content = this.nextElementSibling;
                    if (content) {
                        this.classList.toggle('collapsed');
                        content.classList.toggle('collapsed');
                        
                        if (content.classList.contains('collapsed')) {
                            content.style.maxHeight = '0';
                        } else {
                            content.style.maxHeight = content.scrollHeight + 'px';
                        }
                    }
                });
            });
            
            // Smooth loading animation
            document.body.classList.add('loading');
            
            // Image lightbox effect (simple version)
            document.querySelectorAll('.phb-container img').forEach(img => {
                img.addEventListener('click', function() {
                    const modal = document.createElement('div');
                    modal.style.cssText = `
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0,0,0,0.9);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        z-index: 2000;
                        cursor: pointer;
                    `;
                    
                    const modalImg = document.createElement('img');
                    modalImg.src = this.src;
                    modalImg.style.cssText = `
                        max-width: 90%;
                        max-height: 90%;
                        border-radius: 8px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
                    `;
                    
                    modal.appendChild(modalImg);
                    document.body.appendChild(modal);
                    
                    modal.addEventListener('click', function() {
                        document.body.removeChild(modal);
                    });
                });
            });
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + K for search focus
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    if (searchBox) searchBox.focus();
                }
                
                // Escape to clear search
                if (e.key === 'Escape' && searchBox) {
                    searchBox.value = '';
                    searchBox.dispatchEvent(new Event('input'));
                }
            });
        });
        </script>
        """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="D&D Session Logs with Enhanced Player's Handbook Styling" />
  <title>{title}</title>
  <style>{phb_css}</style>
</head>
<body>
  <nav class="nav-header">
    <a href="/" class="nav-title">{title}</a>
    <div class="nav-controls">
      <input type="text" id="search-box" class="search-box" placeholder="Search sessions... (Ctrl+K)" />
      <button id="theme-toggle" class="theme-toggle">🌙 Dark</button>
    </div>
  </nav>
  
  <div class="phb-container">
    {body_html}
  </div>
  
  <button id="back-to-top" class="back-to-top" title="Back to top">↑</button>
  
  {interactive_js}
</body>
</html>"""
    else:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>{CSS_RESET}</style>
</head>
<body>
  <h1>{title}</h1>
  {body_html}
</body>
</html>"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert markdown session logs to a single HTML file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to a markdown file or a directory containing markdown/text files.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("session_logs.html"),
        help="Output HTML filename.",
    )
    parser.add_argument(
        "--title",
        "-t",
        type=str,
        default="D&D Session Logs",
        help="Document title (<title> and top-level H1).",
    )
    parser.add_argument(
        "--toc",
        action="store_true",
        help="Include a generated Table of Contents at the top of the document.",
    )
    parser.add_argument(
        "--separate",
        action="store_true",
        help="When input_path is a directory, generate one HTML file per markdown file (placed next to each source) instead of concatenating them into a single document.",
    )
    parser.add_argument(
        "--dnd-style",
        action="store_true",
        help="Embed D&D Player's Handbook styling (Foundry PHB CSS + embedded Solbera fonts) for authentic look.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = collect_markdown_files(args.input_path)
    # Always output generated HTML into the repository-level "docs" folder so it can be served by GitHub Pages.
    docs_dir = (Path(__file__).parent / "docs").resolve()
    docs_dir.mkdir(parents=True, exist_ok=True)

    if args.separate and args.input_path.is_dir():
        print(f"[INFO] Generating individual HTML files for {len(files)} source files…")
        for src in files:
            body_html = convert_files_to_html([src], include_toc=False)
            # Use per-file title if not default
            per_title = src.stem.replace("_", " ").title()
            full_html = build_full_html(body_html, per_title, args.dnd_style)
            out_path = docs_dir / f"{src.stem}.html"
            out_path.write_text(full_html, encoding="utf-8")
            # Display a user-friendly path without raising errors for mixed absolute/relative cases
            try:
                display_path = out_path.relative_to(Path.cwd()) if out_path.is_absolute() else out_path
            except ValueError:
                display_path = out_path
            print(f"  • Wrote {display_path}")
    else:
        print(f"[INFO] Converting {len(files)} file(s) to a single HTML…")
        body_html = convert_files_to_html(files, include_toc=args.toc)
        full_html = build_full_html(body_html, args.title, args.dnd_style)

        output_path = args.output if args.output.is_absolute() else docs_dir / args.output.name
        output_path.write_text(full_html, encoding="utf-8")
        print(f"[SUCCESS] Wrote {output_path.resolve()}")


if __name__ == "__main__":
    main() 