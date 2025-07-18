# D&D Adventure Content Style Guide

## Overview

This guide ensures consistent formatting and prevents layout issues when generating HTML from
markdown content. Follow these limits to maintain the authentic Player's Handbook appearance.

## Header Length Limits

### H1 (Main Section Titles)

* **Character Limit:**50-60 characters maximum* **Ideal Length:**30-45 characters* **Font:**Mr Eaves Small Caps, large size (0.987cm)* **Behavior:**Center-aligned, spans full width**Examples:**
*✅ Good: "Central Pumping Station" (23 chars)* ✅ Good: "Cistern & Spillways Guide" (26 chars)
*⚠️ Acceptable: "Cistern & Spillways - Puzzle Solutions" (38 chars)* ❌ Too Long: "Cistern &
Spillways - Puzzle Solutions Guide (GM Reference)" (58 chars)
**Fix for long titles:**Break into H1 + subtitle or use H2 for secondary info.

### H2 (Section Headers)
* **Character Limit:**40-50 characters maximum* **Ideal Length:**20-35 characters* **Font:**Mr Eaves Small Caps, medium size (0.705cm)* **Behavior:**Left-aligned with burgundy styling**Examples:**
*✅ Good: "Dialogue: Petros & Elara" (22 chars)* ✅ Good: "Quest Assignment" (16 chars)
*⚠️ Acceptable: "Environmental Hazards & Traps" (29 chars)* ❌ Too Long: "Detailed Environmental
Hazards & Complex Trap Mechanics" (55 chars)

### H3 (Subsection Headers)

* **Character Limit:**35-40 characters maximum* **Ideal Length:**15-30 characters* **Font:**Mr Eaves Small Caps, smaller size (0.529cm)* **Behavior:**Has golden underline border**Examples:**
*✅ Good: "Initial Encounter" (17 chars)* ✅ Good: "Treasure & Rewards" (18 chars)
*⚠️ Acceptable: "Player Approaches & NPC Reactions" (33 chars)* ❌ Too Long: "Detailed Player
Approaches & Complex NPC Reaction Matrix" (56 chars)

## Content Guidelines

### Dialogue Entries

* **Character Names:**Keep to 15 characters or less* **Action Descriptions:**50-80 characters maximum* **Dialogue Text:**Break long speeches into multiple entries* **Format:** `**Character:**(Action description)*"Dialogue text"*`
**Example:**```markdown*   **Petros:**(Grunting as he works)*"What do you want? This place is falling apart!"*
* **Elara:**(Without looking up)*"We need help. The system is failing."*```

### Read-Aloud Text Boxes
* **Line Length:**80-100 characters per line recommended* **Total Length:**3-4 sentences maximum per box* **Format:**Use `> ` prefix for read-aloud styling

### Image Captions
* **Character Limit:**60-80 characters maximum* **Keep descriptive but concise**### Table Headers
* **Column Headers:**20 characters maximum* **Cell Content:**40 characters maximum for readability

## Mobile Responsiveness

### Breakpoints to Consider
* **Desktop:**1200px+ (full layout)* **Tablet:**768px-1199px (may need shorter headers)* **Mobile:**<768px (aggressive length limits)

### Mobile-Specific Limits
* **H1:**40 characters maximum* **H2:**30 characters maximum* **H3:**25 characters maximum

## Best Practices

### Title Construction

1.**Lead with the most important word**2.**Use "&" instead of "and" to save space**3.**Avoid
unnecessary articles (a, an, the)**4.**Use abbreviations when clear (GM, NPC, PC)**### Examples of
Good Title Patterns:
* "Location Name"
*"Location Name - Area Code"* "Encounter Type: Specific Name"
*"System Name & Mechanics"

### Examples to Avoid:
* "A Detailed Guide to the Complex Mechanics of..."
*"Understanding the Intricate Relationships Between..."* "Comprehensive Analysis of Multiple System
Interactions..."

## Technical Specifications

### CSS Behavior

*Headers use `word-wrap: break-word` for emergency wrapping* Line-height ensures proper spacing when
wrapping occurs
*Center-aligned H1s need extra consideration for length

### Testing Guidelines

1.**Preview at different screen sizes**2.**Check for line wrapping in headers**3.**Ensure
readability on mobile devices**4.**Verify golden borders don't break on long H3s**## Content Review
Checklist

Before finalizing content:* [ ] All H1 headers under 50 characters
*[ ] All H2 headers under 40 characters* [ ] All H3 headers under 35 characters
*[ ] Dialogue entries properly formatted* [ ] No single line of text exceeds 100 characters
*[ ] Content tested on mobile layout* [ ] Headers remain readable when wrapped

## Revision Strategies

### For Overly Long Headers:

1. **Split into main title + subtitle**2.**Move descriptive text to first paragraph**3.**Use
abbreviations (Guide → G., Reference → Ref.)**4.**Remove unnecessary words**### Example Revision:
* **Before:**"Cistern & Spillways - Puzzle Solutions Guide (GM Reference)"* **After:**"Cistern & Spillways" (H1) + "Puzzle Solutions Guide" (H2)
This maintains hierarchy while preventing layout issues.

## Specific Fix Example

### Current Issue:

```markdown

# Cistern & Spillways - Puzzle Solutions Guide (GM Reference)

```**Character Count:**58 characters ❌ (Too long, causes wrapping)

### Recommended Fix Option 1 (Split Headers):

```markdown

# Cistern & Spillways

## Puzzle Solutions Guide (GM Reference)

```

### Recommended Fix Option 2 (Abbreviated):

```markdown

# Cistern & Spillways - Puzzle Guide (GM Ref.)

```**Character Count:**45 characters ✅ (Within acceptable range)

### Recommended Fix Option 3 (Content Restructure):

```markdown

# Cistern & Spillways
*GM Reference: Puzzle Solutions Guide*This guide helps Game Masters understand how players might solve...
```

## Implementation Notes

When updating existing content:
1.**Audit all headers**using character count
2.**Prioritize Option 1**(split headers) for better hierarchy
3.**Use Option 2**(abbreviation) when hierarchy isn't critical
4.**Use Option 3** (content restructure) for complex references
The goal is to maintain the D&D Player's Handbook visual standards while ensuring readability across
all devices.
