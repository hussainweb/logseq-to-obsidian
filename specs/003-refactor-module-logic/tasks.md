# Tasks: Refactor Application Modules

**Feature**: [Refactor Application Modules](./spec.md)

This document breaks down the implementation of the module refactoring into actionable, dependency-ordered tasks.

---

## Phase 1: Setup
- [ ] T001 Verify `uv` is installed and the project environment is active with all dependencies from `pyproject.toml`.

---

## Phase 2: Foundational (Data Model)
- [ ] T002 [US1] Add `cleaned_content: str` field to `Block` and `Page` dataclasses in `src/logseq_converter/logseq/models.py`.
- [ ] T003 [US1] Create a new test file `tests/unit/test_parser_cleaning.py` to specifically test the population of the `cleaned_content` field.
- [ ] T004 [US1] In `tests/unit/test_parser_cleaning.py`, write a test case to verify that a block with Logseq properties has them removed in the `cleaned_content` field.

---

## Phase 3: Implementation (User Story 1)

**User Story**: As a developer, I want the code to be organized logically so that I can find and modify functionality in its expected location.
**Independent Test**: Code review confirms logic is in the correct modules, and all automated tests pass.

- [ ] T005 [US1] Implement the property-stripping logic within the `logseq` parsing module (`src/logseq_converter/logseq/parser.py`) to populate the `cleaned_content` field.
- [ ] T006 [US1] Ensure the test from T004 now passes.
- [ ] T007 [US1] Identify the statistics calculation logic in the `obsidian` module (`src/logseq_converter/obsidian/converter.py`).
- [ ] T008 [US1] Move the statistics calculation logic to a new file `src/logseq_converter/stats.py`.
- [ ] T009 [US1] Update any necessary imports and entry points in `src/logseq_converter/cli.py` to call the statistics logic from its new location.
- [ ] T010 [US1] Identify any remaining content parsing or transformation logic within `src/logseq_converter/obsidian/converter.py`.
- [ ] T011 [US1] Move the identified parsing logic to `src/logseq_converter/logseq/parser.py`.
- [ ] T012 [US1] Refactor the `obsidian` converter (`src/logseq_converter/obsidian/converter.py`) to use the `cleaned_content` field from the data models as its source for writing Markdown files.
- [ ] T013 [US1] Update existing tests in `tests/` that are now broken due to the moved logic, ensuring they point to the new locations of the refactored code.

---

## Phase 4: Polish & Verification
- [ ] T014 Run the entire test suite via `pytest` and ensure 100% of tests pass.
- [ ] T015 Perform a final code review to confirm that the `obsidian` module is free of parsing/statistics logic and that modules have clear responsibilities.
- [ ] T016 Manually verify the refactoring by running the tool on a sample graph and `diff`-ing the output against a known-good version, as described in `quickstart.md`.

---

## Dependencies & Execution Strategy

- **Implementation Strategy**: The tasks are ordered sequentially as this is a refactoring effort with tight dependencies. A "big bang" approach where all tasks are completed on the feature branch before merging is required.
- **MVP Scope**: The entire set of tasks constitutes the MVP. The refactoring is not considered complete until all tasks are done and all tests pass.
- **Task Dependencies**:
  - `T002` must be complete before `T005`.
  - `T005` must be complete before `T012`.
  - `T008` and `T011` must be complete before `T015`.

### Parallel Execution Opportunities

Due to the nature of this refactoring, most tasks are sequential. However, some minor parallelization is possible:
- **Story 1**:
  - `T003` and `T004` (writing tests) can be done in parallel with `T002` (updating the model).
  - `T008` (moving stats) and `T011` (moving parsing logic) could potentially be worked on in parallel after the initial model changes are complete.
