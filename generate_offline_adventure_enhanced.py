#!/usr/bin/env python3
"""
Enhanced D&D 5e HTML Adventure Generator
Integrates Foundry VTT PHB styling with Solbera D&D fonts for authentic book appearance.
Creates self-contained HTML files with embedded fonts and CSS.
"""

import os
import json
import re
import base64
from pathlib import Path

def load_font_as_base64(font_path):
    """Load a font file and convert it to base64."""
    try:
        with open(font_path, 'rb') as f:
            font_data = f.read()
        return base64.b64encode(font_data).decode('utf-8')
    except Exception as e:
        print(f"Warning: Could not load font {font_path}: {e}")
        return None

def get_embedded_fonts():
    """Get embedded font CSS with base64 data."""
    fonts_dir = Path(__file__).parent.parent / 'web_frameworks' / 'solbera-dnd-fonts'
    
    # Define the fonts we need for D&D styling
    font_definitions = []
    
    # Bookinsanity (body text)
    bookinsanity_files = [
        ('Bookinsanity', 'Bookinsanity.otf', 'normal', 'normal'),
        ('Bookinsanity', 'Bookinsanity Bold.otf', 'bold', 'normal'),
        ('Bookinsanity', 'Bookinsanity Italic.otf', 'normal', 'italic'),
        ('Bookinsanity', 'Bookinsanity Bold Italic.otf', 'bold', 'italic'),
    ]
    
    for family, filename, weight, style in bookinsanity_files:
        font_path = fonts_dir / 'Bookinsanity' / filename
        if font_path.exists():
            font_base64 = load_font_as_base64(font_path)
            if font_base64:
                weight_style = ""
                if weight != 'normal':
                    weight_style += f"    font-weight: {weight};\n"
                if style != 'normal':
                    weight_style += f"    font-style: {style};\n"
                
                font_definitions.append(f"""
@font-face {{
    font-family: "Bookinsanity";
    src: url(data:font/opentype;base64,{font_base64}) format("opentype");
{weight_style}}}""")

    # Mr Eaves Small Caps (headings)
    mr_eaves_path = fonts_dir / 'Mr Eaves' / 'Mr Eaves Small Caps.otf'
    if mr_eaves_path.exists():
        font_base64 = load_font_as_base64(mr_eaves_path)
        if font_base64:
            font_definitions.append(f"""
@font-face {{
    font-family: "Mr Eaves Small Caps";
    src: url(data:font/opentype;base64,{font_base64}) format("opentype");
}}""")

    # Scaly Sans (tables and special text)
    scaly_sans_files = [
        ('Scaly Sans', 'Scaly Sans.otf', 'normal', 'normal'),
        ('Scaly Sans', 'Scaly Sans Bold.otf', 'bold', 'normal'),
        ('Scaly Sans', 'Scaly Sans Italic.otf', 'normal', 'italic'),
        ('Scaly Sans', 'Scaly Sans Bold Italic.otf', 'bold', 'italic'),
    ]
    
    for family, filename, weight, style in scaly_sans_files:
        font_path = fonts_dir / 'Scaly Sans' / filename
        if font_path.exists():
            font_base64 = load_font_as_base64(font_path)
            if font_base64:
                weight_style = ""
                if weight != 'normal':
                    weight_style += f"    font-weight: {weight};\n"
                if style != 'normal':
                    weight_style += f"    font-style: {style};\n"
                
                font_definitions.append(f"""
@font-face {{
    font-family: "Scaly Sans";
    src: url(data:font/opentype;base64,{font_base64}) format("opentype");
{weight_style}}}""")

    # Scaly Sans Caps (small caps text)
    scaly_caps_path = fonts_dir / 'Scaly Sans Caps' / 'Scaly Sans Caps.otf'
    if scaly_caps_path.exists():
        font_base64 = load_font_as_base64(scaly_caps_path)
        if font_base64:
            font_definitions.append(f"""
@font-face {{
    font-family: "Scaly Sans Caps";
    src: url(data:font/opentype;base64,{font_base64}) format("opentype");
}}""")

    # Solbera Imitation (decorative drop caps)
    solbera_path = fonts_dir / 'Solbera Imitation' / 'Solbera Imitation.otf'
    if solbera_path.exists():
        font_base64 = load_font_as_base64(solbera_path)
        if font_base64:
            font_definitions.append(f"""
@font-face {{
    font-family: "Solbera Imitation";
    src: url(data:font/opentype;base64,{font_base64}) format("opentype");
}}""")

    return '\n'.join(font_definitions)

