# Quickstart: LogSeq to Tana Converter

This guide provides a quick overview of how to use the `logseq-to-tana` CLI tool to convert your LogSeq vault to the Tana Intermediate Format.

## Prerequisites

-   Python 3.14+ installed.
-   `uv` for dependency management (recommended).

## Installation

```bash
# Clone the repository
git clone [repository-url]
cd logseq-to-obsidian

# Install dependencies
uv sync
```

## Usage

### Converting Your LogSeq Vault

To convert your LogSeq vault, use the `convert` command with the source path to your LogSeq vault and a destination path for the output Tana Intermediate Format files.

```bash
python -m src.logseq_converter convert /path/to/your/logseq-vault /path/to/output-directory
```

Replace `/path/to/your/logseq-vault` with the actual path to your LogSeq vault and `/path/to/output-directory` with the desired location for the converted files.

### Overwriting Existing Output

If your destination directory is not empty, the tool will normally ask for confirmation before overwriting. You can force the overwrite using the `--force` or `-f` flag:

```bash
python -m src.logseq_converter convert /path/to/your/logseq-vault /path/to/output-directory --force
```

### Example

Let's assume your LogSeq vault is located at `~/Documents/LogSeqVault` and you want the output in `~/Documents/TanaImport`.

```bash
python -m src.logseq_converter convert ~/Documents/LogSeqVault ~/Documents/TanaImport
```

Upon successful conversion, `~/Documents/TanaImport` will contain JSON files in the Tana Intermediate Format, one for each LogSeq page.

## Next Steps

-   Import the generated JSON files into Tana according to Tana's import instructions.
-   Review the converted content in Tana to ensure accuracy and completeness.
