#!/usr/bin/env python3
"""
Restore biography sections to Cinderfork Foundry NPCs.
"""

from pathlib import Path

# Dictionary of NPC biographies to restore
NPC_BIOGRAPHIES = {
    "acolyte_ghoran.md": """
## Biography

Acolyte Ghoran is the spiritual authority within the Cinderfork Foundry, a terrifying figure whose fanatical devotion to Laduguer is plain to see. He wears a tall, imposing mitre and heavy, dark robes, with thick iron chains draped over his shoulders as a sign of his holy burden. His eyes glow with a malevolent orange light as he oversees the ritualistic creation of Screamers, viewing each tormented shriek as a hymn to his god. He believes that suffering is a holy state and that true power is forged only through pain and agony.
""",
    
    "alyxina_fire_beard.md": """
## Biography

Alyxina Fire-Beard is the wife of Chief Researcher Korvun, and she is the heart of their small household within the grim Cinderfork Foundry. Her official style is 'Quartermaster of Comfort, Keeper of the Hearth-Lab,' a title she embraces with fiery optimism. She is fiercely protective of her husband, whom she affectionately calls 'my clever fool,' and will not abide others mocking him. With a tinkerer's curiosity, she can't resist fiddling with unattended gadgets, gems, or fungi. While she projects warmth, she is a sturdy clan matron who won't hesitate to defend her home with a cast-iron ladle. She is typically found in the Research Cottage (Area 2) on the foundry's sub-level.
""",
    
    "black_mithril_screamer.md": """
## Combat Statistics (Unstable Variant)

<div id="screamer-unstable-statblock"></div>

<script>
// Wait for page load to ensure all scripts are available
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    // Load statblock from JSON file
    loadJsonStatblock('../json/black_mithril_screamer_unstable.json', 'screamer-unstable-statblock');
  }, 100);
});
</script>

## Biography

The Black Mithril Screamer is the terrifying result of House Glutthraz's funding and the duergars' profane craftsmanship. A hulking suit of interlocking black metal plates that glow with faint orange fissures, this construct is built around the tormented soul of a living creature. Its right arm has been replaced with a massive, revolving drill capable of tearing through steel and stone, and its tortured screams can shatter bone. The Black Mithril fused to its chassis makes it incredibly resilient but dangerously unstable.
""",
    
    "chief_engineer_tholdrum_steam_heart_garn.md": """
## Biography

Chief Engineer Tholdrum "Steam-Heart" Garn oversees the industrial production of Screamers at the Cinderfork Foundry. With a partially mechanical heart, he views sentient constructs as an engineering challenge to be perfected. His right eye has been replaced with a mechanical monocle that constantly adjusts focus, and steam occasionally hisses from vents in his armor. He carries a heavy wrench that doubles as a mace and speaks in efficient, clipped sentences.
""",
    
    "chief_researcher_korvun.md": """
## Biography

Chief Researcher Korvun is the brilliant mind behind the screamer torment matrices at Cinderfork Foundry. A meticulous duergar with wild, singed eyebrows and a perpetually distracted expression, he treats the creation of these abominations as pure science. He keeps detailed notes on pain thresholds and soul-binding techniques, viewing each screaming construct as a data point in his grand experiment. Despite his clinical approach to horror, he maintains a surprisingly warm relationship with his wife, Alyxina.
""",
    
    "director_koldar.md": """
## Biography

Director Koldar runs the Cinderfork Foundry with ruthless efficiency, treating both workers and screamers as resources to be optimized. A stern duergar with iron-gray beard braided with small gears, he wears a coat covered in pockets filled with ledgers and production schedules. He speaks in terms of quotas and deadlines, showing emotion only when production targets are missed or exceeded.
""",
    
    "duergar_forgeworker.md": """
## Biography

The Duergar Forgeworkers are the backbone of Cinderfork Foundry's production. These grim, soot-covered dwarves work in shifts around the clock, their faces hidden behind thick goggles and breathing masks. They rarely speak, communicating mostly through hand signals in the noisy foundry environment. Each bears burns and scars from years of dangerous work with molten metal and unstable magical energies.
""",
    
    "duergar_sentry.md": """
## Biography

Duergar Sentries guard the critical areas of Cinderfork Foundry with unwavering discipline. They wear standardized armor marked with the foundry's seal and carry crossbows loaded with specially crafted bolts. These guards are chosen for their loyalty and lack of curiosity about the screams that echo through the facility. They rotate posts regularly to prevent complacency.
""",
    
    "foundry_master_borok.md": """
## Biography

Foundry Master Borok oversees the day-to-day operations of the screamer production line. A veteran duergar with arms like tree trunks and a voice that cuts through the foundry's din, he ensures quotas are met through a combination of harsh discipline and grudging respect for skilled work. His face is a map of old burns, and he's missing two fingers on his left hand from an early accident he refuses to discuss.
""",
    
    "geothermal_elemental.md": """
## Biography

The Bound Geothermal Elemental is a creature of living magma and stone, enslaved by the duergar artificers to power the foundry's forges. Chains of enchanted adamantine bind it to the facility's core, where its immense heat is channeled into the screamer production process. It constantly struggles against its bonds, causing occasional tremors throughout the complex. The elemental understands its captivity and burns with hatred for its captors.
""",
    
    "liaison_malexa.md": """
## Biography

Liaison Malexa serves as the primary contact between House Glutthraz and the Cinderfork Foundry. This elegant drow maintains an office within the facility, though she clearly finds the industrial environment distasteful. She dresses in fine spider silk robes that seem perpetually clean despite the foundry's grime, and speaks with the cultured tones of high drow society. Her role is to ensure the foundry's output meets House Glutthraz's specifications and payment flows smoothly.
""",
    
    "master_smith_durkal.md": """
## Biography

Master Smith Durkal is the foundry's most skilled metalworker, responsible for forging the black mithril plating that gives screamers their resilience. A perfectionist who takes pride in his craft despite its horrific purpose, he inspects every piece personally. His workshop is meticulously organized, with tools arranged by size and purpose. He speaks little but his work speaks volumes about his skill.
""",
    
    "scrutinizer.md": """
## Biography

The Scrutinizer is a specialized construct designed to monitor and evaluate screamer production quality. This spider-like automaton skitters through the foundry on eight articulated legs, its cluster of crystal eyes recording every detail. It communicates through a series of clicks and whirs that the foundry workers have learned to interpret. Unlike the screamers, the Scrutinizer shows no signs of consciousness, operating purely on programmed directives.
""",
    
    "skitter.md": """
# Keep Skitter's existing content since it already has biography
"""
}

