# Data Model: Parse Journal Blocks

## Entities

### Journal

-   **Description**: Represents a Logseq daily note.
-   **Attributes**:
    -   `date`: (DateTime) The date of the journal, derived from its filename.
    -   `content`: (String) The raw Markdown content of the journal file.
    -   `blocks`: (List of Block) A collection of identified blocks within the journal.
-   **Relationships**: Contains multiple `Block` entities.

### Block

-   **Description**: A distinct section within a `Journal` identified by a heading.
-   **Attributes**:
    -   `type`: (Enum: `links`, `learnings`, `achievements`, `highlights`, `other`) The category of the block.
    -   `heading`: (String) The Markdown heading text (e.g., "## #links").
    -   `raw_content`: (String) The raw Markdown content of the block, including top-level items and sub-items.
    -   `top_level_items`: (List of Link Item or Content Item) Parsed top-level items within the block.
-   **Relationships**: Belongs to a `Journal`. Contains multiple `Link Item` or `Content Item` entities.

### Link Item

-   **Description**: A top-level item specifically from a `#links` block.
-   **Attributes**:
    -   `caption`: (String) The displayed text for the link. Used for filename generation.
    -   `url`: (String) The primary URL of the link.
    -   `github_url`: (String, Optional) A GitHub URL associated with the link, if present.
    -   `sub_items_content`: (String) Raw Markdown content of any sub-bullet points.
    -   `frontmatter_properties`: (Dictionary) Key-value pairs for additional frontmatter (e.g., `date`, `url`, `github_url`).
-   **Relationships**: Belongs to a `Block` of type `links`.

### Content Item

-   **Description**: A top-level item from `#learnings`, `#achievements`, or `#highlights` blocks.
-   **Attributes**:
    -   `description_preview`: (String) The first few words of the bullet point, used for filename generation.
    -   `raw_content`: (String) The raw Markdown content of the top-level item and its sub-items.
    -   `sub_items_content`: (String) Raw Markdown content of any sub-bullet points.
    -   `frontmatter_properties`: (Dictionary) Key-value pairs for additional frontmatter (e.g., `date`).
-   **Relationships**: Belongs to a `Block` of type `learnings`, `achievements`, or `highlights`.

### Markdown File

-   **Description**: The output file generated for each extracted `Link Item` or `Content Item`.
-   **Attributes**:
    -   `filename`: (String) The unique name of the Markdown file, derived from the item's caption/description.
    -   `path`: (String) The full path to the file within the Obsidian vault (e.g., `ObsidianVault/Links/Link Heading.md`).
    -   `frontmatter`: (Dictionary) YAML frontmatter containing properties like `date`, `url`, `github_url`.
    -   `body`: (String) The Markdown content of the extracted item (sub-items).
-   **Relationships**: Generated from a `Link Item` or `Content Item`.
