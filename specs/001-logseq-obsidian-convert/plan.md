# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements a CLI tool to convert LogSeq vaults to Obsidian vaults. It handles directory restructuring (journals to Daily, pages to root/nested folders), file content transformation (links, block refs, properties), and extraction of specific journal sections. The approach uses a custom indentation-aware parser to handle LogSeq's outline structure reliably.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: uv, ruff, pytest
**Storage**: Local Filesystem
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
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── logseq_to_obsidian/
│   ├── __init__.py
│   ├── cli.py           # Entry point
│   ├── converter.py     # Main conversion logic
│   ├── parser.py        # Indentation-aware parser
│   ├── models.py        # Data classes (Vault, Page, Block)
│   └── utils.py         # Path and string helpers
└── pyproject.toml

tests/
├── conftest.py
├── unit/
│   ├── test_parser.py
│   └── test_converter.py
└── integration/
    └── test_cli.py
```

**Structure Decision**: Standard Python CLI project structure using `src` layout.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

## Verification Plan

### Automated Tests
- **Unit Tests**:
  - `uv run pytest tests/unit/test_parser.py`: Verify indentation parsing and section extraction.
  - `uv run pytest tests/unit/test_converter.py`: Verify link transformation and property extraction.
- **Integration Tests**:
  - `uv run pytest tests/integration/test_cli.py`: Run full conversion on a fixture vault and verify output directory structure and file contents.

### Manual Verification
- **Full Run**:
  1. Create a sample LogSeq vault with:
     - A journal page with "Achievements" section.
     - A page with block refs and properties.
  2. Run `uv run logseq-to-obsidian convert ./sample-in ./sample-out`.
  3. Open `./sample-out` in Obsidian.
  4. Verify "Achievements" folder exists and contains extracted bullets.
  5. Verify links work.
