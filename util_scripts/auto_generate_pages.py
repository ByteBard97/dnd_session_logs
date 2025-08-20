import os
import re
from collections import defaultdict

def extract_title_from_md(filepath):
    """Reads the first line of a markdown file and extracts the main heading."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('# '):
                return first_line[2:].strip()
    except Exception:
        pass
    # Fallback to filename if no title is found
    return os.path.splitext(os.path.basename(filepath))[0].replace('_', ' ').title()

def get_session_number(filename):
    """Extracts session number from filenames like 'log_session_10.md'."""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else -1

def create_pages_file(directory, files, subdirs):
    """Creates a .pages file in a given directory."""
    pages_content = ""
    
    # Prioritize index or overview files
    index_file = None
    if 'index.md' in files:
        index_file = 'index.md'
    elif 'overview.md' in files:
        index_file = 'overview.md'

    if index_file:
        title = extract_title_from_md(os.path.join(directory, index_file))
        pages_content += f"title: {title}\n"
        pages_content += "nav:\n"
        pages_content += f"  - Overview: {index_file}\n"
        files.remove(index_file)
    else:
        pages_content += "nav:\n"

    # Group files by type (log, recap, other) to sort them separately
    logs = sorted([f for f in files if 'log_session' in f], key=get_session_number, reverse=True)
    recaps = sorted([f for f in files if 'recap_session' in f], key=get_session_number, reverse=True)
    other_files = sorted([f for f in files if f not in logs and f not in recaps])

    # Add sorted files to content
    for f in other_files:
        title = extract_title_from_md(os.path.join(directory, f))
        pages_content += f'  - "{title}": {f}\n'
        
    for f in recaps:
        title = extract_title_from_md(os.path.join(directory, f))
        pages_content += f'  - "{title}": {f}\n'

    for f in logs:
        title = extract_title_from_md(os.path.join(directory, f))
        pages_content += f'  - "{title}": {f}\n'

    # Add subdirectories
    for subdir in sorted(subdirs):
        # Use the directory name as the title, formatted nicely
        dir_title = subdir.replace('_', ' ').title()
        pages_content += f'  - {dir_title}:\n'
        # Indent to nest the directory's own .pages file logic under this entry
        pages_content += f'    - ...\n'


    pages_filepath = os.path.join(directory, '.pages')
    with open(pages_filepath, 'w', encoding='utf-8') as f:
        f.write(pages_content)
    print(f"Generated {pages_filepath}")

def main():
    """Main function to walk through the directory and generate .pages files."""
    root_dir = 'site_src'
    campaign_dirs = ['monday', 'wednesday', 'friday']

    for campaign in campaign_dirs:
        campaign_path = os.path.join(root_dir, campaign)
        for dirpath, dirnames, filenames in os.walk(campaign_path):
            # Exclude specified directories
            dirnames[:] = [d for d in dirnames if d not in ['images', 'assets']]
            
            md_files = [f for f in filenames if f.endswith('.md')]
            if not md_files:
                continue

            create_pages_file(dirpath, md_files, dirnames)

if __name__ == '__main__':
    main()

