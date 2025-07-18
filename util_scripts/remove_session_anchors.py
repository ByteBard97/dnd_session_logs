import os
import re

def remove_all_anchors(directory):
    # Remove any {#...} anchor, including optional leading whitespace
    pattern = re.compile(r'\s*\{#[^}]+\}')
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.endswith('.md'):
                path = os.path.join(root, fname)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                new_content = pattern.sub('', content)
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Cleaned {path}")

if __name__ == '__main__':
    remove_all_anchors('site_src') 