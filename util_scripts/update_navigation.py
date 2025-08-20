import os
import re
import yaml
from collections import defaultdict

def natural_sort_key(s):
    """Sorts strings containing numbers in a natural way (e.g., 'session_10' before 'session_2')."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def get_session_number(filename):
    """Extracts session number for reverse numerical sorting."""
    match = re.search(r'(\d+)', filename)
    return -int(match.group(1)) if match else 0 # Negate for descending sort

def scan_directory(directory):
    """Scans a directory and returns a sorted list of markdown files and subdirectories."""
    items = defaultdict(list)
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if os.path.isdir(full_path):
            if item.lower() not in ['images', 'assets', 'downloads', 'character_dossiers']:
                items['dirs'].append(item)
        elif item.endswith('.md'):
            items['files'].append(item)
    
    # Sort files: logs/recaps descending, others natural sort
    log_files = sorted([f for f in items['files'] if 'log_session' in f or 'recap_session' in f], key=get_session_number)
    other_files = sorted([f for f in items['files'] if f not in log_files], key=natural_sort_key)
    
    items['files'] = other_files + log_files
    items['dirs'].sort(key=natural_sort_key)
    return items

def update_nav_section(nav_section, base_path):
    """Recursively scans directories and updates the nav section list."""
    if not isinstance(nav_section, list):
        return

    # Use a dictionary to track which items from the YAML have been found on disk
    # This helps preserve the original order and structure
    existing_items = {}
    for i, item in enumerate(nav_section):
        if isinstance(item, dict):
            key, value = list(item.items())[0]
            if isinstance(value, str):
                existing_items[value] = {'title': key, 'index': i, 'type': 'file'}
            elif isinstance(value, list):
                existing_items[key.lower()] = {'title': key, 'index': i, 'type': 'dir'}
        elif isinstance(item, str):
            existing_items[item] = {'title': None, 'index': i, 'type': 'file'}

    scanned = scan_directory(base_path)
    
    # Add newly found files
    for file in scanned['files']:
        if file not in existing_items:
            # Simple title from filename
            title = os.path.splitext(file)[0].replace('_', ' ').replace('-', ' ').title()
            nav_section.append({title: os.path.join(os.path.basename(base_path), file)})
            print(f"  + Added file: {file} to {base_path}")

    # Recurse into subdirectories
    for subdir_name in scanned['dirs']:
        found = False
        for item in nav_section:
            if isinstance(item, dict):
                key, value = list(item.items())[0]
                if key.lower() == subdir_name.lower() and isinstance(value, list):
                    update_nav_section(value, os.path.join(base_path, subdir_name))
                    found = True
                    break
        if not found:
            # Add new directory section if not found
            new_section = []
            title = subdir_name.replace('_', ' ').title()
            nav_section.append({title: new_section})
            update_nav_section(new_section, os.path.join(base_path, subdir_name))
            print(f"  + Added directory: {subdir_name} to {base_path}")

def update_mkdocs_yml(filepath='mkdocs.yml'):
    """Loads, updates, and saves the mkdocs.yml file."""
    print("Starting mkdocs.yml update...")
    try:
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {filepath}: {e}")
        return

    if 'nav' not in config:
        print("No 'nav' section found in mkdocs.yml. Nothing to update.")
        return

    nav_structure = config['nav']
    
    for item in nav_structure:
        if isinstance(item, dict):
            key, value = list(item.items())[0]
            if isinstance(value, list): # It's a campaign directory (e.g., "Monday")
                campaign_path = os.path.join('site_src', key.lower())
                if os.path.isdir(campaign_path):
                    print(f"Scanning campaign: {key}")
                    update_nav_section(value, campaign_path)

    try:
        with open(filepath, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
        print("Successfully updated mkdocs.yml")
    except Exception as e:
        print(f"Error writing to {filepath}: {e}")

if __name__ == '__main__':
    update_mkdocs_yml()
