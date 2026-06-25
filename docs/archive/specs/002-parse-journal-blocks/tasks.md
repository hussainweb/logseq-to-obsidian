---

description: "Task list for feature implementation: Parse Journal Blocks"
---

# Tasks: Parse Journal Blocks

**Input**: Design documents from `/specs/002-parse-journal-blocks/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This plan includes test tasks as part of the development workflow to ensure quality and independent verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Python environment with uv, ruff, pytest (if not already set up)
- [x] T002 Review project structure and ensure `src/logseq_converter/cli.py` is the main entry point
- [x] T003 [P] Create base data models for Journal, Block, Link Item, Content Item in `src/logseq_converter/logseq/models.py`
- [x] T004 Implement CLI command structure for 'parse-journals' in `src/logseq_converter/cli.py` with argument parsing (`logseq-journals-dir`, `obsidian-vault-dir`, `--dry-run`, `--verbose`, `--log-file`)
- [x] T005 [P] Add utility functions for file path handling, date parsing, and basic string manipulation in `src/logseq_converter/utils.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Implement core parsing logic in `src/logseq_converter/logseq/parser.py` to read a journal file and identify blocks
- [x] T007 [P] Add unit tests for data models in `tests/unit/test_models.py`
- [x] T008 [P] Add unit tests for utility functions in `tests/unit/test_utils.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Extract Links from Journals (Priority: P1) 🎯 MVP

**Goal**: Automatically identify and extract link blocks from daily notes, convert each top-level link item into a separate Markdown file in a 'Links' directory with relevant frontmatter, and remove the extracted block from the original journal file.

**Independent Test**: Provide a journal file with a links block and verify the creation of new Markdown files in the 'Links' directory with correct content and frontmatter, and that the original journal file no longer contains the links block.

### Implementation for User Story 1

- [x] T009 [US1] Implement parsing logic for '#links' blocks to extract Link Items (caption, URL, GitHub URL, sub-items) in `src/logseq_converter/logseq/parser.py`
- [x] T010 [US1] Implement conversion logic for Link Items to create new Markdown files with correct filename derivation, content, and frontmatter (url, github_url, date) in `src/logseq_converter/obsidian/converter.py`
- [x] T011 [US1] Implement removal of the extracted '#links' block from the original journal file in `src/logseq_converter/obsidian/converter.py`
- [x] T012 [P] [US1] Add unit tests for '#links' parsing in `tests/unit/test_parser.py`
- [x] T013 [P] [US1] Add unit tests for Link Item conversion in `tests/unit/test_converter.py`
- [x] T014 [US1] Add integration test for end-to-end '#links' extraction and conversion in `tests/integration/test_links_extraction.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Extract Learnings, Achievements, and Highlights from Journals (Priority: P1)

**Goal**: Identify and extract 'learnings', 'achievements', and 'highlights' blocks from daily notes, convert each top-level item into a separate Markdown file in corresponding directories with the journal date in frontmatter, and remove the extracted block from the original journal file.

**Independent Test**: Provide a journal file with 'learnings', 'achievements', and 'highlights' blocks and verify the creation of new Markdown files in the respective directories with correct content and frontmatter, and that the original journal file no longer contains these blocks.

### Implementation for User Story 2

- [x] T015 [US2] Extend parsing logic in `src/logseq_converter/logseq/parser.py` for '#learnings', '#achievements', '#highlights' blocks to extract Content Items (description preview, sub-items)
- [x] T016 [US2] Extend conversion logic in `src/logseq_converter/obsidian/converter.py` for Content Items to create new Markdown files with correct filename derivation, content, and frontmatter (date)
- [x] T017 [US2] Implement removal of '#learnings', '#achievements', '#highlights' blocks from original journal files in `src/logseq_converter/obsidian/converter.py`
- [x] T018 [P] [US2] Add unit tests for '#learnings', '#achievements', '#highlights' parsing in `tests/unit/test_parser.py`
- [x] T019 [P] [US2] Add unit tests for Content Item conversion in `tests/unit/test_converter.py`
- [x] T020 [US2] Add integration test for end-to-end '#learnings', '#achievements', '#highlights' extraction and conversion in `tests/integration/test_content_extraction.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T021 Implement unique filename generation for all created Markdown files (handling duplicates) in `src/logseq_converter/utils.py`
- [x] T022 Refine error handling and logging (console output, optional log file) throughout the application (`src/logseq_converter/cli.py`, `src/logseq_converter/logseq/parser.py`, `src/logseq_converter/obsidian/converter.py`)
- [x] T023 Implement '--dry-run' functionality to prevent file system changes when enabled in `src/logseq_converter/cli.py` and `src/logseq_converter/obsidian/converter.py`
- [x] T024 Implement '--verbose' / '-v' logging functionality in `src/logseq_converter/cli.py`
- [x] T025 Validate CLI arguments (e.g., directories exist and are accessible) in `src/logseq_converter/cli.py`
- [x] T026 Refactor and clean up code for maintainability and adherence to project conventions (ruff check)
- [x] T027 Ensure all tests pass and achieve good code coverage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Add unit tests for '#links' parsing in tests/unit/test_parser.py"
Task: "Add unit tests for Link Item conversion in tests/unit/test_converter.py"

# Launch relevant independent implementation tasks:
Task: "Implement parsing logic for '#links' blocks to extract Link Items (caption, URL, GitHub URL, sub-items) in src/logseq_converter/logseq/parser.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
