import os
import re

def cleanup_markdown(directory):
    # Patterns to remove
    patterns_to_remove = [
        re.compile(r'^\(from.*\)\s*$', re.MULTILINE),
        re.compile(r'^\[cite:.*\]\s*$', re.MULTILINE),
    ]
    # Pattern to fix headers (####Heading -> #### Heading)
    header_fix_pattern = re.compile(r'^(#{1,6})([^ #\n])', re.MULTILINE)
    # Pattern to remove leading spaces before headers
    header_leading_space_pattern = re.compile(r'^[ \t]+(#{1,6} )', re.MULTILINE)

    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.endswith('.md'):
                path = os.path.join(root, fname)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                original_content = content
                # Remove unwanted lines
                for pat in patterns_to_remove:
                    content = pat.sub('', content)
                # Fix headers missing a space
                content = header_fix_pattern.sub(r'\1 \2', content)
                # Remove leading spaces before headers
                content = header_leading_space_pattern.sub(r'\1', content)
                if content != original_content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Cleaned {path}")

if __name__ == '__main__':
    cleanup_markdown('site_src') 