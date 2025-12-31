# Implementation Plan: Export LogSeq to Tana Intermediate Format

**Branch**: `004-export-logseq-tana` | **Date**: 2025-11-30 | **Spec**: /specs/004-export-logseq-tana/spec.md
**Input**: Feature specification from `/specs/004-export-logseq-tana/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The core functionality of this feature is to convert an entire LogSeq vault into the Tana Intermediate Format. The technical approach involves leveraging the existing `logseq` module for parsing LogSeq Markdown. The conversion will target the latest stable version of the Tana Intermediate Format. Specific LogSeq features such as advanced queries, templates, and diagram/whiteboard features will be considered out of scope. Additionally, LogSeq block properties other than `tags` will be ignored during conversion. Error reporting will involve detailed messages presented directly to the user, with no separate logging.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: uv, ruff, pytest
**Storage**: files
**Testing**: pytest
**Target Platform**: macOS, Linux
**Project Type**: CLI application

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Modern Python Tooling**: Uses `uv` for dependencies and `ruff` for linting/formatting?
- [x] **Testing Discipline**: Uses `pytest` with independent tests?
- [x] **CLI Standards**: Adheres to exit code and output stream standards?

## Project Structure

### Documentation (this feature)

```text
specs/004-export-logseq-tana/
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