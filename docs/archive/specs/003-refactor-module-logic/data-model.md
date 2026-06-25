# Data Model

This document outlines the key data structures passed between the different modules of the application. These models are defined in `src/logseq_converter/logseq/models.py`.

The core data flow is:
1.  The `logseq` module parses raw Logseq files into `Page` and `Journal` objects, which contain `Block` objects.
2.  During the conversion process, this structured data may be further processed into semantic objects like `LinkItem` or `ContentItem`.
3.  The `obsidian` module receives these objects and is responsible for converting them into Obsidian-flavored Markdown text.

---

## Core Models

### `Block`
Represents a single block (a bullet point) in Logseq.
- **`content`**: The raw text content of the block, including Logseq-specific properties.
- **`cleaned_content`**: The text content of the block after Logseq-specific properties have been removed, but retaining accurate Markdown (links, formatting).
- **`id`**: The optional unique ID of the block.
- **`properties`**: A dictionary of key-value properties associated with the block.
- **`children`**: A list of nested `Block` objects.

### `Page`
Represents a standard Logseq page.
- **`filename`**: The name of the source file.
- **`content`**: The raw text content of the page before block parsing begins, including Logseq-specific properties.
- **`cleaned_content`**: The text content of the page after Logseq-specific properties have been removed from its blocks, but retaining accurate Markdown (links, formatting).
- **`blocks`**: A list of top-level `Block` objects on the page.
- **`properties`**: A dictionary of page-level properties.

### `Journal`
Represents a Logseq journal page.
- **`filename`**: The name of the source file (e.g., `2025-11-29.md`).
- **`date`**: The `datetime.date` object representing the journal entry date.
- **`content`**: The raw text content of the journal before block parsing.
- **`blocks`**: A list of top-level `Block` objects in the journal.

### `Graph`
Represents the entire Logseq graph to be converted.
- **`source_path`**: The root directory of the Logseq graph.
- **`destination_path`**: The root directory where the Obsidian vault will be created.
- **`pages`**: A list of all `Page` objects in the graph.
- **`journals`**: A list of all `Journal` objects in the graph.
- **`assets`**: A list of all `Asset` objects (e.g., images) to be copied.

## Semantic Models

These models represent specific types of content extracted from blocks during processing.

### `LinkItem`
Represents a formatted link, typically extracted from sections like "Links".
- **`caption`**: The display text of the link.
- **`url`**: The destination URL.
- **`original_content`**: The full original line of the block.
- **`github_url`**: An optional, extracted GitHub URL.
- **`sub_items`**: A list of strings representing indented content under the link.

### `ContentItem`
Represents a generic content item from sections like "Learnings" or "Achievements".
- **`type`**: The type of the content (e.g., 'learning').
- **`description`**: The main text of the item.
- **`sub_items`**: A list of strings representing indented content.
