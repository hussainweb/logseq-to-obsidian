# Quickstart Guide

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd logseq-to-obsidian

# Install dependencies
uv sync
```

## Usage

The tool is a CLI application.

```bash
# Basic conversion
uv run logseq-to-obsidian convert /path/to/logseq-vault /path/to/obsidian-vault

# Get help
uv run logseq-to-obsidian --help
```

### Arguments

- `SOURCE`: Path to the existing LogSeq vault directory.
- `DESTINATION`: Path to the *empty* directory where the Obsidian vault will be created.

### Options

- `--verbose`, `-v`: Enable debug logging.
- `--version`: Show version information.

## Example

```bash
uv run logseq-to-obsidian convert ~/Documents/LogSeq/MyGraph ~/Documents/Obsidian/MyGraph
```

## Troubleshooting

- **"Destination is not empty"**: Ensure the target folder is empty.
- **"Source not found"**: Check if the source path exists.
