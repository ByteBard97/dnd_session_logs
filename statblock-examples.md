# Statblock Generator Examples

## How to Use

Just create a data object and call `createStatblock()`:

### Example 1: Simple Usage

```html
<div id="keelhauler-statblock"></div>

<script>
// Wait for page load to ensure statblock-generator.js is available
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    const keelhaulerData = {
      name: "Black Loch Keelhauler",
      size: "Large",
      type: "monstrosity",
      alignment: "unaligned",
      ac: "15 (natural armor)",
      hp: "126 (12d10 + 60)", 
      speed: "0 ft., swim 50 ft.",
      abilities: {
        str: ability(20),
        dex: ability(10), 
        con: ability(20),
        int: ability(5),
        wis: ability(12),
        cha: ability(7)
      },
      senses: "darkvision 60 ft., passive Perception 11",
      languages: "understands commands in Orcish but can't speak",
      challenge: "5 (1,800 XP)",
      traits: [
        {
          name: "Amphibious",
          description: "The Keelhauler can breathe air and water."
        },
        {
          name: "Beast of Burden", 
          description: "The Keelhauler is considered to be one size larger for the purpose of determining its carrying capacity."
        }
      ],
      actions: [
        {
          name: "Crushing Bite",
          description: "<i>Melee Weapon Attack:</i> +8 to hit, reach 5 ft., one creature. <i>Hit:</i> 16 (2d10 + 5) piercing damage."
        },
        {
          name: "Tail Slam", 
          description: "<i>Melee Weapon Attack:</i> +8 to hit, reach 10 ft., one creature. <i>Hit:</i> 12 (2d6 + 5) bludgeoning damage, and the target must succeed on a DC 16 Strength saving throw or be knocked prone."
        }
      ]
    };

    if (typeof createStatblock !== 'undefined' && typeof ability !== 'undefined') {
      document.getElementById('keelhauler-statblock').innerHTML = createStatblock(keelhaulerData);
    } else {
      console.error('Statblock generator functions not loaded');
    }
  }, 100);
});
</script>
```

### Example 2: Quick Dragon

```html
<div id="dragon-statblock"></div>

<script>
// Wait for page load to ensure statblock-generator.js is available
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    const dragonData = {
      name: "Young Red Dragon",
      size: "Large", 
      type: "dragon",
      alignment: "chaotic evil",
      ac: "18 (natural armor)",
      hp: "178 (17d12 + 68)",
      speed: "40 ft., climb 40 ft., fly 80 ft.",
      abilities: {
        str: ability(23),
        dex: ability(10),
        con: ability(19), 
        int: ability(14),
        wis: ability(11),
        cha: ability(19)
      },
      senses: "blindsight 30 ft., darkvision 120 ft., passive Perception 18",
      languages: "Common, Draconic", 
      challenge: "10 (5,900 XP)",
      traits: [
        {
          name: "Fire Immunity",
          description: "The dragon is immune to fire damage."
        }
      ],
      actions: [
        {
          name: "Fire Breath",
          description: "The dragon exhales fire in a 30-foot cone. Each creature in that area must make a DC 17 Dexterity saving throw, taking 56 (16d6) fire damage on a failed save, or half as much damage on a successful one."
        }
      ]
    };

    if (typeof createStatblock !== 'undefined' && typeof ability !== 'undefined') {
      document.getElementById('dragon-statblock').innerHTML = createStatblock(dragonData);
    } else {
      console.error('Statblock generator functions not loaded');
    }
  }, 100);
});
</script>
```

## Features

- ✅ **Super easy to use** - just JavaScript data objects
- ✅ **Automatic ability modifiers** - uses `ability(score)` helper 
- ✅ **Optional fields** - skip senses, languages, traits, etc.
- ✅ **Clean HTML output** - matches your current styling
- ✅ **Copy & paste friendly** - minimal code needed

## Usage in Markdown Files

In any markdown file, just add a div with an ID and a script tag!

### Example 3: Loading from JSON

For complex NPCs with lots of data, you can load from a JSON file:

```html
<div id="npc-statblock"></div>

<script>
// Wait for page load to ensure all scripts are available  
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    // Load statblock from JSON file
    loadJsonStatblock('json/my_npc.json', 'npc-statblock');
  }, 100);
});
</script>
```

The JSON format supports:
- ✅ **Complex spellcasting** - Full spell lists and slots
- ✅ **Equipment details** - Magical items with descriptions  
- ✅ **Bonus actions & reactions** - Automatically formatted
- ✅ **Automatic CR calculation** - Based on caster level
- ✅ **Rich attack formatting** - Converts attack objects to text