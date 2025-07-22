#!/usr/bin/env python3
"""
JSON to Markdown NPC Converter
Converts D&D 5e NPC JSON files to themed markdown stat block pages
"""

import json
import os
import sys
from pathlib import Path
import re

def calculate_modifier(ability_score):
    """Calculate ability modifier from score"""
    return (ability_score - 10) // 2

def format_modifier(modifier):
    """Format modifier with proper sign"""
    return f"+{modifier}" if modifier >= 0 else str(modifier)

def format_ability_row(abilities):
    """Format abilities as markdown table row"""
    def format_ability(name, score):
        mod = calculate_modifier(score)
        return f"{score} ({format_modifier(mod)})"
    
    return f"| {format_ability('STR', abilities['str'])} | {format_ability('DEX', abilities['dex'])} | {format_ability('CON', abilities['con'])} | {format_ability('INT', abilities['int'])} | {format_ability('WIS', abilities['wis'])} | {format_ability('CHA', abilities['cha'])} |"

def format_attack(attack_data):
    """Format attack information"""
    attack_str = f"{attack_data.get('type', 'Attack')}: {attack_data.get('tohit', '+0')} to hit"
    
    if 'reach' in attack_data:
        attack_str += f", reach {attack_data['reach']}"
    if 'range' in attack_data:
        attack_str += f", range {attack_data['range']}"
    
    attack_str += f", {attack_data.get('target', 'one target')}."
    
    # Damage
    if 'dmg1' in attack_data:
        attack_str += f" *Hit:* {attack_data['dmg1']} {attack_data.get('type1', 'damage')}"
        if 'dmg2' in attack_data:
            attack_str += f" plus {attack_data['dmg2']} {attack_data.get('type2', 'damage')}"
        attack_str += "."
    
    return attack_str

def format_spellcasting(npc_data):
    """Format spellcasting information"""
    if 'spellcasting_ability' not in npc_data:
        return ""
    
    spellcasting = []
    ability = npc_data['spellcasting_ability']
    level = npc_data.get('caster_level', 1)
    
    # Find spell save DC from traits
    spell_save_dc = "Unknown"
    spell_attack = "Unknown"
    
    for trait in npc_data.get('traits', []):
        if 'Spellcasting' in trait.get('name', ''):
            desc = trait.get('desc', '')
            dc_match = re.search(r'spell save DC (\d+)', desc)
            attack_match = re.search(r'\+(\d+) to hit with spell attacks', desc)
            if dc_match:
                spell_save_dc = dc_match.group(1)
            if attack_match:
                spell_attack = f"+{attack_match.group(1)}"
    
    spellcasting.append(f"**Spellcasting:** {ability}-based, {level}th level caster")
    spellcasting.append(f"**Spell Save DC:** {spell_save_dc}, **Spell Attack Bonus:** {spell_attack}")
    
    if 'spells' in npc_data:
        spells = npc_data['spells']
        if 'cantrips' in spells:
            spellcasting.append(f"**Cantrips (at will):** {', '.join(spells['cantrips'])}")
        
        for level in range(1, 10):
            level_key = f"level{level}"
            if level_key in spells:
                slots = npc_data.get('spell_slots', {}).get(str(level), 'Unknown')
                spells_list = ', '.join(spells[level_key])
                spellcasting.append(f"**{level}{'st' if level == 1 else 'nd' if level == 2 else 'rd' if level == 3 else 'th'} level ({slots} slots):** {spells_list}")
    
    return '\n'.join(spellcasting)

