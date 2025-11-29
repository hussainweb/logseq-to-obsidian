# Quickstart Guide: Parse Journal Blocks

This guide provides a quick setup and usage overview for the "Parse Journal Blocks" feature of the `logseq-to-obsidian` CLI tool.

## 1. Prerequisites

-   **Python 3.14+**: Ensure you have Python 3.14 or a newer version installed on your system.
-   **uv**: The project uses `uv` for dependency management. If you don't have it, install it:
    ```bash
    pip install uv
    ```

## 2. Setup

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd logseq-to-obsidian
    ```

2.  **Install dependencies**:
    Navigate to the project root and install the required dependencies using `uv`:
    ```bash
    uv sync
    ```

## 3. Usage

The `parse-journals` command allows you to process your Logseq daily notes and extract specific blocks into new Obsidian Markdown files.

**Basic Command Structure**:

```bash
python main.py parse-journals <path-to-logseq-journals-directory> <path-to-obsidian-vault-directory> [options]
```

-   `<path-to-logseq-journals-directory>`: The path to your Logseq `journals` directory (e.g., `/path/to/logseq_vault/journals`).
-   `<path-to-obsidian-vault-directory>`: The path to the root of your Obsidian vault (e.g., `/path/to/obsidian_vault`).

**Example**:

Let's assume your Logseq journals are in `/Users/username/Logseq/MyVault/journals` and your Obsidian vault is at `/Users/username/Obsidian/MyObsidianVault`.

```bash
python main.py parse-journals /Users/username/Logseq/MyVault/journals /Users/username/Obsidian/MyObsidianVault
```

### Options

-   `--dry-run`: Perform all parsing logic but do not write any changes to the file system. Use this to preview what changes would be made.
    ```bash
    python main.py parse-journals --dry-run /Users/username/Logseq/MyVault/journals /Users/username/Obsidian/MyObsidianVault
    ```
-   `--verbose` / `-v`: Increase output verbosity to see detailed processing steps.
-   `--log-file <path>`: Write logs to a specified file.

## 4. Expected Behavior

-   For each processed Logseq journal file, the tool will:
    -   Identify blocks tagged with `#links`, `#learnings`, `#achievements`, or `#highlights`.
    -   Create new Markdown files for each top-level item within these blocks. These files will be placed in corresponding subdirectories within your Obsidian vault (e.g., `ObsidianVault/Links/`, `ObsidianVault/Learnings/`).
    -   Each new file will have appropriate frontmatter (e.g., `date`, `url`, `github_url` for links).
    -   The original blocks will be removed from the Logseq journal file.
-   Progress and any errors will be logged to the console.

## 5. Next Steps

After running the quickstart, check your Obsidian vault for the newly created files and ensure the Logseq journal files have been modified as expected.