def get_dnd_phb_css():
    """Get the enhanced D&D PHB styling based on Foundry VTT CSS."""
    return '''
/* D&D 5e Player's Handbook Styling - Adapted from Foundry VTT */

/* Font Embedding */
''' + get_embedded_fonts() + '''

/* Base Document Styling - Foundry VTT Adapted */
body {
    margin: 0;
    padding: 0;
    background: #2c2c2c; /* Dark browser background */
}

.phb-container {
    color: #000;
    padding: 1cm 1.7cm;
    padding-bottom: 1.5cm;
    background-color: #EEE5CE;	
    background-image: linear-gradient(135deg, #EEE5CE 0%, #F5F1E8 100%);
    
    font-family: "Bookinsanity", "Book Antiqua", serif !important;
    font-size: 0.317cm !important;
    text-rendering: optimizeLegibility !important;
    
    max-width: 21cm;
    margin: 2em auto;
    min-height: 29.7cm; /* A4 height */
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
    line-height: 1.3em;
}

/* Headers - Foundry VTT Style */
.phb-container h1, 
.phb-container h2, 
.phb-container h3, 
.phb-container h4 {
    margin-top: 0.2em !important; 
    margin-bottom: 0.2em !important;
    font-family: "Mr Eaves Small Caps", "Cinzel", serif !important;
    color: rgb(93, 24, 13) !important;
    font-weight: normal;
}

.phb-container h1 {
    font-size: 0.987cm;
    -webkit-column-span: all;
    -moz-column-span: all;
    border-bottom: none;
    -webkit-text-stroke-width: 1.2px;
    text-align: center;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
    line-height: 1.2em;
    word-wrap: break-word;
    hyphens: auto;
}

.phb-container h2 {
    font-size: 0.705cm;
    -webkit-column-span: all;
    -moz-column-span: all;
    border-bottom: none;
    -webkit-text-stroke-width: 1px;
    line-height: 1.3em;
    word-wrap: break-word;
}

.phb-container h3 {
    font-size: 0.529cm;
    -webkit-column-span: all;
    -moz-column-span: all;
    border-bottom: 2px solid #c9ad6a;
    -webkit-text-stroke-width: 0.6px;
    padding-bottom: 0.1em;
    line-height: 1.3em;
    word-wrap: break-word;
}

.phb-container h4 {
    margin-bottom: 0 !important;
    font-size: 0.458cm;
    -webkit-column-span: all;
    -moz-column-span: all;
    -webkit-text-stroke-width: 0.6px;
}

.phb-container h5 {
    margin-top: 0;
    margin-bottom: 0.2em;
    font-family: "Scaly Sans Caps", "Cinzel", serif;
    font-size: 0.423cm;
    font-weight: 900;
    color: rgb(93, 24, 13);
}

/* Body Text - Foundry VTT Style */
.phb-container p {
    margin: 0 0 10.5px;
    line-height: 1.3em;
    -webkit-text-stroke-width: 0px;
}

.phb-container p + p {
    margin-top: -0.8em;
}

/* First Letter Drop Cap - Foundry Style - Only for first content paragraph */
.phb-container .section:first-of-type p:first-of-type::first-letter {
    float: left;
    font-family: "Solbera Imitation", "Cinzel Decorative", serif;
    font-size: 5em;
    color: #222;
    line-height: 0.8em;
    margin-right: 0.1em;
    margin-top: 0.1em;
}

/* Paragraph Indentation - Foundry Style */
.phb-container p + p, 
.phb-container ul + p,
.phb-container ol + p {
    text-indent: 1em;
}

/* Read-Aloud Text Boxes */
.phb-container .read-aloud, 
.phb-container .descriptive-text {
    background: #faf9f4;
    border: 2px solid #c9ad6a;
    border-radius: 0;
    padding: 0.8em 1em;
    margin: 1em 0;
    font-style: italic;
    position: relative;
    text-indent: 0 !important; /* No indentation in boxes */
}

.phb-container .read-aloud::before {
    content: "";
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border: 1px solid #8b7355;
    border-radius: 0;
    pointer-events: none;
}

/* Tables - Foundry Style */
.phb-container table {
    font-family: "Scaly Sans", "Noto Sans", sans-serif;
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

.phb-container table th {
    background: #c9ad6a;
    color: #000;
    font-weight: bold;
    padding: 0.5em;
    border: 1px solid #8b7355;
    text-align: left;
}

/* Dialogue Entries - Enhanced Spacing */
.phb-container .dialogue-entry {
    margin: 1em 0;
    padding: 0.5em 0;
    line-height: 1.5em;
    border-left: 3px solid #c9ad6a;
    padding-left: 1em;
    margin-left: 0.5em;
}

.phb-container table td {
    padding: 0.5em;
    border: 1px solid #8b7355;
    vertical-align: top;
}

.phb-container table tr:nth-child(even) {
    background: #f5f3ed;
}

/* Lists */
.phb-container ul, 
.phb-container ol {
    margin: 0.5em 0;
    padding-left: 2em;
}

.phb-container li {
    margin: 0.2em 0;
}

/* Strong and Emphasis */
.phb-container strong, 
.phb-container b {
    font-weight: bold;
    color: rgb(93, 24, 13);
}

.phb-container em, 
.phb-container i {
    font-style: italic;
}

/* Images */
.phb-container img {
    max-width: 100%;
    height: auto;
    border: 3px solid #c9ad6a;
    border-radius: 3px;
    margin: 1em 0;
    display: block;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .phb-container {
        margin: 1em;
        padding: 1em;
        font-size: 0.35cm !important;
    }
}

/* Print Styles */
@media print {
    body {
        background: white;
    }
    
    .phb-container {
        margin: 0;
        box-shadow: none;
        max-width: none;
    }
}
'''

