---
description: "Task list for LogSeq to Obsidian Converter implementation"
---

# Tasks: LogSeq to Obsidian Converter

**Input**: Design documents from `/specs/001-logseq-obsidian-convert/`
**Prerequisites**: plan.md, spec.md, data-model.md, quickstart.md

**Tests**: Tests are OPTIONAL and not explicitly requested in the spec, but basic unit tests are good practice.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure: `src/logseq_to_obsidian`, `tests/unit`, `tests/integration`
- [x] T002 Initialize Python project with `uv init`
- [x] T003 [P] Add dev dependencies: `uv add --dev ruff pytest`
- [x] T004 [P] Configure `pyproject.toml` for `ruff` and `pytest`
- [x] T005 [P] Create `src/logseq_to_obsidian/__init__.py` and empty `cli.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create `src/logseq_to_obsidian/models.py` with `Page`, `Block`, `Journal` dataclasses
- [x] T007 Create `src/logseq_to_obsidian/utils.py` with path normalization helpers
- [x] T008 Create `src/logseq_to_obsidian/parser.py` with basic file reading functions
- [x] T009 Setup logging configuration in `src/logseq_to_obsidian/cli.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Full Vault Conversion (Priority: P1) 🎯 MVP

**Goal**: Convert entire LogSeq vault to Obsidian vault (directory structure, file copying, basic renaming).

**Independent Test**: Run tool on sample vault, verify output directory structure and file existence in Obsidian.

### Implementation for User Story 1

- [x] T010 [P] [US1] Implement `Vault` class in `src/logseq_to_obsidian/models.py` to scan source directory
- [x] T011 [US1] Implement `Converter` class in `src/logseq_to_obsidian/converter.py` with initialization
- [x] T012 [US1] Implement `copy_assets` method in `src/logseq_to_obsidian/converter.py`
- [x] T013 [US1] Implement `create_structure` method in `src/logseq_to_obsidian/converter.py` (Daily, pages folders)
- [x] T014 [US1] Implement `process_file` method in `src/logseq_to_obsidian/converter.py` (basic copy/rename)
- [x] T015 [US1] Implement `convert` command in `src/logseq_to_obsidian/cli.py` to trigger `Converter`
- [x] T026 [US1] Validate LogSeq directory structure (pages/journals) in `src/logseq_to_obsidian/cli.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Link and Property Transformation (Priority: P1)

**Goal**: Transform links, block refs, and properties to work in Obsidian.

**Independent Test**: Verify links work and properties appear in frontmatter in Obsidian.

### Implementation for User Story 2

- [ ] T016 [P] [US2] Implement `transform_links` function in `src/logseq_to_obsidian/converter.py` (regex for `[[...]]`)
- [ ] T017 [P] [US2] Implement `transform_block_refs` function in `src/logseq_to_obsidian/converter.py` (regex for `((...))`)
- [ ] T018 [P] [US2] Implement `extract_properties` function in `src/logseq_to_obsidian/parser.py` (frontmatter handling)
- [ ] T019 [US2] Update `process_file` in `src/logseq_to_obsidian/converter.py` to apply transformations

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Journal Section Extraction (Priority: P2)

**Goal**: Extract specific journal sections (Achievements, Highlights, etc.) to separate files.

**Independent Test**: Verify extracted files exist in correct folders and contain correct content.

### Implementation for User Story 3

- [ ] T020 [P] [US3] Implement `parse_blocks` in `src/logseq_to_obsidian/parser.py` to identify sections
- [ ] T021 [US3] Implement `extract_sections` method in `src/logseq_to_obsidian/converter.py`
- [ ] T022 [US3] Implement `get_unique_filename` in `src/logseq_to_obsidian/utils.py`
- [ ] T023 [US3] Update `process_file` in `src/logseq_to_obsidian/converter.py` to call extraction logic

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T024 [P] Run `ruff format` and `ruff check` on all files
- [ ] T025 Run full manual verification on sample vault

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup
- **User Stories (Phase 3+)**: Depend on Foundational
- **Polish (Phase 6)**: Depends on User Stories

### User Story Dependencies

- **US1**: Independent
- **US2**: Independent of US3, extends US1
- **US3**: Independent of US2, extends US1

### Parallel Opportunities

- Setup tasks T003, T004, T005
- Foundational tasks T006, T007, T008
- US1 tasks T010
- US2 tasks T016, T017, T018
- US3 tasks T020, T022

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 & 2
2. Complete Phase 3 (US1)
3. Validate basic conversion (files exist)

### Incremental Delivery

1. Add US2 (Links/Properties) -> Validate links work
2. Add US3 (Extraction) -> Validate extracted files
