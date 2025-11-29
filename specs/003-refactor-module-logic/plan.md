# Implementation Plan: Refactor Application Modules

**Feature Branch**: `003-refactor-module-logic`
**Feature Spec**: [spec.md](./spec.md)

## Technical Context

This feature is a refactoring of an existing Python CLI application. The goal is to improve the internal module structure for better maintainability and extensibility.

- **Language**: Python
- **Key Technologies**: `uv` for dependency management, `ruff` for linting/formatting, `pytest` for testing.
- **Dependencies**: The project's dependencies are listed in `pyproject.toml`. No new dependencies are required for this refactoring.
- **Integration Points**: The primary integrations are internal, between the application's own modules. The key challenge is to refactor the boundaries between the `logseq` (parsing), `obsidian` (output), and `logseq_converter` (orchestration) modules without changing the external behavior of the CLI tool.

## Constitution Check

The plan fully complies with the project's [constitution.md](../../../.specify/memory/constitution.md).
- **Modern Tooling**: The refactoring will be done within the existing `uv` and `ruff` ecosystem.
- **Testing Discipline**: Success is explicitly defined by the entire `pytest` suite passing, ensuring no regressions are introduced.
- **CLI Standards**: A core requirement is that the CLI contract remains unchanged, adhering to the principle of a predictable interface.

---

## Phase 0: Research

Research confirmed that the planned refactoring aligns with standard Python best practices for creating modular and maintainable applications. The key is to separate concerns (parsing, business logic, output generation) into distinct packages.

- **Artifact**: [research.md](./research.md)

---

## Phase 1: Design & Contracts

The design centers on formalizing the data structures that flow between the refactored modules and ensuring the external contract (the CLI) remains stable.

- **Data Model**: The data model consists of the Pydantic classes that represent Logseq content (Pages, Blocks, etc.). These objects will be the primary data carriers between the `logseq` parsing module and the `obsidian` output module.
  - **Artifact**: [data-model.md](./data-model.md)

- **Contracts**: The primary contract is the CLI itself. The refactoring must not introduce any breaking changes to the command-line arguments, options, or output.
  - **Artifact**: [contracts/cli-contract.md](./contracts/cli-contract.md)

- **Quickstart**: The verification plan is documented in the quickstart guide. It relies on running the automated test suite and performing a `diff` on the output of the tool before and after the changes.
  - **Artifact**: [quickstart.md](./quickstart.md)

---

## Phase 2: Implementation (High-Level)

The implementation will proceed as follows:
1.  Move the statistics calculation logic from the `obsidian` module to the `logseq_converter` module.
2.  Move all Logseq-specific parsing logic from the `obsidian` module to the `logseq` module.
3.  Update import statements across the application to reflect the new locations of the moved logic.
4.  Ensure the `obsidian` module is left with only the responsibility of converting the `logseq` data models into Markdown files.
5.  Run all tests continuously to ensure no regressions are introduced during the process.

This plan sets the stage for the implementation. The next step is to break this down into specific tasks.
