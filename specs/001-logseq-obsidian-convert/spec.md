# Feature Specification: LogSeq to Obsidian Converter

**Feature Branch**: `001-logseq-obsidian-convert`
**Created**: 2025-11-27
**Status**: Draft
**Input**: User description: "CLI application to convert a LogSeq graph to Obsidian vault..."

## User Scenarios & Testing

### User Story 1 - Full Graph Conversion (Priority: P1)

As a user, I want to convert my entire LogSeq graph to an Obsidian vault so that I can migrate my notes with minimal manual effort.

**Why this priority**: This is the core functionality of the tool. Without this, the tool provides no value.

**Independent Test**: Can be fully tested by running the tool on a sample LogSeq graph and verifying the output directory structure and file contents in Obsidian.

**Acceptance Scenarios**:

1. **Given** a valid LogSeq graph path and an empty destination path, **When** I run the conversion command, **Then** the destination directory is populated with the converted vault, including `assets`, `Daily` journals, and `pages` folders.
2. **Given** a non-empty destination path, **When** I run the conversion command, **Then** the tool exits with an error message to prevent data loss.
3. **Given** a LogSeq page with `___` in the filename (e.g., `Category___Topic`), **When** converted, **Then** the file is placed in a nested directory structure (e.g., `Category/Topic.md`).

---

### User Story 2 - Link and Property Transformation (Priority: P1)

As a user, I want my links, block references, and properties to work in Obsidian so that my knowledge graph is preserved.

**Why this priority**: A knowledge base relies on connections. Broken links or missing metadata would make the migration a failure.

**Independent Test**: Create a test vault with various link types (block refs, date links) and properties, run the conversion, and verify they work in Obsidian.

**Acceptance Scenarios**:

1. **Given** a page with a block reference `((uuid))`, **When** converted, **Then** the reference is replaced with an Obsidian internal link `[[file#^blockid]]` and the target block has the `^blockid` anchor appended.
2. **Given** a page with a date link `[[15 Nov 2025]]`, **When** converted, **Then** it is transformed to `[[Daily/2025-11-15]]`.
3. **Given** a block with properties `prop:: value`, **When** converted, **Then** these are moved to the YAML frontmatter of the file.

---

### User Story 3 - Journal Section Extraction (Priority: P2)

As a user, I want specific journal sections (Achievements, Highlights, Learnings, Links) extracted to separate files so that I can organize them by topic.

**Why this priority**: This allows for better organization of specific types of content that were previously buried in daily journals.

**Independent Test**: Create journal entries with these sections, run conversion, and check for the existence and content of the extracted files.

**Acceptance Scenarios**:

1. **Given** a journal entry with an "Achievements" section containing bullet points, **When** converted, **Then** each bullet point is saved as a separate file in the `Achievements` directory.
2. **Given** an extracted item with child blocks, **When** converted, **Then** the child blocks are preserved in the body of the new file.
3. **Given** an extracted item with links, **When** converted, **Then** the links are preserved or extracted as properties if applicable (e.g. URL).

### Edge Cases

- **Destination Not Empty**: If the destination directory is not empty, the system MUST abort to prevent data loss.
- **Filename Collisions**: If any file conversion or extraction results in a filename that already exists, the system MUST append a unique suffix (e.g., `filename-1.md`). This applies to case-insensitive collisions (e.g., `Note.md` and `note.md`), which MUST be renamed to avoid data loss (e.g., `note-case-conflict.md`).
- **Missing Source**: If the source path does not exist, the system MUST report an error.
- **Invalid Markdown**: The system should attempt to process files as best as possible, logging warnings and informational messages to the console by default, with an option for increased verbosity, for any files that cannot be parsed.
- **Unsupported Features**: For Logseq features not explicitly supported by the converter (e.g., queries, macros), the system MUST leave the original syntax untouched in the output, log a warning for each instance, and continue processing.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a source directory path, a target format, and an output directory path as CLI arguments (e.g., `convert <source> --to <format> --out <dir>`).
- **FR-002**: System MUST validate that the output directory is empty before proceeding.
- **FR-003**: System MUST copy the `assets` directory from source to destination without modification.
- **FR-004**: System MUST NOT copy the `logseq` configuration directory.
- **FR-005**: System MUST transform journal files (YYYY_MM_DD.md or similar) to `Daily/YYYY-MM-DD.md`.
- **FR-006**: System MUST transform page files with `___` separators into nested directory structures (e.g., `A___B.md` -> `A/B.md`).
- **FR-007**: System MUST rewrite internal links to match the new file paths and folder structures.
- **FR-008**: System MUST rewrite date links to the `Daily/YYYY-MM-DD` format.
- **FR-009**: System MUST convert LogSeq block references (`((uuid))`) to Obsidian block links (`[[file#^blockid]]`).
- **FR-010**: System MUST convert LogSeq block IDs (`id:: uuid`) to Obsidian block anchors (`^blockid`).
- **FR-011**: System MUST convert LogSeq properties (`key:: value`) to YAML frontmatter at the top of the file.
- **FR-012**: System MUST extract content under "Achievements", "Highlights", "Learnings", and "Links" top-level journal bullets into separate files in corresponding directories.
- **FR-013**: System MUST use the bullet text as the filename for extracted items, sanitizing any illegal characters by removing or replacing them with a safe substitute (e.g., hyphen) (handling duplicates by appending a unique suffix if necessary).
- **FR-014**: System MUST remove `:LOGBOOK:` entries and associated timing data from tasks.
- **FR-015**: System MUST display a progress indicator (e.g., spinner or percentage) during conversion, showing the currently processed filename on the same line.
- **FR-016**: System MUST retain original text for broken block references or date links and log a warning for each instance.

