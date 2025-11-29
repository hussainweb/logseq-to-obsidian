# Feature Specification: LogSeq to Tana Importer

**Feature Branch**: `004-tana-importer`  
**Created**: 2025-11-29  
**Status**: Draft  
**Input**: User description: "Use the Tana Input API to import from LogSeq to Tana. Same principles apply as LogSeq to Obsidian but Tana specific features should be used instead of directories and files. Tags in LogSeq should become supertags in Tana with properties set on the supertag where relevant."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Migrate Existing LogSeq Graph to Tana (Priority: P1)

As a Tana user with an existing LogSeq graph, I want to automatically import all my notes, tags, and properties into my Tana workspace. This allows me to seamlessly transition my knowledge base without losing structure or context through manual copy-pasting.

**Why this priority**: This is the core functionality of the feature. Without it, no value is delivered.

**Independent Test**: The feature can be tested by providing a sample LogSeq graph and a Tana API key. The test passes if the content appears in the specified Tana workspace, correctly structured as nodes and supertags.

**Acceptance Scenarios**:

1. **Given** a user has a LogSeq graph directory and a valid Tana API key, **When** they run the importer tool, **Then** their LogSeq pages and blocks are converted into Tana nodes.
2. **Given** a LogSeq block is tagged with `#project`, **When** the import is run, **Then** a `project` supertag is created in Tana and applied to the corresponding node.
3. **Given** a LogSeq block has a property `status:: complete`, **When** the import is run, **Then** the corresponding Tana node has a field named `status` with the value `complete`.

### Edge Cases

- **Invalid Input**: What happens if the provided directory is not a valid LogSeq graph? The system should report a clear error and exit.
- **API Errors**: How does the system handle Tana API rate limiting, network failures, or authentication errors? The system should provide clear feedback and, if possible, allow for resuming the import.
- **Content Duplication**: What happens if the user runs the importer twice on the same graph? The system should ideally avoid creating duplicate content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a local file path to a LogSeq graph directory as input.
- **FR-002**: The system MUST authenticate with the user's Tana workspace using an API key.
- **FR-003**: The system MUST convert LogSeq pages and their block content into a hierarchy of Tana nodes.
- **FR-004**: The system MUST map LogSeq tags (e.g., `#mytag`) to Tana supertags.
- **FR-005**: The system MUST map LogSeq block properties (e.g., `key:: value`) to fields within the corresponding Tana supertag.
- **FR-006**: The system MUST use the Tana Input API to create all content within Tana (documented REST API).
- **FR-007**: The importer MUST be executable as a command-line tool.

### Key Entities

- **LogSeq Graph**: A collection of markdown files representing pages and journals.
- **LogSeq Block**: A unit of content in LogSeq, which can be a paragraph, a list item, etc.
- **LogSeq Tag**: A label used to categorize blocks (e.g., `#idea`).
- **LogSeq Property**: A key-value pair on a block (e.g., `due:: 2025-12-01`).
- **Tana Node**: The fundamental unit of content in Tana.
- **Tana Supertag**: A template applied to Tana nodes, which defines a type and its associated fields.
- **Tana Field**: A property of a supertag (e.g., a "Due Date" field on a "Task" supertag).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A LogSeq graph containing 1,000 pages and 10,000 blocks can be fully imported in under 10 minutes.
- **SC-002**: 99% of LogSeq content, including text, links, and code blocks, is preserved in the corresponding Tana nodes.
- **SC-003**: All LogSeq tags and properties are correctly converted and associated with the correct Tana nodes and supertags, with no data loss.
- **SC-004**: The tool can be successfully run by a non-developer user following a standard `README.md` guide.