def convert_json_to_markdown(json_file_path, output_dir, images_dir=None):
    """Convert a single JSON file to markdown"""
    
    with open(json_file_path, 'r') as f:
        npc_data = json.load(f)
    
    # Generate filename from NPC name
    name = npc_data['name']
    filename = re.sub(r'[^\w\s-]', '', name.lower())
    filename = re.sub(r'[-\s]+', '_', filename)
    filename = f"{filename}.md"
    
    # Start building markdown content
    markdown = []
    markdown.append(f"# {name}")
    markdown.append("")
    markdown.append('<link rel="stylesheet" href="../drow_theme.css">')
    markdown.append("")
    
    # Basic info table
    markdown.append("> | **Size** | **Type** | **Alignment** | **Challenge Rating** |")
    markdown.append("> |----------|----------|---------------|----------------------|")
    
    size = npc_data.get('size', 'Medium')
    creature_type = npc_data.get('type', 'humanoid')
    alignment = npc_data.get('alignment', 'neutral')
    cr = npc_data.get('cr', '1')
    
    markdown.append(f"> | {size} | {creature_type} | {alignment} | {cr} |")
    markdown.append("")
    
    # Core stats
    markdown.append("## Core Statistics")
    markdown.append("")
    markdown.append("> | **Armor Class** | **Hit Points** | **Speed** | **Proficiency Bonus** |")
    markdown.append("> |-----------------|----------------|-----------|------------------------|")
    
    ac = npc_data.get('ac', {})
    ac_value = ac.get('value', 10)
    ac_notes = ac.get('notes', '')
    ac_display = f"{ac_value}" + (f" ({ac_notes})" if ac_notes else "")
    
    hp = npc_data.get('hp', {})
    hp_avg = hp.get('average', 1)
    hp_formula = hp.get('formula', '1d1')
    hp_display = f"{hp_avg} ({hp_formula})"
    
    speed = npc_data.get('speed', '30 ft.')
    pb = npc_data.get('pb', '+2')
    
    markdown.append(f"> | {ac_display} | {hp_display} | {speed} | {pb} |")
    markdown.append("")
    
    # Ability scores
    markdown.append("## Ability Scores")
    markdown.append("")
    markdown.append("> | **STR** | **DEX** | **CON** | **INT** | **WIS** | **CHA** |")
    markdown.append("> |---------|---------|---------|---------|---------|---------|")
    markdown.append(f"> {format_ability_row(npc_data['abilities'])}")
    markdown.append("")
    
    # Saves, Skills, Senses, Languages
    markdown.append("## Additional Statistics")
    markdown.append("")
    
    if 'saves' in npc_data and npc_data['saves']:
        saves_list = [f"{save.upper()} {bonus}" for save, bonus in npc_data['saves'].items()]
        markdown.append(f"**Saving Throws:** {', '.join(saves_list)}")
        markdown.append("")
    
    if 'skills' in npc_data and npc_data['skills']:
        skills_list = [f"{skill.title()} {bonus}" for skill, bonus in npc_data['skills'].items()]
        markdown.append(f"**Skills:** {', '.join(skills_list)}")
        markdown.append("")
    
    if 'senses' in npc_data:
        markdown.append(f"**Senses:** {npc_data['senses']}")
        markdown.append("")
    
    if 'languages' in npc_data:
        markdown.append(f"**Languages:** {npc_data['languages']}")
        markdown.append("")
    
    # Equipment
    if 'equipment' in npc_data and npc_data['equipment']:
        markdown.append("## Equipment")
        markdown.append("")
        for item in npc_data['equipment']:
            markdown.append(f"### {item['name']}")
            markdown.append(item['desc'])
            markdown.append("")
    
    # Traits
    if 'traits' in npc_data and npc_data['traits']:
        markdown.append("## Traits")
        markdown.append("")
        for trait in npc_data['traits']:
            markdown.append(f"### {trait['name']}")
            markdown.append(trait['desc'])
            markdown.append("")
    
    # Spellcasting (if applicable)
    spellcasting_info = format_spellcasting(npc_data)
    if spellcasting_info:
        markdown.append("## Spellcasting")
        markdown.append("")
        markdown.append(spellcasting_info)
        markdown.append("")
    
    # Actions
    if 'actions' in npc_data and npc_data['actions']:
        markdown.append("## Actions")
        markdown.append("")
        for action in npc_data['actions']:
            markdown.append(f"### {action['name']}")
            if 'attack' in action:
                markdown.append(format_attack(action['attack']))
                if action.get('desc'):
                    markdown.append("")
                    markdown.append(action['desc'])
            else:
                markdown.append(action.get('desc', ''))
            markdown.append("")
    
    # Bonus Actions
    if 'bonus_actions' in npc_data and npc_data['bonus_actions']:
        markdown.append("## Bonus Actions")
        markdown.append("")
        for action in npc_data['bonus_actions']:
            markdown.append(f"### {action['name']}")
            markdown.append(action.get('desc', ''))
            markdown.append("")
    
    # Reactions
    if 'reactions' in npc_data and npc_data['reactions']:
        markdown.append("## Reactions")
        markdown.append("")
        for reaction in npc_data['reactions']:
            markdown.append(f"### {reaction['name']}")
            markdown.append(reaction.get('desc', ''))
            markdown.append("")
    
    # Biography
    if 'bio' in npc_data:
        markdown.append("## Biography")
        markdown.append("")
        markdown.append(npc_data['bio'])
        markdown.append("")
    
    # Look for matching image
    if images_dir:
        image_patterns = [
            f"{filename[:-3]}.webp",
            f"{filename[:-3]}.jpg",
            f"{filename[:-3]}.png",
            f"{name.lower().replace(' ', '_')}.webp",
            f"{name.lower().replace(' ', '_')}.jpg",
            f"{name.lower().replace(' ', '_')}.png"
        ]
        
        for pattern in image_patterns:
            image_path = os.path.join(images_dir, pattern)
            if os.path.exists(image_path):
                # Copy image to output directory
                image_filename = os.path.basename(image_path)
                output_image_path = os.path.join(output_dir, image_filename)
                
                # Copy the image (we'll use bash command for this)
                os.system(f'cp "{image_path}" "{output_image_path}"')
                
                # Add image to markdown
                markdown.insert(3, f"![{name}]({image_filename})")
                markdown.insert(4, "")
                break
    
    markdown.append("---")
    markdown.append("")
    markdown.append(f'*"{name} stands ready to serve the interests of their house and the will of the Spider Queen."*')
    
    # Write to file
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w') as f:
        f.write('\n'.join(markdown))
    
    print(f"Converted {name} -> {filename}")
    return filename

def main():
    """Main execution function"""
    if len(sys.argv) < 3:
        print("Usage: python json_to_markdown_parser.py <json_directory> <output_directory> [images_directory]")
        sys.exit(1)
    
    json_dir = sys.argv[1]
    output_dir = sys.argv[2]
    images_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all JSON files
    converted_files = []
    for json_file in Path(json_dir).glob('*.json'):
        try:
            filename = convert_json_to_markdown(json_file, output_dir, images_dir)
            converted_files.append(filename)
        except Exception as e:
            print(f"Error converting {json_file}: {e}")
    
    print(f"\nConverted {len(converted_files)} NPCs:")
    for filename in sorted(converted_files):
        print(f"  - {filename}")

if __name__ == "__main__":
    main()