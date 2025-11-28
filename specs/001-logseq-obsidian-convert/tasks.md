# Tasks: LogSeq to Obsidian Converter

**Input**: Design documents from `/specs/001-logseq-obsidian-convert/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

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

- [X] T001 Create project root directory `src/logseq_converter`
- [X] T002 Create subdirectories `src/logseq_converter/logseq`, `src/logseq_converter/obsidian`
- [X] T003 Create `__init__.py` files in `src/logseq_converter`, `src/logseq_converter/logseq`, `src/logseq_converter/obsidian`
- [X] T004 Create `src/logseq_converter/cli.py` for CLI entry point
- [X] T005 Create `src/logseq_converter/utils.py` for common utilities
- [X] T006 Create `src/logseq_converter/logseq/models.py` for LogSeq data models
- [X] T007 Create `src/logseq_converter/logseq/parser.py` for LogSeq parsing logic
- [X] T008 Create `src/logseq_converter/obsidian/converter.py` for Obsidian-specific conversion logic
- [X] T009 Create `tests/integration` and `tests/unit` directories
- [X] T010 Initialize Python project with `uv init` in `pyproject.toml`
- [X] T011 [P] Add dev dependencies: `uv add --dev ruff pytest` to `pyproject.toml`
- [X] T012 [P] Configure `pyproject.toml` for `ruff` and `pytest`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T013 Implement CLI argument parsing in `src/logseq_converter/cli.py` (FR-001)
- [X] T014 Implement output directory validation (empty check) in `src/logseq_converter/utils.py` (FR-002)
- [X] T015 Implement assets copying logic in `src/logseq_converter/utils.py` (FR-003, FR-004)
- [X] T016 Implement a progress indicator in `src/logseq_converter/utils.py` (FR-015)
- [X] T017 Implement a generic logging and warning mechanism in `src/logseq_converter/utils.py` (Edge Cases)
- [X] T018 Define base `Block`, `Page`, `Journal`, `Graph` models in `src/logseq_converter/logseq/models.py` (data-model.md)
- [X] T019 Implement the initial Markdown parsing setup using `mistletoe` in `src/logseq_converter/logseq/parser.py` (Research)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Full Graph Conversion (Priority: P1) 🎯 MVP

**Goal**: Convert an entire LogSeq graph to an Obsidian vault with minimal manual effort.

**Independent Test**: Run the tool on a sample LogSeq graph and verify the output directory structure and file contents in Obsidian.

### Implementation for User Story 1

- [X] T020 [US1] Implement journal file transformation (YYYY_MM_DD.md to Daily/YYYY-MM-DD.md) in `src/logseq_converter/obsidian/converter.py` (FR-005)
- [X] T021 [US1] Implement page file transformation (A___B.md to A/B.md) in `src/logseq_converter/obsidian/converter.py` (FR-006)
- [X] T022 [US1] Implement the main conversion orchestration in `src/logseq_converter/cli.py` to process all files in a vault.
- [X] T023 [US1] Add integration tests for full vault conversion in `tests/integration/test_full_vault_conversion.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Link and Property Transformation (Priority: P1)

**Goal**: Ensure links, block references, and properties work correctly in Obsidian.

**Independent Test**: Create a test vault with various link types and properties, run the conversion, and verify they work in Obsidian.

### Implementation for User Story 2

- [X] T024 [US2] Implement a two-pass approach for block references in `src/logseq_converter/logseq/parser.py` (Research)
- [X] T025 [US2] Implement LogSeq block ID (`id:: uuid`) to Obsidian block anchor (`^blockid`) conversion in `src/logseq_converter/obsidian/converter.py` (FR-010)
- [X] T026 [US2] Implement LogSeq block reference (`((uuid))`) to Obsidian internal link (`[[file#^blockid]]`) conversion in `src/logseq_converter/obsidian/converter.py` (FR-009)
- [X] T027 [US2] Implement LogSeq date link (`[[15 Nov 2025]]`) to Obsidian format (`[[Daily/2025-11-15]]`) conversion in `src/logseq_converter/obsidian/converter.py` (FR-008)
- [X] T028 [US2] Implement internal link rewriting to match new file paths and folder structures in `src/logseq_converter/obsidian/converter.py` (FR-007)
- [X] T029 [US2] Implement LogSeq properties (`key:: value`) to YAML frontmatter conversion in `src/logseq_converter/obsidian/converter.py` (FR-011)
- [X] T030 [US2] Handle broken block references/date links (retain original text, log warning) in `src/logseq_converter/obsidian/converter.py` (FR-016)
- [X] T031 [US2] Add unit tests for link and property transformations in `tests/unit/test_link_property_transformation.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Journal Section Extraction (Priority: P2)

**Goal**: Extract specific journal sections to separate files for better organization.

**Independent Test**: Create journal entries with "Achievements", "Highlights", "Learnings", and "Links" sections, run conversion, and check for existence and content of extracted files.

### Implementation for User Story 3

- [X] T032 [US3] Implement logic to identify and extract "Achievements", "Highlights", "Learnings", "Links" sections from journal entries in `src/logseq_converter/obsidian/converter.py` (FR-012)
- [X] T033 [US3] Implement logic to save extracted items as separate files in corresponding directories in `src/logseq_converter/obsidian/converter.py` (FR-012)
- [X] T034 [US3] Implement filename sanitization for extracted items in `src/logseq_converter/utils.py` (FR-013)
- [X] T035 [US3] Implement handling of child blocks and links for extracted items in `src/logseq_converter/obsidian/converter.py`
- [X] T036 [US3] Implement removal of `:LOGBOOK:` entries from tasks in `src/logseq_converter/obsidian/converter.py` (FR-014)
- [X] T037 [US3] Add unit tests for journal section extraction in `tests/unit/test_journal_extraction.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T038 Handle filename collisions (append unique suffix) in `src/logseq_converter/utils.py` (Edge Cases)
- [X] T039 Handle missing source path (report error) in `src/logseq_converter/cli.py` (Edge Cases)
- [X] T040 Handle invalid Markdown (log warnings, continue processing) in `src/logseq_converter/logseq/parser.py` (Edge Cases)
- [X] T041 Handle unsupported features (log warnings, leave original syntax) in `src/logseq_converter/logseq/parser.py` (Edge Cases)
- [ ] T042 Ensure processing of large files in a streaming/chunk-based manner in `src/logseq_converter/logseq/parser.py` (NFR-001)
- [X] T043 Code cleanup and refactoring across the codebase
- [X] T044 Run `quickstart.md` validation, ensuring installation and usage instructions are accurate.

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
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

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
# Launch all tests for User Story 1 together (if tests requested):
Task: "Add integration tests for full graph conversion in tests/integration/test_full_vault_conversion.py"

# Launch all models for User Story 1 together:
Task: "Implement journal file transformation (YYYY_MM_DD.md to Daily/YYYY-MM-DD.md) in src/logseq_converter/obsidian/converter.py"
Task: "Implement page file transformation (A___B.md to A/B.md) in src/logseq_converter/obsidian/converter.py"
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
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
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