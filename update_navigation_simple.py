#!/usr/bin/env python3
"""
Simple Navigation Updater for MkDocs
Only updates session logs and recaps, preserving all other navigation structure exactly.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any

def extract_session_number(filename: str) -> int:
    """Extract session number from filename like 'log_session_10.md' or 'recap_session_10.md'"""
    match = re.search(r'session_(\d+)\.md$', filename)
    return int(match.group(1)) if match else 0

def scan_session_files(site_src_path: Path) -> Dict[str, Dict[str, List[Tuple[int, str]]]]:
    """
    Scan for session files and return organized structure.
    Returns: {campaign: {'logs': [(session_num, filename)], 'recaps': [(session_num, filename)]}}
    """
    campaigns = {}
    
    for campaign in ['monday', 'wednesday', 'friday']:
        campaign_path = site_src_path / campaign
        if not campaign_path.exists():
            continue
            
        campaigns[campaign] = {'logs': [], 'recaps': []}
        
        # Scan logs
        logs_path = campaign_path / 'logs'
        if logs_path.exists():
            for log_file in logs_path.glob('log_session_*.md'):
                session_num = extract_session_number(log_file.name)
                campaigns[campaign]['logs'].append((session_num, log_file.name))
        
        # Scan recaps
        recaps_path = campaign_path / 'recaps'
        if recaps_path.exists():
            for recap_file in recaps_path.glob('recap_session_*.md'):
                session_num = extract_session_number(recap_file.name)
                campaigns[campaign]['recaps'].append((session_num, recap_file.name))
        
        # Sort by session number (descending for newest first)
        campaigns[campaign]['logs'].sort(key=lambda x: x[0], reverse=True)
        campaigns[campaign]['recaps'].sort(key=lambda x: x[0], reverse=True)
    
    return campaigns

def find_campaign_nav(nav: List[Any], campaign_name: str) -> Any:
    """Find the navigation section for a specific campaign"""
    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                if key.lower() == campaign_name.lower():
                    return value
    return None

def find_session_archives(campaign_nav: List[Any]) -> Any:
    """Find the Session Archives section within a campaign navigation"""
    if not isinstance(campaign_nav, list):
        return None
    
    for item in campaign_nav:
        if isinstance(item, dict):
            for key, value in item.items():
                if 'session' in key.lower() and 'archive' in key.lower():
                    return value
    return None

def find_section_in_archives(session_archives: List[Any], section_name: str) -> Tuple[Any, int]:
    """Find Recaps or Quest Logs section within Session Archives and return it with its index"""
    if not isinstance(session_archives, list):
        return None, -1
    
    for i, item in enumerate(session_archives):
        if isinstance(item, dict):
            for key, value in item.items():
                if section_name.lower() in key.lower():
                    return value, i
    return None, -1

def update_session_section(section: List[Any], session_data: List[Tuple[int, str]], campaign: str, file_type: str):
    """Update a session section (Recaps or Quest Logs) with new entries"""
    if not isinstance(section, list):
        return
    
    # Clear existing entries and rebuild from scratch to ensure correct order
    section.clear()
    
    # Add all sessions in descending order
    for session_num, filename in session_data:
        title = f"Session {session_num}"
        path = f"{campaign}/{file_type}/{filename}"
        section.append({title: path})

def update_mkdocs_navigation(mkdocs_path: Path, session_data: Dict) -> bool:
    """Update the mkdocs.yml navigation with new session files"""
    
    # Read the YAML file as text first to preserve formatting and comments
    with open(mkdocs_path, 'r') as f:
        content = f.read()
    
    # Parse YAML
    config = yaml.safe_load(content)
    
    if 'nav' not in config:
        print("Error: No 'nav' section found in mkdocs.yml")
        return False
    
    # Update each campaign
    for campaign_name, data in session_data.items():
        campaign_nav = find_campaign_nav(config['nav'], campaign_name)
        if not campaign_nav:
            print(f"Warning: {campaign_name} section not found in navigation")
            continue
        
        session_archives = find_session_archives(campaign_nav)
        if not session_archives:
            print(f"Warning: Session Archives not found in {campaign_name}")
            continue
        
        # Update Recaps section
        recaps_section, recaps_index = find_section_in_archives(session_archives, 'recaps')
        if recaps_section is not None:
            update_session_section(recaps_section, data['recaps'], campaign_name, 'recaps')
            print(f"Updated {campaign_name} recaps ({len(data['recaps'])} sessions)")
        
        # Update Quest Logs section  
        logs_section, logs_index = find_section_in_archives(session_archives, 'quest logs')
        if logs_section is not None:
            update_session_section(logs_section, data['logs'], campaign_name, 'logs')
            print(f"Updated {campaign_name} quest logs ({len(data['logs'])} sessions)")
    
    # Write back with preserved formatting
    with open(mkdocs_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, width=1000, indent=2)
    
    return True

def main():
    """Main function to update navigation"""
    project_root = Path(__file__).parent
    site_src_path = project_root / 'site_src'
    mkdocs_path = project_root / 'mkdocs.yml'
    
    if not site_src_path.exists():
        print(f"Error: site_src directory not found at {site_src_path}")
        return False
    
    if not mkdocs_path.exists():
        print(f"Error: mkdocs.yml not found at {mkdocs_path}")
        return False
    
    print("Scanning for session files...")
    session_data = scan_session_files(site_src_path)
    
    # Print what we found
    for campaign, data in session_data.items():
        print(f"\n{campaign.title()}:")
        print(f"  Found {len(data['logs'])} log files")
        print(f"  Found {len(data['recaps'])} recap files")
        if data['logs']:
            latest_log = max(data['logs'], key=lambda x: x[0])
            print(f"  Latest log: Session {latest_log[0]}")
        if data['recaps']:
            latest_recap = max(data['recaps'], key=lambda x: x[0])
            print(f"  Latest recap: Session {latest_recap[0]}")
    
    print(f"\nUpdating {mkdocs_path}...")
    success = update_mkdocs_navigation(mkdocs_path, session_data)
    
    if success:
        print("✅ Navigation updated successfully!")
        print("You can now run 'mkdocs build' to rebuild your site.")
    else:
        print("❌ Failed to update navigation")
        return False
    
    return True

if __name__ == "__main__":
    main()