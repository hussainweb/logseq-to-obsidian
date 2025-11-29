# Tasks: LogSeq to Tana Importer

**Input**: Design documents from `/specs/004-tana-importer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for the new `tana` module.

- [X] T001 Create the directory structure outlined in `plan.md`: `src/logseq_converter/tana/` and `tests/unit/tana/`.
- [X] T002 [P] Create empty file `src/logseq_converter/tana/__init__.py`.
- [X] T003 [P] Create empty file `src/logseq_converter/tana/models.py`.
- [X] T004 [P] Create empty file `src/logseq_converter/tana/client.py`.
- [X] T005 [P] Create empty file `src/logseq_converter/tana/converter.py`.
- [X] T006 [P] Create empty file `tests/unit/tana/__init__.py`.
- [X] T007 [P] Create empty file `tests/unit/tana/test_client.py`.
- [X] T008 [P] Create empty file `tests/unit/tana/test_converter.py`.
- [X] T009 [P] Create empty file `tests/integration/test_tana_conversion.py`.
- [X] T010 Add `requests` dependency to `pyproject.toml` using `uv add requests`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and client structure that must be complete before the main logic can be implemented.

- [X] T011 [US1] Implement Pydantic models (`TanaNode`, `TanaSupertagRef`, `TanaField`, `TanaAPIPayload`) in `src/logseq_converter/tana/models.py` as defined in `data-model.md`.
- [X] T012 [US1] Implement the basic structure for the Tana API client in `src/logseq_converter/tana/client.py`. This includes creating a `TanaClient` class that reads the `TANA_API_KEY` environment variable in its constructor.

---

## Phase 3: User Story 1 - Migrate Existing LogSeq Graph to Tana 🎯 MVP

**Goal**: Automatically import all notes, tags, and properties from a LogSeq graph into a Tana workspace.

**Independent Test**: Provide a sample LogSeq graph and a Tana API key. The test passes if the content appears in the specified Tana workspace, correctly structured.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Write unit tests for the Tana data models in `src/logseq_converter/tana/models.py` to ensure validation works as expected.
- [X] T014 [P] [US1] Write failing unit tests in `tests/unit/tana/test_client.py` for the Tana client's core functions (authentication, batching, sending requests). Use `requests-mock`.
- [X] T015 [P] [US1] Write failing unit tests in `tests/unit/tana/test_converter.py` for the main conversion logic, mocking the `TanaClient`.

### Implementation for User Story 1

- [X] T016 [US1] Implement the core API request logic in `src/logseq_converter/tana/client.py`. This method should handle making a `POST` request, setting the `Authorization` header, and respecting the 1-second delay. (Depends on T012)
- [X] T017 [US1] Implement node batching logic in `src/logseq_converter/tana/client.py` to handle the 100-node limit per API call. (Depends on T016)
- [X] T018 [US1] Implement the main conversion logic in `src/logseq_converter/tana/converter.py`. This function should transform LogSeq `Block` objects into `TanaNode` data structures. (Depends on T011)
- [X] T019 [US1] Implement the main CLI command in `src/logseq_converter/cli.py`. Add the `tana` subcommand, which should initialize the `TanaClient` and the `TanaConverter` and orchestrate the import process.
- [X] T020 [US1] Integrate the converter and client in `src/logseq_converter/cli.py`. The CLI command should call the converter, which in turn uses the client to send the batched nodes to Tana. (Depends on T017, T018, T019)

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and overall usability.

- [X] T021 [P] Implement comprehensive error handling in `src/logseq_converter/tana/client.py` to manage API errors (e.g., 429 Rate Limit, 401 Unauthorized) and network issues.
- [X] T022 [P] Add logging throughout the `tana` module to provide progress updates and diagnostic information to the user via `stderr`.
- [X] T023 Write the integration test in `tests/integration/test_tana_conversion.py` that runs the full process against a mocked Tana API.
- [X] T024 [P] Update the project's main `README.md` to include documentation for the new `tana` subcommand, referencing the `quickstart.md`.
- [X] T025 [P] Manually validate the end-to-end flow by running the command as described in `quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion.
- **User Story 1 (Phase 3)**: Depends on Foundational completion.
- **Polish (Phase 4)**: Depends on User Story 1 completion.

### Task Dependencies (Key Chains)
- **Models**: `T011` -> `T013` (tests), `T018` (converter)
- **Client**: `T012` -> `T014` (tests) -> `T016` (core logic) -> `T017` (batching) -> `T021` (error handling)
- **Converter**: `T018` (depends on `T011`) -> `T015` (tests)
- **CLI**: `T019` -> `T020` (integration)

### Parallel Opportunities
- Most setup tasks (T002-T009) can be run in parallel.
- Foundational tasks can begin once the file structure is in place.
- The tests in Phase 3 (T013, T014, T015) can be developed in parallel before the implementation begins.
- Polish tasks (T021, T022, T024) can largely be done in parallel.

---

## Implementation Strategy

### MVP First (User Story 1)
The entire feature is contained within a single user story, making it the MVP.

1.  Complete Phase 1: Setup.
2.  Complete Phase 2: Foundational.
3.  Write the failing tests in Phase 3.
4.  Implement the logic in Phase 3 until all tests pass.
5.  Complete the Polish phase to ensure the feature is robust and documented.
6.  Validate the final result using the `quickstart.md` guide.
