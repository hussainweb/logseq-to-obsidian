# Feature Specification: Export LogSeq to Tana Intermediate Format

**Feature Branch**: `004-export-logseq-tana`
**Created**: 2025-11-30
**Status**: Draft
**Input**: User description: "I want to export from LogSeq to Tana Intermediate Format file described at https://tana.inc/docs/tana-intermediate-format."

## User Scenarios & Testing *(mandatory)*

## Clarifications

### Session 2025-11-30

- Q: Which approach should be taken for parsing LogSeq markdown? → A: the existing logseq module already has everything you need
- Q: Which LogSeq-specific features, if any, should explicitly be considered out of scope for the initial conversion? → A: Advanced LogSeq queries, templates, and diagram/whiteboard features.
- Q: How should LogSeq block properties (other than `tags`) be handled if they don't have a direct or obvious equivalent in Tana's predefined fields? → A: Ignore them.
- Q: What should be the strategy for error reporting and logging? → A: Detailed error messages always presented to the user, with no separate logging.
- Q: Which specific version of the Tana Intermediate Format should the converter target? → A: The latest stable version available at the time of implementation.

### User Story 1 - Convert LogSeq Vault to Tana Format (Priority: P1)

As a user of both LogSeq and Tana, I want to convert my entire LogSeq vault into the Tana Intermediate Format, so that I can migrate my notes and knowledge base from LogSeq to Tana seamlessly.

**Why this priority**: This is the core functionality of the feature. Without it, the tool has no value.

**Independent Test**: This can be tested by running the converter on a sample LogSeq vault and verifying that the output can be imported into Tana and that the data is consistent.

**Acceptance Scenarios**:

1. **Given** a valid path to a LogSeq vault and a valid path to an empty output directory, **When** the user executes the conversion command, **Then** the output directory is populated with JSON files in the Tana Intermediate Format.
2. **Given** the generated JSON files from a successful conversion, **When** the user imports them into Tana, **Then** the content, structure (including nested blocks), links, and properties from LogSeq are all present and correctly represented in Tana.

---

### Edge Cases

- What happens when the input path is not a valid LogSeq vault? The tool should report a detailed error message to the user and exit.
- What happens when the output directory is not empty? The tool should ask for confirmation before overwriting, and if not confirmed, report a detailed error message to the user and exit.
- How does the system handle LogSeq-specific features that don't have a direct equivalent in the Tana Intermediate Format? The system should report a detailed warning message to the user for any LogSeq features that cannot be mapped to the Tana Intermediate Format. No separate logging will be used.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a command-line interface (CLI) that accepts a source path for the LogSeq vault and a destination path for the output files.
- **FR-002**: The system MUST parse LogSeq's Markdown-based file format, including pages, blocks (lines with bullets), properties (key:: value), and nested block structures (indentation).
- **FR-003**: The system MUST convert the parsed LogSeq content into JSON files that adhere to the latest stable version of the Tana Intermediate Format specification available at the time of implementation.
- **FR-004**: The system MUST map LogSeq's nested blocks to Tana's `children` node structure.
- **FR-005**: The system MUST convert LogSeq's `[[wiki-links]]` and `#tags` into Tana's format for node references.
- **FR-006**: The system MUST generate one JSON file per LogSeq page, with the filename matching the page name.
- **FR-007**: The system MUST use the existing `logseq` module's parser to handle LogSeq markdown.
- **FR-008**: The system will map LogSeq's `tags` property to Tana supertags. Other LogSeq block properties that do not have a direct equivalent in Tana will be ignored.

### Out-of-Scope

The following LogSeq-specific features are explicitly out-of-scope for the initial conversion:
- Advanced LogSeq queries
- Templates
- Diagram/whiteboard features

### Key Entities *(include if feature involves data)*

- **LogSeq Page**: A markdown file in a LogSeq vault, representing a single note.
- **LogSeq Block**: A bullet point (line) within a LogSeq page, which can contain text, links, and properties. Blocks can be nested.
- **Tana Node**: The fundamental object in Tana, which has a name, description, and can have children nodes and fields.
- **Tana Field**: A key-value attribute associated with a Tana Node, analogous to LogSeq properties.
- **Tana SuperTag**: A special attribute in Tana used to define a type of node with a specific structure and set of fields.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The converter can process a LogSeq vault with 1,000 pages and 10,000 blocks with a 100% success rate (no crashes or hangs).
- **SC-002**: The conversion time for a vault of the size mentioned in SC-001 is under 5 minutes.
- **SC-003**: When importing a converted vault into Tana, at least 98% of the structural and semantic information (nested blocks, links, tags, properties) is preserved.
- **SC-004**: The generated Tana Intermediate Format files are 100% compliant with the official Tana specification and can be successfully imported without errors.