def load_json_monster(json_file_path):
    """Load a JSON monster file and return the data."""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {json_file_path}: {e}")
        return None

def convert_json_to_statblock5e(json_data):
    """Convert JSON monster data to StatBlock5e HTML format."""
    if not json_data:
        return ""
    
    try:
        # Basic info
        name = json_data.get('name', 'Unknown')
        print(f"Converting {name}...")  # Debug info
        size = json_data.get('size', 'Medium')
        type_str = json_data.get('type', 'humanoid')
        alignment = json_data.get('alignment', 'neutral')
        
        # Armor Class
        ac = json_data.get('ac', {})
        if isinstance(ac, dict):
            ac_value = ac.get('value', ac.get('ac', 10))
            ac_notes = ac.get('notes', '')
            ac_display = f"{ac_value}"
            if ac_notes:
                ac_display += f" ({ac_notes})"
        elif isinstance(ac, str):
            ac_display = ac
        else:
            ac_display = str(ac)
        
        # Hit Points
        hp = json_data.get('hp', {})
        if isinstance(hp, dict):
            hp_average = hp.get('average', 1)
            hp_formula = hp.get('formula', '1d4')
            hp_display = f"{hp_average} ({hp_formula})"
        elif isinstance(hp, str):
            hp_display = hp
        else:
            hp_display = str(hp)
        
        # Speed
        speed = json_data.get('speed', {})
        if isinstance(speed, dict):
            speed_parts = []
            for speed_type, value in speed.items():
                if speed_type == 'walk':
                    speed_parts.insert(0, f"{value} ft.")
                else:
                    speed_parts.append(f"{speed_type} {value} ft.")
            speed_display = ", ".join(speed_parts)
        else:
            speed_display = f"{speed} ft." if speed else "30 ft."
        
        # Ability Scores - handle both direct properties and abilities object
        abilities = json_data.get('abilities', {})
        
        # Helper function to safely get ability scores
        def get_ability_score(ability_name):
            # First try from abilities object
            if abilities and ability_name in abilities:
                score = abilities[ability_name]
            else:
                # Fall back to direct property
                score = json_data.get(ability_name, 10)
            
            # Convert to integer if it's a string
            try:
                return int(score)
            except (ValueError, TypeError):
                print(f"Warning: Invalid {ability_name} score '{score}' for {json_data.get('name', 'Unknown')}")
                return 10
        
        str_score = get_ability_score('str')
        dex_score = get_ability_score('dex')
        con_score = get_ability_score('con')
        int_score = get_ability_score('int')
        wis_score = get_ability_score('wis')
        cha_score = get_ability_score('cha')
        
        def ability_modifier(score):
            return (score - 10) // 2
        
        def format_modifier(mod):
            return f"+{mod}" if mod >= 0 else str(mod)
        
        # Build the stat block HTML
        html = f'''
<stat-block>
    <h1>{name}</h1>
    <h2>{size} {type_str}, {alignment}</h2>
    <div class="bar"></div>
    
    <p><strong>Armor Class</strong> {ac_display}</p>
    <p><strong>Hit Points</strong> {hp_display}</p>
    <p><strong>Speed</strong> {speed_display}</p>
    
    <div class="bar"></div>
    
    <table>
        <tr>
            <th>STR</th>
            <th>DEX</th>
            <th>CON</th>
            <th>INT</th>
            <th>WIS</th>
            <th>CHA</th>
        </tr>
        <tr>
            <td>{str_score} ({format_modifier(ability_modifier(str_score))})</td>
            <td>{dex_score} ({format_modifier(ability_modifier(dex_score))})</td>
            <td>{con_score} ({format_modifier(ability_modifier(con_score))})</td>
            <td>{int_score} ({format_modifier(ability_modifier(int_score))})</td>
            <td>{wis_score} ({format_modifier(ability_modifier(wis_score))})</td>
            <td>{cha_score} ({format_modifier(ability_modifier(cha_score))})</td>
        </tr>
    </table>
    
    <div class="bar"></div>
'''
        
        # Optional attributes
        skills = json_data.get('skills', {})
        if skills:
            skill_list = []
            for skill, bonus in skills.items():
                skill_name = skill.replace('_', ' ').title()
                # Handle string bonuses like "+5" and integer bonuses
                try:
                    if isinstance(bonus, str):
                        # If it's already formatted with +/-, use as is
                        if bonus.startswith(('+', '-')):
                            skill_list.append(f"{skill_name} {bonus}")
                        else:
                            # Try to convert to int and format
                            skill_list.append(f"{skill_name} {format_modifier(int(bonus))}")
                    else:
                        skill_list.append(f"{skill_name} {format_modifier(int(bonus))}")
                except (ValueError, TypeError):
                    # Fallback to string representation
                    skill_list.append(f"{skill_name} {bonus}")
            html += f'    <p><strong>Skills</strong> {", ".join(skill_list)}</p>\n'
        
        if 'damage_resistances' in json_data:
            html += f'    <p><strong>Damage Resistances</strong> {json_data["damage_resistances"]}</p>\n'
        
        if 'damage_immunities' in json_data:
            html += f'    <p><strong>Damage Immunities</strong> {json_data["damage_immunities"]}</p>\n'
        
        if 'condition_immunities' in json_data:
            html += f'    <p><strong>Condition Immunities</strong> {json_data["condition_immunities"]}</p>\n'
        
        senses = json_data.get('senses', [])
        if senses:
            if isinstance(senses, list):
                senses_str = ", ".join(senses)
            else:
                senses_str = str(senses)
            html += f'    <p><strong>Senses</strong> {senses_str}</p>\n'
        
        languages = json_data.get('languages', [])
        if languages:
            if isinstance(languages, list):
                lang_str = ", ".join(languages)
            else:
                lang_str = str(languages)
            html += f'    <p><strong>Languages</strong> {lang_str}</p>\n'
        
        cr = json_data.get('cr', '1/4')
        html += f'    <p><strong>Challenge</strong> {cr}</p>\n'
        
        html += '    <div class="bar"></div>\n'
        
        # Traits - handle both 'trait' and 'traits' arrays, and 'desc' vs 'entries'
        traits = json_data.get('trait', json_data.get('traits', []))
        if traits:
            for trait in traits:
                trait_name = trait.get('name', 'Special Ability')
                trait_text = trait.get('desc', trait.get('entries', ''))
                if isinstance(trait_text, list):
                    trait_text = ' '.join(trait_text)
                else:
                    trait_text = str(trait_text)
                html += f'    <h4>{trait_name}.</h4><p>{trait_text}</p>\n'
            html += '    <div class="bar"></div>\n'
        
        # Actions - handle both 'action' and 'actions' arrays, and 'desc' vs 'entries'
        actions = json_data.get('action', json_data.get('actions', []))
        if actions:
            html += '    <h3>Actions</h3>\n'
            for action in actions:
                action_name = action.get('name', 'Action')
                action_text = action.get('desc', action.get('entries', ''))
                if isinstance(action_text, list):
                    action_text = ' '.join(action_text)
                else:
                    action_text = str(action_text)
                html += f'    <h4>{action_name}.</h4><p>{action_text}</p>\n'
        
        # Bonus Actions
        bonus_actions = json_data.get('bonus_actions', [])
        if bonus_actions:
            html += '    <div class="bar"></div>\n'
            html += '    <h3>Bonus Actions</h3>\n'
            for action in bonus_actions:
                if isinstance(action, dict):
                    action_name = action.get('name', 'Bonus Action')
                    action_text = action.get('desc', action.get('entries', ''))
                    if isinstance(action_text, list):
                        action_text = ' '.join(action_text)
                    else:
                        action_text = str(action_text)
                    html += f'    <h4>{action_name}.</h4><p>{action_text}</p>\n'
        
        # Reactions
        reactions = json_data.get('reactions', [])
        if reactions:
            html += '    <div class="bar"></div>\n'
            html += '    <h3>Reactions</h3>\n'
            for reaction in reactions:
                if isinstance(reaction, dict):
                    reaction_name = reaction.get('name', 'Reaction')
                    reaction_text = reaction.get('desc', reaction.get('entries', ''))
                    if isinstance(reaction_text, list):
                        reaction_text = ' '.join(reaction_text)
                    else:
                        reaction_text = str(reaction_text)
                    html += f'    <h4>{reaction_name}.</h4><p>{reaction_text}</p>\n'
        
        # Legendary Actions - handle both object format and array format
        legendary_data = json_data.get('legendary', json_data.get('legendary_actions', []))
        legendary_actions = []
        
        # Handle different legendary action formats
        if isinstance(legendary_data, dict):
            # Object format with 'actions' array
            legendary_actions = legendary_data.get('actions', [])
            legendary_count = legendary_data.get('count', 3)
        elif isinstance(legendary_data, list):
            # Direct array format
            legendary_actions = legendary_data
            legendary_count = 3
        
        if legendary_actions:
            html += '    <div class="bar"></div>\n'
            html += f'    <h3>Legendary Actions ({legendary_count} per turn)</h3>\n'
            for action in legendary_actions:
                if isinstance(action, dict):
                    action_name = action.get('name', 'Legendary Action')
                    action_text = action.get('desc', action.get('entries', ''))
                    cost = action.get('cost', 1)
                    if cost > 1:
                        action_name += f' (Costs {cost} Actions)'
                    if isinstance(action_text, list):
                        action_text = ' '.join(action_text)
                    else:
                        action_text = str(action_text)
                    html += f'    <h4>{action_name}.</h4><p>{action_text}</p>\n'
        
        # Mythic Actions (Villain Actions) - handle complex structure
        mythic_actions = json_data.get('mythic_actions', {})
        if mythic_actions and isinstance(mythic_actions, dict):
            mythic_desc = mythic_actions.get('desc', '')
            mythic_action_list = mythic_actions.get('actions', [])
            if mythic_action_list:
                html += '    <div class="bar"></div>\n'
                html += '    <h3>Villain Actions</h3>\n'
                if mythic_desc:
                    html += f'    <p><em>{mythic_desc}</em></p>\n'
                for action in mythic_action_list:
                    if isinstance(action, dict):
                        action_name = action.get('name', 'Villain Action')
                        action_text = action.get('desc', action.get('entries', ''))
                        if isinstance(action_text, list):
                            action_text = ' '.join(action_text)
                        else:
                            action_text = str(action_text)
                        html += f'    <h4>{action_name}.</h4><p>{action_text}</p>\n'
        
        html += '</stat-block>'
        return html
        
    except Exception as e:
        monster_name = json_data.get('name', 'Unknown') if isinstance(json_data, dict) else 'Unknown'
        print(f"Error converting monster '{monster_name}' to StatBlock5e: {e}")
        print(f"Monster data type: {type(json_data)}")
        if isinstance(json_data, dict):
            print(f"Monster keys: {list(json_data.keys())}")
        return f'<p><strong>Error:</strong> Could not convert monster data for {monster_name}</p>'

