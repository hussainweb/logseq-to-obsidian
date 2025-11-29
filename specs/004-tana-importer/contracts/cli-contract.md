# CLI Contract: Tana Importer

**Date**: 2025-11-29

This document defines the command-line interface for the LogSeq to Tana importer.

## Command Structure

The new functionality will be exposed as a subcommand named `tana`.

```bash
logseq-converter tana [OPTIONS]
```

## Arguments and Options

### `--input-dir <DIRECTORY>` (Required)

- **Description**: The path to the directory containing the LogSeq graph to be imported.
- **Type**: `string` (Path)
- **Example**: `logseq-converter tana --input-dir /Users/me/my-logseq-graph`

### `--output-dir <DIRECTORY>`

- This option from the `obsidian` command will not be used for the `tana` command, as the output is sent directly to the Tana API.

### `--target-node-id <NODE_ID>` (Optional)

- **Description**: The ID of a specific node in Tana under which to import the content.
- **Default**: `INBOX`
- **Type**: `string`
- **Example**: `logseq-converter tana --input-dir ... --target-node-id "abcdef12345"`

## Authentication

The Tana API key must be provided via an environment variable.

- **Variable**: `TANA_API_KEY`
- **Description**: The API token generated from the Tana workspace settings.
- **Behavior**: The command will exit with an error message if this environment variable is not set.

## Example Usage

```bash
# Export the API key
export TANA_API_KEY="your-tana-api-token-here"

# Run the importer on a LogSeq graph
logseq-converter tana --input-dir /path/to/logseq/graph
```
