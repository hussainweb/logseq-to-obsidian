# CLI Contract

**Version**: 1.0

## Principle: Interface Stability

The command-line interface (CLI) of the `logseq-to-obsidian` converter is a public contract and MUST remain stable and unchanged throughout this refactoring effort.

## Requirements

1.  **Command-Line Arguments & Options**: All existing arguments and options must continue to be accepted, and their behavior must not change.
    -   `--input-dir`: The path to the Logseq graph directory.
    -   `--output-dir`: The path to the Obsidian vault directory.
    -   `--journal-notes-filter`: A filter to apply to journal notes.
    -   Any other existing flags or options.

2.  **Output**: For a given set of input files and arguments, the resulting file and folder structure in the output directory MUST be identical to the structure produced before the refactoring. The content of each generated Markdown file MUST also be identical.

3.  **Exit Codes**: The application MUST continue to use standard exit codes:
    -   `0` on successful completion.
    -   A non-zero integer on failure, with appropriate error messages sent to `stderr`.

## Verification

The stability of this contract will be verified by:
-   Ensuring all existing integration tests pass. These tests implicitly cover the CLI contract by running the tool with specific inputs and asserting the output is correct.
-   Manually running the tool with a sample dataset and `diff`-ing the output against a known-good version.
