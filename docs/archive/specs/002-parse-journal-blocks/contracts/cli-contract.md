# CLI Contract: Parse Journal Blocks

This document outlines the functional contract for the `logseq-to-obsidian` CLI tool, specifically for the "Parse Journal Blocks" feature. It describes the expected invocation, arguments, and outcomes.

## Command Invocation

The feature will likely be integrated as a subcommand or an option within the existing `logseq-to-obsidian` CLI.

**Proposed Invocation**:
```bash
logseq-to-obsidian parse-journals <path-to-logseq-journals-directory> <path-to-obsidian-vault-directory> [options]
```

## Arguments

-   `<path-to-logseq-journals-directory>` (Required):
    -   **Description**: The absolute or relative path to the directory containing Logseq journal Markdown files.
    -   **Type**: String (Path)
    -   **Validation**: Must be an existing, readable directory.

-   `<path-to-obsidian-vault-directory>` (Required):
    -   **Description**: The absolute or relative path to the root of the Obsidian vault where the new Markdown files will be created and existing journal files will be modified.
    -   **Type**: String (Path)
    -   **Validation**: Must be an existing, writable directory.

## Options

-   `--dry-run` (Optional):
    -   **Description**: If specified, the command will perform all parsing and processing logic but will not write any changes to the file system. It will report what *would* have happened.
    -   **Type**: Boolean Flag
    -   **Default**: `False`

-   `--verbose` / `-v` (Optional):
    -   **Description**: Increases logging verbosity to include detailed processing steps.
    -   **Type**: Boolean Flag
    -   **Default**: `False`

-   `--log-file <path>` (Optional):
    -   **Description**: Specifies a file to which detailed logs should be written, in addition to console output.
    -   **Type**: String (Path)
    -   **Validation**: Must be a writable path.

## Behavior

Upon invocation, the CLI tool will:

1.  **Read Journal Files**: Iterate through all Markdown files within `<path-to-logseq-journals-directory>`, identifying them as journal files (e.g., by filename pattern `YYYY_MM_DD.md` or similar, to be refined during implementation).
2.  **Parse Blocks**: For each journal file, it will parse the content to identify `#links`, `#learnings`, `#achievements`, and `#highlights` blocks.
3.  **Extract Items**: Within identified blocks, it will extract top-level items.
    -   For `#links` blocks, it will extract `Link Item`s with `caption`, `url`, and `github_url`.
    -   For other blocks, it will extract `Content Item`s.
4.  **Generate New Markdown Files**: For each extracted `Link Item` or `Content Item`:
    -   A new Markdown file will be created in a corresponding subdirectory within `<path-to-obsidian-vault-directory>` (e.g., `Links/`, `Learnings/`).
    -   The filename will be derived from the item's caption or a portion of its content.
    -   Unique filenames will be ensured (e.g., by appending a counter).
    -   The file's frontmatter will be populated with a `date` property (from the journal) and relevant item-specific properties (`url`, `github_url`).
    -   The body of the new file will contain the sub-items associated with the extracted top-level item.
5.  **Modify Original Journal Files**: After successful extraction, the identified blocks (including their headings) will be removed from the original journal Markdown files in `<path-to-logseq-journals-directory>`.
6.  **Error Handling**:
    -   Errors during processing of a single file will be logged (to console and optionally to `--log-file`).
    -   Processing will continue for other files.
    -   Files causing errors will remain in their original state.
7.  **Logging**: Essential progress (file started, file completed, errors) will be logged to the console (and `--log-file` if specified) with timestamps.

## Exit Codes

-   `0`: All specified journal files were processed, and modifications/creations were attempted successfully (even if some individual files had errors, as long as the overall process completed).
-   `1`: General error during CLI invocation (e.g., invalid arguments, directories not found).
-   `2`: Fatal error that prevented processing of any files (e.g., critical configuration issue).
