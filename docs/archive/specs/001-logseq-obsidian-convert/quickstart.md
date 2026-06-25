# Quickstart: LogSeq to Obsidian Converter

**Date**: 2025-11-27
**Status**: Done

This guide provides a brief overview of how to install and run the LogSeq to Obsidian Converter CLI tool.

## Prerequisites

- Python 3.14+
- `uv` installed (`pip install uv`)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd logseq-to-obsidian
    ```

2.  **Create a virtual environment and install dependencies**:
    ```bash
    uv venv
    uv sync
    ```

## Usage

The primary command for running the conversion is `logseq-to-obsidian`.

### Command Syntax

```bash
logseq-to-obsidian <source_directory> <destination_directory> [options]
```

-   `<source_directory>`: The path to your source LogSeq graph.
-   `<destination_directory>`: The path to the directory where the Obsidian vault will be created. **This directory MUST be empty.**

### Options

-   `-v`, `--verbose`: Enable verbose logging to see detailed information about the conversion process.

### Example

To convert a LogSeq graph located at `~/notes/logseq` to a new Obsidian vault at `~/notes/obsidian`:

```bash
logseq-to-obsidian ~/notes/logseq ~/notes/obsidian
```

The tool will then perform the conversion, showing a progress indicator:

```
Processing files... [ spinning wheel ] processing journal/2025_11_27.md
```

Upon completion, the `~/notes/obsidian` directory will be a fully converted Obsidian vault.

### Error Handling

-   If the destination directory is not empty, the tool will exit with an error to prevent accidental data loss.
-   If the source directory does not not exist, the tool will exit with an error.
-   Warnings for broken links or un-parsable files will be printed to the console (`stderr`).