def get_statblock5e_base():
    """Get the self-contained StatBlock5e CSS and JavaScript."""
    return '''
<style>
  .bar {
    height: 5px;
    background: #E69A28;
    border: 1px solid #000;
    position: relative;
    z-index: 1;
  }

  stat-block {
    display: block;
    font-family: "Scaly Sans", 'Noto Sans', 'Myriad Pro', Calibri, Helvetica, Arial, sans-serif;
    font-size: 13.5px;
    background: #FDF1DC;
    padding: 0.8em;
    padding-bottom: 0.6em;
    border: 2px solid #c9ad6a;
    box-shadow: 0 0 10px rgba(139, 115, 85, 0.5);
    position: relative;
    z-index: 0;
    margin: 20px auto;
    max-width: 450px;
    width: 100%;
    border-radius: 0;
  }

  stat-block h1 {
    font-family: "Mr Eaves Small Caps", 'Libre Baskerville', 'Lora', 'Calisto MT', 'Bookman Old Style', serif;
    color: rgb(93, 24, 13);
    font-weight: normal;
    margin: 0px;
    font-size: 23px;
    letter-spacing: 1px;
    font-variant: small-caps;
    text-align: center;
  }

  stat-block h2 {
    font-weight: normal;
    font-style: italic;
    font-size: 12px;
    spacing: 0px;
    margin: 0;
  }

  stat-block h3 {
    border-bottom: 1px solid #7A200D;
    color: #7A200D;
    font-size: 21px;
    font-variant: small-caps;
    font-weight: normal;
    letter-spacing: 1px;
    margin: 0;
    margin-bottom: 0.3em;
    break-inside: avoid-column;
    break-after: avoid-column;
  }

  stat-block h4 {
    margin: 0;
    margin-right: 0.3em;
    font-weight: bold;
    font-style: italic;
    display: inline;
  }

  stat-block p {
    margin-top: 0.3em;
    margin-bottom: 0.9em;
    line-height: 1.5;
    display: inline;
  }

  stat-block table {
    width: 100%;
    border: 0px;
    border-collapse: collapse;
  }

  stat-block table thead,
  stat-block table tbody {
    text-align: center;
  }

  stat-block table th,
  stat-block table td {
    width: 50px;
  }
</style>
'''

