# Quickstart: LogSeq to Tana Importer

This guide provides the basic steps to use the LogSeq to Tana importer.

## Prerequisites

1.  You have a LogSeq graph stored locally on your machine.
2.  You have generated an API token from your Tana workspace.

## Steps

### 1. Set Your Tana API Key

The importer requires your Tana API token to be set as an environment variable named `TANA_API_KEY`.

Open your terminal and run the following command, replacing `<YOUR_TANA_API_TOKEN>` with your actual token:

```bash
export TANA_API_KEY="<YOUR_TANA_API_TOKEN>"
```

**Note**: This environment variable is only set for your current terminal session. You will need to set it again if you open a new terminal.

### 2. Run the Importer

Once the API key is set, you can run the importer. The command requires one argument: the path to your LogSeq graph directory.

Execute the following command, replacing `/path/to/your/logseq-graph` with the actual path:

```bash
logseq-converter tana --input-dir /path/to/your/logseq-graph
```

The tool will begin parsing your LogSeq files and sending them to your Tana workspace. By default, content will be added to your Tana **Inbox**.

### (Optional) Importing to a Specific Node

If you want to import the content under a specific node in Tana (instead of the Inbox), you can use the `--target-node-id` option. You will need to get the Node ID from Tana (e.g., by using the `Copy link` command on a node).

```bash
logseq-converter tana --input-dir /path/to/your/logseq-graph --target-node-id "<TANA_NODE_ID>"
```
