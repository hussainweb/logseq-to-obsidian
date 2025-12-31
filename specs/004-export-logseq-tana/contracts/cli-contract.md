# CLI Contract: LogSeq to Tana Converter

## Command: `logseq-to-tana convert`

### Description

This command converts an entire LogSeq vault into the Tana Intermediate Format.

### Usage

`logseq-to-tana convert <source_path> <destination_path> [options]`

### Arguments

-   `<source_path>`:
    -   **Required**: Yes
    -   **Description**: The file system path to the root of the LogSeq vault (e.g., `/path/to/my/logseq/vault`).
    -   **Validation**: Must be a valid, accessible directory containing LogSeq Markdown files. If not, the tool will report a detailed error message and exit.

-   `<destination_path>`:
    -   **Required**: Yes
    -   **Description**: The file system path to an output directory where the converted Tana Intermediate Format JSON files will be written.
    -   **Validation**: Must be a valid, accessible directory. If the directory is not empty, the tool will ask for confirmation before overwriting. If not confirmed, it will report a detailed error message and exit.

### Options

-   `--force`, `-f`:
    -   **Required**: No
    -   **Type**: Boolean flag
    -   **Description**: Forces overwrite of the destination directory if it's not empty, without asking for confirmation.

### Exit Codes

-   `0`: Successful conversion.
-   `1`: General error (e.g., invalid paths, conversion errors). Detailed error messages will be presented to the user on `stderr`.
