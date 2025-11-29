# Research: Tana Input API

**Date**: 2025-11-29
**Source**: [Tana Input API Documentation](https://tana.inc/docs/input-api)

## Summary
The Tana Input API provides a mechanism to programmatically add content to a Tana workspace. It consists of a single primary endpoint that accepts JSON payloads. Authentication is handled via a per-workspace API token.

## Key Findings

### 1. Endpoint & Authentication
- **URL**: `https://europe-west1-tagr-prod.cloudfunctions.net/addToNodeV2`
- **Method**: `POST`
- **Authentication**: A bearer token must be included in the `Authorization` header.
  - `Authorization: Bearer <YOUR_TANA_API_TOKEN>`
- **API Token Source**: The token is generated within Tana's settings on a per-workspace basis and should be read from an environment variable (e.g., `TANA_API_KEY`) as per the user request.

### 2. Core JSON Structure
The API expects a JSON object with two main keys: `targetNodeId` and `nodes`.

```json
{
  "targetNodeId": "INBOX", // or "SCHEMA", "LIBRARY", or a specific node ID
  "nodes": [
    // ... array of node objects
  ]
}
```

- **`targetNodeId`**: Determines where the new nodes will be created.
    - `INBOX`: Adds nodes to the user's inbox.
    - `SCHEMA`: Required when creating new supertags or fields.
    - `LIBRARY`: Adds nodes to the library.
    - `<node-id>`: Adds nodes as children of a specific existing node.

### 3. Node Object Structure
Each object in the `nodes` array represents a piece of content to be created.

**Basic Node**:
```json
{
  "name": "This is the node content",
  "description": "Optional extended description for the node."
}
```

**Node with Supertags**:
Supertags are applied by referencing their existing `nodeID`.
```json
{
  "name": "The Hobbit",
  "supertags": [
    { "id": "existing-supertag-id-1" },
    { "id": "existing-supertag-id-2" }
  ]
}
```

**Node with Fields (as children)**:
Fields are added as children of a node. The `attributeId` refers to the `nodeID` of an existing field definition.
```json
{
  "name": "A node with a field",
  "children": [
    {
      "type": "field",
      "attributeId": "existing-field-id",
      "children": [
        { "name": "This is the value of the field" }
      ]
    }
  ]
}
```

### 4. Creating SupeTags and Fields
To create supertags or fields, the `targetNodeId` must be `SCHEMA`. They are created like regular nodes but with a specific system-level supertag applied to them.
- **Create a Supertag**: A node named "My Supertag" with the system supertag `SYS_T01`.
- **Create a Field**: A node named "My Field" with the system supertag `SYS_T02`.

### 5. Rate Limits & Constraints
- **Frequency**: Max 1 call per second per API token.
- **Batch Size**: Max 100 nodes per API call.
- **Payload Size**: Max 5000 characters per API call.
- **Workspace Size**: The API will not sync on workspaces with over 750,000 nodes.

## Decisions for Implementation
- **Batching**: The converter must batch LogSeq blocks into groups of 100 to stay within the rate limit.
- **Throttling**: A 1-second delay must be implemented between each API call.
- **Schema Management**: The importer will need a strategy to manage supertags and fields. It should first check if a supertag/field exists in Tana. If not, it must create it by targeting the `SCHEMA` before using it for content nodes. This requires getting the `nodeID` of the newly created schema elements. The API does not appear to return the IDs of created nodes, which presents a significant challenge. **[NEEDS CLARIFICATION]** How to get the `nodeID` of a newly created supertag or field to use it when creating content nodes?
- **Error Handling**: The implementation must gracefully handle API errors, including rate limiting (HTTP 429), authentication failures (HTTP 401/403), and validation errors.
