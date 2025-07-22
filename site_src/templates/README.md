# Stat Block Templates

This directory contains reusable templates for D&D 5e stat blocks.

## Available Templates

### 1. Basic Creature Stat Block
- **File:** `creature_statblock.md`
- **Use:** Standard monsters and NPCs
- **Features:** Full stat block with all optional sections

### 2. Simplified NPC Stat Block
- **File:** `npc_statblock_simple.md`
- **Use:** Quick NPCs that don't need full combat stats
- **Features:** Streamlined format focusing on key abilities

### 3. Minion/Swarm Template
- **File:** `minion_statblock.md`
- **Use:** Groups of weak enemies or swarms
- **Features:** Simplified stats with swarm traits

## How to Use

1. Copy the template you need
2. Replace all [BRACKETED] placeholders with actual values
3. Delete any sections you don't need
4. Save in the appropriate campaign folder

## Quick Copy Examples

### For a Basic Humanoid NPC:
```markdown
> **Name Here**
> *Medium humanoid (race), alignment*
> 
> **Armor Class** 15 (studded leather)
> **Hit Points** 45 (6d8 + 18)
> **Speed** 30 ft.
> 
> | STR     | DEX     | CON     | INT     | WIS     | CHA     |
> |---------|---------|---------|---------|---------|---------|
> | 14 (+2) | 16 (+3) | 16 (+3) | 12 (+1) | 14 (+2) | 10 (+0) |
```

### For a Simple Beast:
```markdown
> **Name Here**
> *Large beast, unaligned*
> 
> **Armor Class** 13 (natural armor)
> **Hit Points** 76 (8d10 + 32)
> **Speed** 40 ft., swim 30 ft.
```

## Style Guidelines

- Use blockquotes (>) for the entire stat block
- Keep ability modifiers in parentheses
- List damage types after damage dice
- Include page breaks between major sections with `---`
- Always include CR and XP values