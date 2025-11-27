# Data Model

## Entities

### Graph
Represents the entire LogSeq knowledge base.
- **Path**: `pathlib.Path` (Source directory)
- **Pages**: List[`Page`]
- **Journals**: List[`Journal`]
- **Assets**: List[`pathlib.Path`]

### Page
Represents a single Markdown file (Note).
- **Path**: `pathlib.Path` (Relative to vault root)
- **Parent**: `Page` (Parent folder)
- **Title**: `str` (Derived from filename)
- **Blocks**: List[`Block`]
- **Frontmatter**: `dict` (Extracted properties)
- **Type**: Enum(`Standard`, `Journal`)

### Journal (inherits Page)
Represents a daily note.
- **Date**: `datetime.date` (Derived from filename YYYY_MM_DD)

### Block
Represents a single unit of content (paragraph, bullet).
- **ID**: `str` (Optional UUID)
- **Content**: `str` (Markdown text)
- **Properties**: `dict` (Key-value pairs)
- **Children**: List[`Block`] (Nested blocks)
- **IndentLevel**: `int` (0-based)

## Transformations

### Path Transformation Rules
- **Journals**: `journals/YYYY_MM_DD.md` -> `Daily/YYYY-MM-DD.md`
- **Pages (Root)**: `pages/PageName.md` -> `PageName.md`
- **Pages (Namespaced)**: `pages/Category___Topic.md` -> `Category/Topic.md`
- **Assets**: `assets/*` -> `assets/*` (Copied as-is)

### Link Rewriting
- **Internal Link**: `[[Page Name]]` -> `[[Page Name]]` (Obsidian handles unique filenames at root) or `[[Category/Topic]]` if nested.
- **Journal Link**: `[[15 Nov 2025]]` -> `[[Daily/2025-11-15]]`
- **Block Ref**: `((uuid))` -> `[[Page#^blockid]]`

### Property Extraction
- **Block Properties**: `key:: value` -> Moved to Page Frontmatter if at top level, or kept as text if needed (Spec says "System MUST convert LogSeq properties ... to YAML frontmatter at the top of the file").
    - *Clarification*: LogSeq allows properties on *any* block. Obsidian properties (YAML) are file-level.
    - *Decision*: Only top-level page properties (first block) are moved to Frontmatter. Block-level properties on child blocks might need to be kept as text or converted to Obsidian inline fields (`[key:: value]`). The spec FR-011 says "System MUST convert LogSeq properties ... to YAML frontmatter". It implies page properties. I will assume page properties for now.

## Validation Rules

- **Destination Empty**: Destination directory must not contain files (except `.git` maybe? Spec says "empty").
- **Unique Filenames**: Extracted sections must handle collisions.
