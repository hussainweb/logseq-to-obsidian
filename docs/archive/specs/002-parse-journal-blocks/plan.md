# Implementation Plan: Parse Journal Blocks

**Branch**: `002-parse-journal-blocks` | **Date**: 2025-11-28 | **Spec**: specs/002-parse-journal-blocks/spec.md
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement parsing of Logseq daily notes (journals) to extract specific content blocks (links, learnings, achievements, highlights). Each top-level item within these blocks will be converted into a separate Markdown file in a corresponding directory. These new Markdown files will include relevant frontmatter (e.g., URL, GitHub URL for links, and the journal date for all). The original extracted blocks, including their headings, will be removed from the journal files. The system should handle edge cases like empty blocks, duplicate filenames (by ensuring uniqueness), and gracefully process journal files without target blocks.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: uv, ruff, pytest, mistletoe (as identified in GEMINI.md for 001-logseq-obsidian-convert)
**Storage**: Markdown files
**Testing**: pytest
**Target Platform**: macOS, Linux (standard Python environment)
**Project Type**: CLI application
**Key Libraries**: mistletoe (for Markdown parsing), os, datetime

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Modern Python Tooling**: Uses `uv` for dependencies and `ruff` for linting/formatting?
- [x] **Testing Discipline**: Uses `pytest` with independent tests?
- [x] **CLI Standards**: Adheres to exit code and output stream standards?

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

src/
├── logseq_converter/
│   ├── __init__.py
│   ├── cli.py             # Main CLI entry point
│   ├── utils.py           # General utility functions
│   ├── logseq/            # Logseq related modules
│   │   ├── __init__.py
│   │   ├── models.py      # Data models for Logseq entities
│   │   └── parser.py      # Logseq parsing logic
│   └── obsidian/          # Obsidian related modules
│       ├── __init__.py
│       └── converter.py   # Conversion logic to Obsidian format

tests/
├── integration/
└── unit/

**Structure Decision**: The project uses a single-project structure with `src/logseq_converter` as the main package. This aligns with a standard Python CLI application structure, separating concerns into `logseq` and `obsidian` sub-packages, and a `cli` module for the entry point. This decision is based on the existing project layout.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |