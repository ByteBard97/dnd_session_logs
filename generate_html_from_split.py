import os
import markdown
from pathlib import Path

SITE_SRC = 'site_src'
SITE_HTML = 'site_html'

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Georgia', serif; max-width: 800px; margin: 2em auto; padding: 2em; background: #f9f9f9; color: #222; }}
        h1, h2, h3, h4 {{ color: #2d2d6a; }}
        pre, code {{ background: #eee; padding: 2px 4px; border-radius: 3px; }}
        a {{ color: #2d2d6a; }}
        nav {{ margin-bottom: 2em; }}
    </style>
</head>
<body>
<nav><a href="../index.html">Back to Index</a></nav>
{content}
</body>
</html>
'''

def get_title(md_text, fallback):
    for line in md_text.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return fallback

def main():
    for group in os.listdir(SITE_SRC):
        group_dir = os.path.join(SITE_SRC, group)
        if not os.path.isdir(group_dir):
            continue
        out_group_dir = os.path.join(SITE_HTML, group)
        os.makedirs(out_group_dir, exist_ok=True)
        for fname in os.listdir(group_dir):
            if fname.endswith('.md'):
                src_path = os.path.join(group_dir, fname)
                with open(src_path, 'r', encoding='utf-8') as f:
                    md_text = f.read()
                html_content = markdown.markdown(md_text, extensions=['extra', 'toc'])
                title = get_title(md_text, fname)
                html = HTML_TEMPLATE.format(title=title, content=html_content)
                out_name = fname.replace('.md', '.html')
                out_path = os.path.join(out_group_dir, out_name)
                with open(out_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(html)
                print(f"Wrote {out_path}")

if __name__ == '__main__':
    main() 