# Data Model: Export LogSeq to Tana Intermediate Format

This document outlines the key entities involved in the conversion process from LogSeq to Tana Intermediate Format, detailing their attributes and relationships.

## LogSeq Entities

### LogSeq Page

-   **Description**: Represents a single Markdown file within a LogSeq vault. This is the primary unit of organization in LogSeq and corresponds to a Tana Node.
-   **Attributes**:
    -   `filename`: (String) The name of the Markdown file, which typically corresponds to the page title.
    -   `content`: (String) The raw Markdown content of the page.
    -   `blocks`: (List of LogSeq Block) A hierarchical list of blocks contained within the page.
-   **Relationships**: Contains multiple `LogSeq Block` entities.

### LogSeq Block

-   **Description**: Represents a bullet point (line) within a LogSeq page. Blocks can contain text, links, and properties, and can be nested to form a hierarchical structure.
-   **Attributes**:
    -   `text`: (String) The main content of the block.
    -   `properties`: (Dictionary) Key-value pairs associated with the block (e.g., `key:: value`). As per clarification, only `tags` will be mapped to Tana SuperTags. Other properties will be ignored.
    -   `children`: (List of LogSeq Block) Nested blocks, representing the hierarchical structure.
    -   `links`: (List of String) References to other LogSeq pages (`[[wiki-links]]`).
    -   `tags`: (List of String) Hashtags (`#tags`) associated with the block.
-   **Relationships**: Can be nested within other `LogSeq Block` entities, and belongs to a `LogSeq Page`.

## Tana Entities (Intermediate Format)

**Note**: The precise structure of Tana Node and Tana Field is derived from the Tana Intermediate Format specification (`types.ts` and related files). The following descriptions are based on general understanding and the information available, and will be refined once the full `Node` type definition is accessible.

### Tana Node

-   **Description**: The fundamental object in Tana. Represents a piece of information, which can be a page, a block, or a field value.
-   **Attributes**:
    -   `name`: (String) The display name or title of the node.
    -   `uid`: (String) A unique identifier for the node.
    -   `content`: (String, Optional) The textual content of the node, if applicable.
    -   `children`: (List of Tana Node, Optional) Nested nodes, forming a hierarchical structure.
    -   `fields`: (Dictionary of Tana Field, Optional) Key-value attributes associated with the node.
    -   `supertags`: (List of Tana SuperTag, Optional) References to SuperTags, defining the type or schema of the node.
    -   `type`: (String, e.g., 'NODE', 'FIELD', 'TAG') The type of Tana object.
-   **Relationships**: Can have `children` (other Tana Nodes) and `fields` (Tana Fields), and be associated with `supertags`.

### Tana Field

-   **Description**: A key-value attribute associated with a Tana Node. Analogous to LogSeq properties.
-   **Attributes**:
    -   `name`: (String) The name of the field (key).
    -   `value`: (Any) The value of the field. This can be text, a reference to another Node, a date, etc.
-   **Relationships**: Belongs to a `Tana Node`.

### Tana SuperTag

-   **Description**: A special attribute in Tana used to define a type of node with a specific structure and set of fields. LogSeq `#tags` are mapped to Tana SuperTags.
-   **Attributes**:
    -   `name`: (String) The name of the SuperTag.
    -   `uid`: (String) A unique identifier for the SuperTag.
-   **Relationships**: Can be applied to a `Tana Node`.

## Mapping Logic Summary

-   Each `LogSeq Page` will primarily convert to a `Tana Node`.
-   `LogSeq Block` entities (including their text and hierarchical structure) will translate into nested `Tana Node` `children`.
-   `LogSeq [[wiki-links]]` and `#tags` will be converted into Tana's reference format for nodes and `supertags` respectively.
-   LogSeq properties: The `tags` property will map to Tana `supertags`. Other properties will be ignored as per clarification.
-   The conversion will adhere to the latest stable Tana Intermediate Format specification.
