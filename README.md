# LogSeq Converter

A Python tool to convert LogSeq graphs to Obsidian vaults or Tana workspaces.

## Features

- **Obsidian Conversion**: Convert LogSeq markdown files to Obsidian-compatible format
- **Tana Import**: Import LogSeq content directly into Tana workspaces via API
- Block reference resolution
- Asset copying
- Journal and page processing

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/logseq-to-obsidian.git
cd logseq-to-obsidian

# Install dependencies using uv
uv sync
```

## Usage

### Convert to Obsidian

```bash
logseq-converter convert /path/to/logseq/graph /path/to/obsidian/vault
```

Options:
- `-v, --verbose`: Enable verbose logging
- `--dry-run`: Perform a dry run without writing changes

### Import to Tana

```bash
# Set your Tana API key
export TANA_API_KEY="your-tana-api-token"

# Import to Tana
logseq-converter tana --input-dir /path/to/logseq/graph
```

Options:
- `--input-dir`: Source LogSeq graph directory (required)
- `--target-node-id`: Target node ID in Tana (default: INBOX)
- `-v, --verbose`: Enable verbose logging
- `--dry-run`: Perform a dry run without making API calls

For more details on Tana import, see the [Tana Importer Quickstart](specs/004-tana-importer/quickstart.md).

## Development

```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Format code
uv run ruff format .
```

## Requirements

- Python 3.14+
- uv package manager
- For Tana import: Tana API key

## License

[Your License Here]
