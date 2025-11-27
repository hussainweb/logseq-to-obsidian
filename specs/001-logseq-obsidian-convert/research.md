# Research: LogSeq to Obsidian Conversion Strategy

## Parsing Strategy for LogSeq Markdown

**Problem**: LogSeq uses an outline-based Markdown flavor where indentation is structural (parent-child relationships). We need to:
1. Extract specific sub-trees (e.g., "Achievements").
2. Transform specific tokens (links, block refs) within lines.
3. Handle block properties (key:: value).

**Options Considered**:

1.  **Standard Markdown Parser (e.g., `markdown-it-py`)**:
    *   *Pros*: Robust standard Markdown support.
    *   *Cons*: LogSeq isn't strictly CommonMark. It treats indentation as block nesting in a way that standard parsers might interpret as code blocks or lists differently. Overkill for simple line transformations.

2.  **Regex-only**:
    *   *Pros*: Fast, easy for simple substitutions (`[[link]]` -> `[[new]]`).
    *   *Cons*: Fragile for structural operations (extracting a tree of bullets). Hard to maintain state (e.g., "am I inside an 'Achievements' block?").

3.  **Custom Indentation-Aware Line Processor (State Machine)**:
    *   *Pros*: Directly models LogSeq's outline structure. Easy to track "current parent" and "indentation level". Efficient for stream processing.
    *   *Cons*: Requires writing custom logic.

**Decision**: **Custom Indentation-Aware Line Processor**.
*   **Rationale**: LogSeq files are fundamentally outlines. We need to preserve this structure or transform it based on hierarchy. A simple reader that tracks indentation level and current context (e.g., "inside Achievements section") is the most robust way to handle the extraction requirements (FR-012, FR-013) and property extraction (FR-011).

## Libraries

*   **Path Handling**: `pathlib` (Standard Lib) - Robust path manipulation.
*   **Frontmatter**: `python-frontmatter` or manual YAML handling. Since we are *creating* frontmatter from properties, manual generation is simple and avoids dependencies.
*   **Testing**: `pytest` (as per Constitution).

## Unknowns Resolved

*   **Parsing**: Custom state machine.
*   **File System**: `pathlib`.
