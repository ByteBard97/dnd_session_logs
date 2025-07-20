# Project Brief: D&D Campaign Wiki Website

## 1. High-Level Objective

The goal is to create a modern, visually appealing, searchable, and responsive static website to serve as a comprehensive wiki for three separate Dungeons & Dragons campaigns. This site will be the central information hub for players.

## 2. The Core Problem & Past Failures

This project has encountered significant roadblocks due to an over-reliance on complex tooling that has proven difficult for AI assistants to manage reliably.

- **Initial Approach:** The site was first built with `MkDocs` and the `mkdocs-awesome-pages` plugin. This failed because the plugin's complex, distributed configuration (via `.pages` files) was consistently broken by LLM-driven changes.
- **Second Approach:** An attempt was made to switch to a simpler workflow using `Obsidian` and the `Webpage HTML Export` plugin. While more stable, the default output feels dated and lacks the "wow factor" desired.

**The primary requirement for the new technical approach is stability and ease of use for an AI assistant.** The chosen framework must have a well-documented, conventional structure that is not prone to catastrophic failure when making simple content or style changes.

## 3. Content & Information Architecture

The website's content is sourced from a collection of Markdown files, organized by campaign.

- **Top-Level Campaigns:**
  - `Monday Campaign`
  - `Wednesday Campaign`
  - `Friday Campaign`

- **Standard Content Types (Within each campaign):**
  - **Campaign Home Page:** A landing page introducing the specific campaign's theme and story.
  - **Player Characters:** A main page introducing the party, with sub-pages for individual character details and their personal quests.
  - **Session Logs:** Detailed, chronological notes for every game session.
  - **Session Recaps:** High-level summaries of each session.
  - **NPCs:** A directory of Non-Player Characters.
  - **Factions:** Information on key organizations or groups.
  - **Locations:** Descriptions of cities, regions, and dungeons, including maps.
  - **Lore:** Notes on world history and mythology.
  - **Items:** Details on important artifacts and magic items.

## 4. Functional & Aesthetic Requirements

- **Navigation:** The primary navigation menu must implement a "progressive disclosure" pattern. It should not show every link at once. Instead, it should allow users to intuitively explore the content hierarchy, for example, by clicking on a top-level campaign (`Monday`) to reveal its sub-sections (`Players`, `Locations`, etc.). A nested sidebar, a multi-level dropdown menu, or other modern UI patterns are all acceptable solutions.
- **Search:** The entire site's content must be searchable via a simple search bar.
- **Responsiveness:** The site must have a modern, responsive design that works flawlessly on both desktop and mobile browsers.
- **Theming:** The site must support per-campaign theming. Specifically, the **Monday Campaign** section requires a "sexy drow theme" – a dark, sleek design using a palette of deep purples and blues, with glowing accent colors for links and interactive elements.

## 5. Desired Outcome

The final result should be a stable, beautiful, and maintainable website that an LLM assistant can reliably support and extend in the future. The focus is on a high-quality user experience for the players and a frustration-free development experience. 