def restore_biography(file_path, biography_content):
    """Add biography section to file if missing."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check if biography already exists
        if "## Biography" in content:
            print(f"  ⏭️  Biography already exists")
            return False
        
        # Find where to insert the biography (before the --- line)
        if "---" in content:
            parts = content.split("---", 1)
            new_content = parts[0].rstrip() + "\n" + biography_content.strip() + "\n\n---" + (parts[1] if len(parts) > 1 else "")
        else:
            # Add at the end if no separator found
            new_content = content.rstrip() + "\n" + biography_content.strip() + "\n"
        
        file_path.write_text(new_content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Restore biographies to all Cinderfork Foundry NPCs."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    foundry_dir = project_root / 'site_src' / 'monday' / 'npcs' / 'cinderfork_foundry'
    
    restored = 0
    skipped = 0
    failed = 0
    
    for filename, biography in NPC_BIOGRAPHIES.items():
        if filename == "skitter.md":
            continue  # Skip Skitter as it has special handling
            
        file_path = foundry_dir / filename
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            failed += 1
            continue
            
        print(f"Processing: {filename}")
        
        if restore_biography(file_path, biography):
            print(f"  ✅ Restored biography")
            restored += 1
        else:
            skipped += 1
    
    print("-" * 50)
    print(f"📊 Summary:")
    print(f"  ✅ Restored: {restored}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Failed: {failed}")

if __name__ == '__main__':
    main()