# LogSeq Converter

A flexible command-line interface (CLI) tool designed to migrate your LogSeq graph to other note-taking formats, with a primary and comprehensive focus on **Obsidian**. 

It also supports exporting notes to other targets, including **Tana** (Intermediate Format JSON), **Tolaria** (Markdown), and **Blinko** (via API).

---

## 🎯 Primary Destination: Obsidian

The converter features a robust pipeline built to ensure a clean, structured, and search-friendly transition of your LogSeq graph to a fully native **Obsidian** vault.

### Supported Obsidian Features

* **Daily Notes (Journals)**
  * Automatically transforms daily note filenames from LogSeq format (`YYYY_MM_DD.md`) to standard Obsidian format (`Daily/YYYY-MM-DD.md`).
  * Transforms LogSeq inline date links (e.g., `[[15 Nov 2025]]`) to Obsidian-compatible Daily Note links (`[[Daily/2025-11-15]]`).
* **Nested Folders for Namespaces**
  * Converts LogSeq namespace page names using `___` (e.g., `Category___Subcategory.md`) into a nested folder hierarchy (`Category/Subcategory.md`) in Obsidian.
* **Block References & Anchors**
  * Scans the source graph for block UUIDs (`id:: uuid`) and transforms them into native Obsidian block anchors (`^blockid`).
  * Converts block references (`((uuid))`) into Obsidian internal block links pointing to the target file and anchor (`[[filename#^blockid]]`).
* **Metadata & Property Handling**
  * Promotes LogSeq block/page properties (`key:: value`) into a clean YAML frontmatter block at the top of files.
  * Filters out LogSeq-specific UI/presentation properties (e.g., `heading::`, `collapsed::`, `icon::`, `title::`, `exclude-from-graph-view::`) to keep your Obsidian notes clutter-free.
  * Strips LogSeq task metadata like `:LOGBOOK:` entries and clock tracking tables.
* **Asset Migration**
  * Copies your entire `assets` directory to the destination vault root, maintaining all references to local images, PDFs, and media attachments.
* **Vault Configuration & Plugins**
  * Bootstraps the `.obsidian` configuration folder in the destination vault.
  * Enables the **Daily Notes** core plugin and configures its format (`YYYY-MM-DD`) and folder path (`Daily`) to align with the conversion output.
  * Programmatically fetches, installs, and enables the latest release of the **Notebook Navigator** community plugin from GitHub to provide improved navigation for daily journals out of the box.

### Automated Section Extraction
Keep your daily journals clean by extracting specific reflection/resource sections into separate folders. The converter scans daily notes for sections tagged or headed with `#links`, `#learnings`, `#achievements`, or `#highlights`.
* Each top-level bullet item under these headers is extracted into its own Markdown file in the corresponding folder (e.g., `Links/`, `Learnings/`, `Achievements/`, `Highlights/`).
* Filenames are automatically generated from link captions (for `#links`) or the first few words of the bullet point (sanitized for illegal characters).
* **Metadata extraction**: For `#links`, the converter extracts `url` and `github_url` properties and places them in the new file's YAML frontmatter, along with the source journal's `date`.
* The entire block is cleanly removed from the original daily note. Empty journals resulting from this extraction are omitted to avoid blank file clutter.

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.14+
* [uv](https://github.com/astral-sh/uv) (recommended Python package installer and runner)

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/hussainweb/logseq-to-obsidian.git
   cd logseq-to-obsidian
   ```
2. Set up the virtual environment and sync dependencies:
   ```bash
   uv venv
   uv sync
   ```

---

## 🚀 Usage

All conversion commands are invoked via Python from the project root using `uv run`:

```bash
uv run python -m logseq_converter.cli <subcommand> [options]
```

### 1. Convert to Obsidian (Primary)

```bash
uv run python -m logseq_converter.cli obsidian <source_logseq_path> <destination_obsidian_path> [options]
```

> [!IMPORTANT]
> The destination directory must either not exist or be completely empty to prevent accidental data loss.

**Options:**
* `-v`, `--verbose`: Enable detailed progress output.
* `--dry-run`: Run the entire pipeline in simulation mode without writing files/folders to disk.

**Example:**
```bash
uv run python -m logseq_converter.cli obsidian ~/notes/logseq ~/notes/obsidian -v
```

---

## 🔮 Secondary Destinations

For users looking to export their LogSeq data elsewhere, the tool provides these subcommands:

### 2. Export to Tana
Converts pages, journals, and nested block structures into a single file adhering to the **Tana Intermediate Format (TIF)**:

```bash
uv run python -m logseq_converter.cli tana <source_logseq_path> <destination_file.json> [options]
```
* **Features**: Maps nested block levels to Tana child nodes, formats wiki-links/tags, and maps LogSeq `tags::` to Tana supertags.
* **Options**: Use `-f` or `--force` to overwrite the output file if it already exists.

### 3. Convert to Tolaria
Converts journals and pages to Tolaria's Markdown formatting guidelines (placing daily notes into a `journal/` directory):

```bash
uv run python -m logseq_converter.cli tolaria <source_logseq_path> <destination_tolaria_path> [options]
```

### 4. Sync to Blinko
Exports LogSeq notes directly to a self-hosted **Blinko** instance using the API:

```bash
# Set your Blinko access token
export BLINKO_TOKEN="your-blinko-api-token"

# Sync notes
uv run python -m logseq_converter.cli blinko <source_logseq_path> https://your-blinko-instance.com/api
```
To clear all notes in your Blinko instance, you can use:
```bash
uv run python -m logseq_converter.cli blinko:delete-all https://your-blinko-instance.com/api
```

---

## 🧪 Testing & Linting

Verify your environment by running the test suite:
```bash
uv run pytest
```

Check code formatting and linting:
```bash
uv run ruff check .
```

---

## 📖 Documentation

For a detailed look at the conversion rules, schemas, and verification steps:
* [System Specifications](docs/specifications.md): Details on modular design, property pruning/filtering, block references, and target format schemas.
* [Verification & Manual Testing Guide](docs/verification_guide.md): Step-by-step instructions on creating a mock graph to test and verify the CLI conversion commands.

