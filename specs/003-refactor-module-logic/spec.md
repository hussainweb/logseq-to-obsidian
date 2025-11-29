# Feature Specification: Refactor Application Modules

**Feature Branch**: `003-refactor-module-logic`  
**Created**: 2025-11-29
**Status**: Draft  
**Input**: User description: "I want to refactor the app to move functionality at proper places. These are the things I see which are in the wrong place: - statistics calculator is in the obsidian module. The statistics functionality is regardless of writing to Obsidian or another destination. It should be in the main module logseq_converter. - Some of the logic for parsing the sections for links, learnings, etc, is in the obsidian module. That module should only be concerned with writing the content to markdown files. The actual parsing logic and models should be in the logseq module."

## User Scenarios & Testing *(mandatory)*

This feature is a code refactoring initiative. The "user" is a developer working on the codebase. The goal is to improve code structure, maintainability, and extensibility.

### User Story 1 - Simplified Maintenance (Priority: P1)

As a developer, I want the code to be organized logically so that I can find and modify functionality in its expected location, reducing the time it takes to make changes.

**Why this priority**: This is the core goal of the refactoring. A well-organized codebase is cheaper and easier to maintain.

**Independent Test**: This can be verified by code review and by confirming that all post-refactoring code resides in the correct, more logical modules.

**Acceptance Scenarios**:

1. **Given** a developer needs to change the statistics calculation logic, **When** they inspect the codebase, **Then** they find the logic within the main `logseq_converter` module, not the `obsidian` output module.
2. **Given** a developer needs to modify how Logseq blocks are parsed, **When** they inspect the codebase, **Then** they find the parsing logic within the `logseq` module.

---

### User Story 2 - Improved Extensibility (Priority: P2)

As a developer, I want to add a new output format (e.g., for Tana, Roam) without modifying the core Logseq parsing logic, so that extending the application is faster and less error-prone.

**Why this priority**: This demonstrates the practical value of the refactoring. Decoupling parsing from output makes the application more flexible.

**Independent Test**: This can be tested by creating a new, minimal output module. The new module should be able to reuse the parsing logic from the `logseq` module without requiring any changes to it.

**Acceptance Scenarios**:

1. **Given** the refactoring is complete, **When** a developer creates a new output module, **Then** they can import and use the parsers from the `logseq` module to process content without altering the `logseq` module itself.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST move the statistics calculation functionality from the `logseq_converter.obsidian` module to the `logseq_converter` module.
- **FR-002**: The system MUST move the content parsing logic (for links, learnings, etc.) from the `logseq_converter.obsidian` module to the `logseq_converter.logseq` module.
- **FR-003**: The `logseq_converter.obsidian` module MUST only contain logic to convert Logseq model objects into Obsidian-flavored Markdown files and write them to the filesystem.
- **FR-004**: The system MUST ensure that all existing functionality behaves identically to the end-user after the refactoring.
- **FR-005**: All existing automated tests MUST pass after the refactoring is complete.

### Key Entities *(include if feature involves data)*

- **`logseq_converter`**: The main application module, responsible for orchestrating the conversion process and housing shared functionality like statistics.
- **`logseq_converter.logseq`**: The module responsible for parsing Logseq-specific syntax and data structures.
- **`logseq_converter.obsidian`**: The module responsible for converting the parsed data into Obsidian-flavored Markdown files.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of existing unit and integration tests pass after the code is refactored.
- **SC-002**: Code review confirms that statistics-related logic is no longer present in the `logseq_converter.obsidian` module and resides in `logseq_converter`.
- **SC-003**: Code review confirms that Logseq content parsing logic is no longer present in the `logseq_converter.obsidian` module and resides in `logseq_converter.logseq`.
- **SC-004**: The public API or CLI contract of the application remains unchanged and produces the exact same output for a given input.