def normalize_title(title):
    """Normalize a title for comparison - remove special chars, lower case, etc."""
    return re.sub(r'[^a-zA-Z0-9\s]', '', title).lower().strip()

def should_skip_first_h1(markdown_content, section_title):
    """Check if the first H1 in markdown duplicates the section title."""
    # Extract first H1 from markdown
    first_h1_match = re.search(r'^# (.+)$', markdown_content, re.MULTILINE)
    if not first_h1_match:
        return False
    
    first_h1 = first_h1_match.group(1)
    
    # Normalize both titles for comparison
    norm_h1 = normalize_title(first_h1)
    norm_section = normalize_title(section_title)
    
    # Check for substantial overlap (contains key words)
    h1_words = set(norm_h1.split())
    section_words = set(norm_section.split())
    
    # Special case: if section title contains quadrant/area identifiers and H1 mentions same area
    if any(word in norm_section for word in ['quadrant', 'll', 'lr', 'ul', 'ur']) and \
       any(word in norm_h1 for word in ['quadrant', 'left', 'right', 'upper', 'lower']):
        return True
    
    # If 50% or more of the words overlap, consider it a duplicate (lowered threshold)
    if len(h1_words) > 0 and len(section_words) > 0:
        overlap = len(h1_words.intersection(section_words))
        return overlap / min(len(h1_words), len(section_words)) >= 0.5
    
    return False

