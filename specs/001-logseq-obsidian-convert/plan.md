# Implementation Plan: LogSeq to Obsidian Converter

**Branch**: `001-logseq-obsidian-convert` | **Date**: 2025-11-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/Users/hw/work/personal/logseq-to-obsidian/specs/001-logseq-obsidian-convert/spec.md`

## Summary

This plan outlines the technical approach for building a CLI application that converts a LogSeq graph into an Obsidian vault. The tool will parse Markdown files, transform LogSeq-specific syntax (block references, properties, date links), and restructure the directory layout to be compatible with Obsidian. The core of the conversion will be handled by a robust Markdown parsing library capable of AST manipulation.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: uv, ruff, pytest, mistletoe
**Storage**: Local file system
**Testing**: pytest
**Target Platform**: macOS, Linux
**Project Type**: CLI application

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **Modern Python Tooling**: Uses `uv` for dependencies and `ruff` for linting/formatting?
- [X] **Testing Discipline**: Uses `pytest` with independent tests?
- [X] **CLI Standards**: Adheres to exit code and output stream standards?

**Result**: All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/001-logseq-obsidian-convert/
├── plan.md              # This file
├── research.md          # Research on parsing libraries and CLI best practices
├── data-model.md        # Key entities and their relationships
├── quickstart.md        # Installation and usage guide
├── contracts/           # Not applicable for this CLI tool
└── tasks.md             # To be created by /speckit.tasks
```

### Source Code (repository root)

The project follows the standard single-project structure.

```text
src/logseq_converter/        # Renamed from logseq_to_obsidian
    ├── __init__.py
    ├── cli.py               # Main entry point, dispatches to the correct converter
    ├── utils.py             # Common utility functions
    ├── logseq/              # Shared LogSeq parser and data models
    │   ├── __init__.py
    │   ├── models.py
    │   └── parser.py
    └── obsidian/            # Obsidian-specific conversion logic
        ├── __init__.py
        └── converter.py

tests/
├── integration/         # End-to-end tests with sample vaults
└── unit/                # Unit tests for individual functions and classes
```

**Structure Decision**: The project has been restructured into a single, scalable package (`logseq_converter`) that can accommodate multiple converters. The shared LogSeq parsing logic is separated from the target-specific (Obsidian) conversion logic. Source code is in `src/logseq_converter`, and tests are in `tests/`.

## Complexity Tracking

> No violations of the constitution were identified. This section is not needed.
