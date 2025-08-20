#!/usr/bin/env python3
"""
Auto-update mkdocs.yml navigation with new session files.
This script scans for new log_session_*.md and recap_session_*.md files
and automatically updates the mkdocs.yml navigation structure.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

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

def update_mkdocs_navigation(mkdocs_path: Path, session_data: Dict) -> bool:
    """Update the mkdocs.yml navigation with new session files"""
    
    # Read current mkdocs.yml
    with open(mkdocs_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Find and update each campaign's session archives
    nav = config.get('nav', [])
    
    for nav_item in nav:
        if not isinstance(nav_item, dict):
            continue
            
        for campaign_name, campaign_nav in nav_item.items():
            if campaign_name.lower() in ['monday', 'wednesday', 'friday']:
                campaign_key = campaign_name.lower()
                
                if campaign_key not in session_data:
                    continue
                    
                # Find Session Archives section
                if isinstance(campaign_nav, list):
                    for section in campaign_nav:
                        if isinstance(section, dict) and 'Session Archives' in section:
                            session_archives = section['Session Archives']
                            
                            # Update Recaps
                            for archives_section in session_archives:
                                if isinstance(archives_section, dict) and 'Recaps' in archives_section:
                                    recap_entries = []
                                    for session_num, filename in session_data[campaign_key]['recaps']:
                                        title = f"Session {session_num}"
                                        path = f"{campaign_key}/recaps/{filename}"
                                        recap_entries.append({title: path})
                                    archives_section['Recaps'] = recap_entries
                                
                                elif isinstance(archives_section, dict) and 'Quest Logs' in archives_section:
                                    log_entries = []
                                    for session_num, filename in session_data[campaign_key]['logs']:
                                        title = f"Session {session_num}"
                                        path = f"{campaign_key}/logs/{filename}"
                                        log_entries.append({title: path})
                                    archives_section['Quest Logs'] = log_entries
    
    # Write updated mkdocs.yml
    with open(mkdocs_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, width=1000)
    
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