def md_to_html(markdown_content, safe_mode=False, skip_first_h1=False):
    """Convert Markdown to HTML with D&D-specific enhancements."""
    html = markdown_content
    
    # Skip first H1 if requested (for summary content)
    if skip_first_h1:
        # Remove the first H1 header line
        html = re.sub(r'^# .+$\n?', '', html, count=1, flags=re.MULTILINE)
    
    # Process AI image tags for safe mode
    if safe_mode:
        # Remove images marked with {ai} tag
        html = re.sub(r'!\[([^\]]*)\]\([^)]+\)\{ai\}', r'*[Image: \1 - AI generated, removed for community version]*', html)
    else:
        # Remove {ai} tags but keep images
        html = re.sub(r'(!\[[^\]]*\]\([^)]+\))\{ai\}', r'\1', html)
    
    # Remove standalone URLs and @URLs (development artifacts)
    html = re.sub(r'^@https?://[^\s]+\s*$', '', html, flags=re.MULTILINE)
    html = re.sub(r'^https?://[^\s]+\s*$', '', html, flags=re.MULTILINE)
    
    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Images with enhanced D&D styling
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', 
                  lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" class="adventure-image map-image" />' 
                  if 'map' in m.group(2).lower() or 'map' in m.group(1).lower()
                  else f'<img src="{m.group(2)}" alt="{m.group(1)}" class="adventure-image" />', html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Read-aloud boxes (text in quotes gets special styling)
    html = re.sub(r'^> (.+)$', r'<div class="read-aloud">\1</div>', html, flags=re.MULTILINE)
    
    # Lists - handle bullet points BEFORE bold/italic processing to preserve structure
    # First, identify bullet points and their full content (including following indented lines)
    lines = html.split('\n')
    processed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        if re.match(r'^\*\s+', line):
            # This is a bullet point - collect all related content
            bullet_content = [line[2:].strip()]  # Remove "* " prefix
            i += 1
            
            # Collect indented continuation lines
            while i < len(lines) and (lines[i].startswith('    ') or lines[i].strip() == ''):
                if lines[i].strip():  # Not empty line
                    bullet_content.append(lines[i].strip())
                elif bullet_content and bullet_content[-1]:  # Add spacing for empty lines
                    bullet_content.append('')
                i += 1
            
            # Join the content and wrap in dialogue-entry div
            full_content = ' '.join(content for content in bullet_content if content)
            processed_lines.append(f'<div class="dialogue-entry">{full_content}</div>')
            i -= 1  # Back up one since the while loop will increment
        else:
            processed_lines.append(line)
        i += 1
    
    html = '\n'.join(processed_lines)
    
    # Bold and italic (process AFTER bullet points to preserve dialogue formatting)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Convert double line breaks to paragraph breaks
    html = re.sub(r'\n\n+', '\n\n[PARAGRAPH_BREAK]\n\n', html)
    
    # Process paragraphs more intelligently
    paragraphs = html.split('[PARAGRAPH_BREAK]')
    processed_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        lines = [line.strip() for line in paragraph.split('\n') if line.strip()]
        
        # If it's already HTML (starts with <), keep as is
        if any(line.startswith('<') for line in lines):
            processed_paragraphs.append('\n'.join(lines))
        else:
            # Wrap non-HTML content in paragraph tags
            if len(lines) == 1:
                processed_paragraphs.append(f'<p>{lines[0]}</p>')
            else:
                # Multiple lines - keep them together in one paragraph with <br> tags
                content = '<br />'.join(lines)
                processed_paragraphs.append(f'<p>{content}</p>')
    
    return '\n\n'.join(processed_paragraphs)

