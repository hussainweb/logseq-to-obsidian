# System Specifications

This document outlines the active and implemented specifications for the LogSeq Converter tool. It defines the behavior, data transformations, and rules for converting LogSeq graphs to other formats.

---

## 🏛️ Architecture & Modules

The application is structured modulerly to separate the parsing of LogSeq markdown and models from the output-specific target writers.

```
src/logseq_converter/
├── __init__.py
├── cli.py             # CLI commands, argument parsing, and execution entrypoint
├── stats.py           # Shared conversion metrics collector
├── utils.py           # Directory validation, asset copying, filename sanitization
├── logseq/            # Parser and internal data models (AST representation)
├── obsidian/          # Obsidian-flavored Markdown output generation
├── tana/              # Tana Intermediate Format JSON generation
├── tolaria/           # Tolaria Markdown output generation
└── blinko/            # Blinko API sync client and converter
```

---

## 🎯 Target: Obsidian Vault Conversion

The Obsidian writer converts a LogSeq graph into a directory structured as an Obsidian vault.

### 1. Filename & Directory Transformations
* **Daily Journals**: Files under the LogSeq `journals/` directory named `YYYY_MM_DD.md` are transformed and saved under `Daily/YYYY-MM-DD.md`.
* **Namespaces**: Files in the LogSeq `pages/` directory containing the triple-underscore separator `A___B.md` are converted into a nested directory structure `A/B.md`.
* **Assets**: The entire `assets/` folder is copied directly to the vault root as `assets/` to ensure all local images and attachments remain linked.

### 2. Markdown & Property Transformations
* **Property Promotion**: Key-value metadata defined inline using the double-colon syntax `key:: value` is promoted to YAML frontmatter at the top of the Markdown file.
* **Property Exclusions**: Certain LogSeq-specific presentation properties are automatically removed as they do not apply to Obsidian. The excluded properties are:
  - `heading`
  - `collapsed`
  - `icon`
  - `title`
  - `exclude-from-graph-view`
* **Logbook Cleanup**: All Logseq `:LOGBOOK:` clock-tracking sections (e.g. `CLOCK: [2025-11-27 Thu 10:00]--[2025-11-27 Thu 11:00] =>  01:00`) are removed to keep task lines clean.
* **Block References & IDs**:
  - LogSeq block UUIDs (`id:: uuid`) are transformed into native Obsidian block anchors (`^blockid`) appended to the end of the block.
  - LogSeq block references (`((uuid))`) are translated to internal links targeting the correct file and anchor: `[[filename#^blockid]]`.
* **Date Links**: Inline date links like `[[15 Nov 2025]]` are converted to links pointing to the daily note `[[Daily/2025-11-15]]`.

### 3. Journal Section Extraction
The converter extracts high-level content blocks tagged or headed with `#links`, `#learnings`, `#achievements`, or `#highlights` in daily journals:
* **Target Directories**: Items are saved into matching subdirectories (`Links/`, `Learnings/`, `Achievements/`, `Highlights/`).
* **Bullet Promotion**: Each top-level bullet point under these headers becomes a separate Markdown file, with its sub-bullets preserved as the file content.
* **Filename Sanitization**: Filenames are generated from the link caption (for `#links`) or the first few words of the bullet, sanitized of illegal filesystem characters. Case-insensitive filename conflicts are handled by appending a unique counter suffix.
* **Metadata Promotion**: 
  - The source journal's date is added as a `date` property in the new file's YAML frontmatter.
  - For `#links`, the converter extracts `url` and `github_url` properties and places them in the frontmatter.
* **Source Cleanup**: The extracted sections are deleted from the original daily journals. If a journal file is empty after extraction, the file itself is deleted/omitted.

---

## 🔮 Target: Tana Intermediate Format

Converts the entire LogSeq vault into a single JSON file adhering to the Tana Intermediate Format (TIF) for seamless import into Tana:
* **Node Hierarchy**: LogSeq's nested bullet points are converted into Tana's tree-like `children` node structure.
* **References**: `[[wiki-links]]` and `#tags` are converted to Tana references.
* **Supertags**: LogSeq's `tags` property is mapped to Tana supertags.
* **Exclusions**: Other LogSeq block properties that don't map directly to Tana fields are ignored. Advanced features like queries and whiteboards are bypassed.

---

## 🔮 Target: Tolaria Markdown

Converts LogSeq pages and journals into Tolaria-flavored Markdown:
* **Journal Directory**: Daily journals are transformed and saved into a subdirectory named `journal/` (lowercase, singular).
* **Metadata Normalization**: Normalizes and formats YAML frontmatter, injecting a `type: journal` property into journals.
* **Block ID Removal**: Removes LogSeq block UUIDs (`id:: uuid`) to keep the Markdown output completely clean.

---

## 🔮 Target: Blinko Note Sync

Exports LogSeq pages and journals directly to a self-hosted Blinko note-taking instance using its HTTP API:
* **Authentication**: Requires a `BLINKO_TOKEN` environment variable.
* **Upsert Client**: Automatically upserts parsed notes to Blinko, rates-limiting calls to prevent overload.
* **Purge Command**: Includes a `blinko:delete-all` subcommand to completely wipe notes from the Blinko instance (useful for resets/re-syncs).
