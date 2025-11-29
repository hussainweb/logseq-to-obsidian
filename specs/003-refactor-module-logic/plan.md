# Implementation Plan: Refactor Application Modules (v2)

**Feature Branch**: `003-refactor-module-logic`
**Feature Spec**: [spec.md](./spec.md) (Clarified)

## Technical Context

This feature is a refactoring of an existing Python CLI application. The goal is to improve the internal module structure for better maintainability and extensibility. The specification was clarified to include a new `cleaned_content` field in the data model, which will be populated by the `logseq` parsing module.

- **Language**: Python
- **Key Technologies**: `uv` for dependency management, `ruff` for linting/formatting, `pytest` for testing.
- **Data Flow**: The plan is to implement a clear data pipeline: `raw files` -> `parsing/cleaning module (logseq)` -> `clean data models` -> `output generation module (obsidian)`.

## Constitution Check

The plan fully complies with the project's [constitution.md](../../../.specify/memory/constitution.md).
- **Modern Tooling**: All work will be done within the existing `uv` and `ruff` ecosystem.
- **Testing Discipline**: Success is defined by the entire `pytest` suite passing. Tests will be added to validate the population of the new `cleaned_content` field.
- **CLI Standards**: The CLI contract remains unchanged, ensuring a predictable interface.

---

## Phase 0: Research

Research confirmed that a staged data transformation pipeline is the best practice for this type of application, as it promotes separation of concerns and modularity.

- **Artifact**: [research.md](./research.md) (Updated)

---

## Phase 1: Design & Contracts

The design is centered on the clarified data models and the stable CLI contract.

- **Data Model**: The data model now officially includes the `cleaned_content` field in `Block` and `Page` objects. This field is populated by the `logseq` module.
  - **Artifact**: [data-model.md](./data-model.md)

- **Contracts**: The external CLI contract remains unchanged. The internal contract between modules is now stronger, as the `obsidian` module can expect to receive data models that are already cleaned.
  - **Artifact**: [contracts/cli-contract.md](./contracts/cli-contract.md)

- **Quickstart**: The verification plan remains the same: run automated tests and perform a `diff` on the output.
  - **Artifact**: [quickstart.md](./quickstart.md)

---

## Phase 2: Implementation (High-Level)

The implementation will proceed as follows:
1.  **Data Model Update**: Add the `cleaned_content: str` field to the `Block` and `Page` dataclasses in `src/logseq_converter/logseq/models.py`.
2.  **Parser Enhancement**: Modify the `logseq` parsing logic to strip Logseq-specific properties from the raw content and populate the new `cleaned_content` field.
3.  **Logic Migration**:
    -   Move the statistics calculation logic from the `obsidian` module to the `logseq_converter` module.
    -   Move any remaining content parsing/transformation logic from the `obsidian` module to the `logseq` module.
4.  **Output Module Refactoring**: Update the `obsidian` module to read from the `cleaned_content` field instead of the raw `content` field for its conversion process.
5.  **Test Updates**:
    -   Create new unit tests to verify that the `cleaned_content` field is populated correctly.
    -   Ensure all existing tests pass after the refactoring.

This plan sets the stage for the implementation. The next step is to break this down into specific tasks.