def load_adventure_content():
    """Load all adventure content from markdown files."""
    content = {}
    base_dir = Path(__file__).parent.parent / 'adventure'
    
    # Load main summary
    summary_file = base_dir / 'adventure_summary.md'
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            content['summary'] = f.read()
    
    # Load neighborhood content
    neighborhoods = {}
    for item in base_dir.iterdir():
        if item.is_dir():
            # Look for main markdown file in the directory
            main_md = item / f"{item.name}.md"
            if main_md.exists():
                with open(main_md, 'r', encoding='utf-8') as f:
                    neighborhoods[item.name] = f.read()
            else:
                # Look for any markdown files in the directory
                md_files = list(item.glob('*.md'))
                if md_files:
                    combined_content = []
                    for md_file in md_files:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                            # Only add filename header if there are multiple files
                            # or if the content doesn't start with its own header
                            if len(md_files) > 1 and not file_content.strip().startswith('#'):
                                combined_content.append(f"## {md_file.stem}\n\n{file_content}")
                            else:
                                combined_content.append(file_content)
                    neighborhoods[item.name] = '\n\n'.join(combined_content)
    
    content['neighborhoods'] = neighborhoods
    return content

def load_monster_statblocks():
    """Load and convert monster JSON files to StatBlock5e HTML."""
    statblocks = {}
    npcs_dir = Path(__file__).parent.parent / 'npcs'
    
    if not npcs_dir.exists():
        print(f"Warning: NPCs directory not found at {npcs_dir}")
        return statblocks
    
    for json_file in npcs_dir.glob('*.json'):
        # Skip example files
        if 'example' in json_file.name.lower():
            continue
            
        monster_data = load_json_monster(json_file)
        if monster_data:
            name = monster_data.get('name', json_file.stem)
            statblock_html = convert_json_to_statblock5e(monster_data)
            if statblock_html:
                statblocks[name] = statblock_html
    
    return statblocks

def generate_html(safe_mode=False):
    """Generate the complete HTML adventure with D&D styling."""
    print("🎲 Loading adventure content...")
    content = load_adventure_content()
    
    print("👹 Loading monster stat blocks...")
    statblocks = load_monster_statblocks()
    
    print(f"📚 Generating {'safe' if safe_mode else 'complete'} HTML with D&D PHB styling...")
    
    # Start building HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mytros Sewer Dungeon: Complete D&D 5e Adventure</title>
    
    {get_statblock5e_base()}
    
    <style>
        {get_dnd_phb_css()}
    </style>