### Non-Functional Requirements

- **NFR-001**: System MUST process files in a streaming or chunk-based manner to handle large files efficiently and avoid excessive memory consumption.

## Architectural Constraints

- **AC-001**: The system MUST be designed with a modular architecture that separates the core Logseq parsing logic and data model from the output-specific "writer" logic. This is to support future conversion to other platforms (e.g., Tana, Capacities) with minimal changes to the core.
- **AC-002**: The project structure will reflect this separation, with a general `logseq` library and distinct `writers` for each target format (e.g., a `writers/obsidian` module).

## Architectural Tradeoffs

- **AT-001**: While the architecture mandates separation between parser/model and writers, a formal "Writer" interface (e.g., abstract base class or protocol) will not be defined initially. The implementation will rely on convention. A refactor to introduce a formal interface will occur if additional writers beyond Obsidian are added in the future.

## Compatibility

- **COM-001**: The converter will aim for best-effort compatibility with recent versions of Logseq. It does not guarantee support for specific Logseq versions or future breaking changes to the format.

## Terminology

- **Parse**: The process of reading and interpreting the source Logseq markdown files and converting them into the intermediate data model (Model).
- **Model**: The in-memory, language-agnostic intermediate representation (IR) of the Logseq data structure. This is the output of the Parse step.
- **Write**: The process of taking the intermediate data model (Model) and generating the output files in the specified target format (e.g., Obsidian markdown).

### Key Entities

These entities define the core intermediate representation (IR) of the Logseq data, which will be passed from the parser to a writer.

- **Graph**: The collection of markdown files and assets.
- **Journal**: A daily note file.
- **Page**: A standard note file.
- **Block**: A single paragraph or bullet point in LogSeq, identified by a UUID.
- **Property**: Key-value pair associated with a block or page.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of non-ignored files from the source graph are present in the destination vault (either as-is or transformed).
- **SC-002**: 0% of block references result in broken links in Obsidian (assuming valid refs in source).
- **SC-003**: All "Achievements", "Highlights", "Learnings", and "Links" items are correctly extracted to their respective folders.
- **SC-004**: The conversion process completes for a medium-sized vault (e.g., 1000 files) in under 1 minute.

## Clarifications

### Session 2025-11-28
- Q: How should the project be structured to support the global parser/model and future writers? → A: A core `logseq` library for parsing and data models, with separate `writers` for each target (e.g., `writers/obsidian`).
- Q: How should the CLI command be designed to accommodate future output formats beyond Obsidian? → A: `convert <source> --to <format> --out <dir>`
- Q: Should we define a formal "Writer" interface that takes the intermediate data model as input, ensuring a clean separation between parsing and writing? → A: No, rely on convention for now and refactor if more writers are added.
- Q: To align with the modular architecture, should we standardize on precise terms for the conversion pipeline, such as `Parse` (Logseq text -> model), `Model` (the intermediate representation), and `Write` (model -> target format)? → A: Yes, standardize on these terms.
- Q: How should the converter handle advanced or esoteric Logseq features like block queries ({{query ...}}), macros, or whiteboard files (.excalidraw)? → A: Warn and Bypass: The converter should log a prominent warning, leave the unsupported syntax untouched in the output file, and continue the conversion.
- Q: How should the system handle potential filename collisions, especially on case-insensitive filesystems (e.g., `Note.md` vs `note.md`)? → A: Append Suffix: On collision, append a unique, descriptive suffix to the conflicting filename (e.g., `note-case-conflict-1.md`).
- Q: What level of compatibility should the converter promise regarding Logseq versions? → A: Best-effort compatibility.
- Q: How should duplicate property keys from different blocks in the same file be handled in the YAML frontmatter? → A: Create a YAML list: Aggregate all values for the duplicate key into a list (array) in the frontmatter.

### Session 2025-11-27
- Q: When extracting a journal item, the bullet text is used for the new filename. This text can contain characters that are illegal in filenames (e.g., ?, /, :). How should the system handle illegal characters in generated filenames? → A: The system should sanitize the filename by removing or replacing any illegal characters with a safe substitute (like a hyphen).
- Q: How should the system handle logging output for warnings and informational messages during the conversion process? → A: Log to console by default, with an option to increase verbosity (e.g., -v flag).
- Q: Should the CLI provide a progress indicator during the conversion of a vault (e.g., a spinner, progress bar, or periodic status updates)? → A: Yes, a simple progress indicator (e.g., a spinner or percentage) should be displayed, showing the filename on the same line.
- Q: How should the system handle individual markdown files that are extremely large (e.g., >10MB)? → A: The system should process large files in a streaming or chunk-based manner.
- Q: The spec describes how to convert valid block references (((uuid))) and date links ([[date]]), but it does not specify what to do if a reference is broken (i.e., the target block UUID or date does not exist in the vault). How should the system handle these broken links? → A: Keep the original reference text as-is and log a warning.