# Data Model: LogSeq to Tana Importer

**Date**: 2025-11-29

This document outlines the key data structures for the LogSeq to Tana importer.

## Conceptual Model

The importer reads data from a **LogSeq Graph** and transforms it into a series of API payloads to create **Tana Nodes**. The core challenge is mapping the flexible, file-based structure of LogSeq to the specific JSON format required by the Tana Input API.

## LogSeq Entities (Source)

These entities are already modeled in `src/logseq_converter/logseq/models.py`. The Tana converter will consume them.

- **`Block`**: Represents a line or block in a LogSeq file. It has `content`, a `level` of indentation, and may contain `tags` and `properties`.
- **`Page`**: Represents a single `.md` file in LogSeq, containing a tree of `Block` objects.

## Tana API Entities (Target)

These models will be created in `src/logseq_converter/tana/models.py`, likely using Pydantic for validation, to represent the JSON payload for the Tana API.

### `TanaNode`
Represents a single node to be sent to the Tana API.

- **`name`**: `string` - The primary content of the node.
- **`description`**: `string | None` - The node's description or extended content.
- **`supertags`**: `list[TanaSupertagRef] | None` - A list of supertags to apply to the node.
- **`children`**: `list[TanaNode | TanaField] | None` - Child nodes, which can be regular content nodes or field instances.

### `TanaSupertagRef`
A simple object to reference an existing supertag by its ID.

- **`id`**: `string` - The `nodeID` of the supertag in Tana.

### `TanaField`
Represents an instance of a field being applied to a node.

- **`type`**: `string` (constant: `"field"`)
- **`attributeId`**: `string` - The `nodeID` of the field definition in the Tana schema.
- **`children`**: `list[TanaNode]` - A list containing a single node whose `name` is the value of the field.

### `TanaAPIPayload`
The top-level object sent in the `POST` request to the Tana API.

- **`targetNodeId`**: `string` - The ID of the parent node in Tana (e.g., "INBOX", "SCHEMA").
- **`nodes`**: `list[TanaNode]` - A list of nodes to create, with a maximum of 100 per payload.