</head>
<body>
    <div class="phb-container">
        <h1 class="chapter-start">Mytros Sewer Dungeon</h1>
        <p style="text-align: center; font-style: italic; margin-bottom: 2em;">A Complete D&D 5e Adventure</p>
'''
    
    # Add adventure summary
    if 'summary' in content:
        html += f'''
        <div class="section">
            <h2>Adventure Overview</h2>
            {md_to_html(content['summary'], safe_mode, skip_first_h1=True)}
        </div>
'''
    
    # Add neighborhoods
    for neighborhood, md_content in content.get('neighborhoods', {}).items():
        neighborhood_title = neighborhood.replace('_', ' ').title()
        
        # Check if we should skip the first H1 to avoid duplication
        skip_h1 = should_skip_first_h1(md_content, neighborhood_title)
        
        html += f'''
        <div class="section">
            <h2>{neighborhood_title}</h2>
            {md_to_html(md_content, safe_mode, skip_first_h1=skip_h1)}
        </div>
'''
    
    # Add monster stat blocks
    if statblocks:
        html += '''
        <div class="section">
            <h2>Monster Compendium</h2>
            <div class="statblocks-grid">
'''
        
        for name, statblock_html in statblocks.items():
            html += f'                {statblock_html}\n'
        
        html += '''
            </div>
        </div>
'''
    
    html += '''
    </div>
</body>
</html>'''
    
    return html

def main():
    """Main function to generate the HTML adventure."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate D&D 5e styled HTML adventure with PHB appearance')
    parser.add_argument('--safe-mode', action='store_true', 
                       help='Generate safe version without AI images for community sharing')
    parser.add_argument('--both', action='store_true',
                       help='Generate both normal and safe versions')
    
    args = parser.parse_args()
    
    output_dir = Path(__file__).parent
    
    if args.both:
        # Generate both versions
        print("🏗️  Generating both normal and safe versions with D&D PHB styling...")
        
        # Normal version
        print("\n📝 Generating normal version (all images included)...")
        html_normal = generate_html(safe_mode=False)
        normal_file = output_dir / 'dnd_adventure_complete.html'
        with open(normal_file, 'w', encoding='utf-8') as f:
            f.write(html_normal)
        
        normal_size = normal_file.stat().st_size
        print(f"✅ Generated {normal_file}")
        print(f"📊 File size: {normal_size:,} bytes ({normal_size/1024/1024:.1f} MB)")
        
        # Safe version
        print("\n🛡️  Generating safe version (AI images removed)...")
        html_safe = generate_html(safe_mode=True)
        safe_file = output_dir / 'dnd_adventure_safe.html'
        with open(safe_file, 'w', encoding='utf-8') as f:
            f.write(html_safe)
        
        safe_size = safe_file.stat().st_size
        print(f"✅ Generated {safe_file}")
        print(f"📊 File size: {safe_size:,} bytes ({safe_size/1024/1024:.1f} MB)")
        
        print(f"\n🎯 Both versions work completely offline with authentic D&D styling!")
        print(f"🔗 Normal: file://{normal_file.absolute()}")
        print(f"🔗 Safe: file://{safe_file.absolute()}")
        
    else:
        # Generate single version
        safe_mode = args.safe_mode
        version_name = "safe (community-friendly)" if safe_mode else "normal (all images)"
        
        print(f"🏗️  Generating {version_name} version with D&D PHB styling...")
        
        html_content = generate_html(safe_mode=safe_mode)
        
        # Choose output filename
        if safe_mode:
            output_file = output_dir / 'dnd_adventure_safe.html'
        else:
            output_file = output_dir / 'dnd_adventure_complete.html'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_size = output_file.stat().st_size
        print(f"✅ Generated {output_file}")
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        print(f"🔗 Open in browser: file://{output_file.absolute()}")
        
        if safe_mode:
            print("\n🛡️  Safe mode: AI-generated images removed for community sharing")
        else:
            print("\n🎨 Normal mode: All images included")
        
        print("🎯 This file uses authentic D&D 5e Player's Handbook styling!")
        print("📚 Features embedded Solbera D&D fonts and Foundry VTT CSS")

if __name__ == "__main__":
    main() 