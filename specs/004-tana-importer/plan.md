# Implementation Plan: LogSeq to Tana Importer

**Branch**: `004-tana-importer` | **Date**: 2025-11-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-tana-importer/spec.md`

## Summary

This plan outlines the implementation of a new CLI subcommand to import a LogSeq graph into a Tana workspace. The tool will parse LogSeq files, transform them into a format compatible with the Tana Input API, and send the data to Tana. The core technical approach involves reading local files, mapping LogSeq's structure to Tana's, and making batched, throttled HTTP requests to the Tana REST API. The API key will be managed via an environment variable.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: uv, ruff, pytest, typer, requests
**Storage**: The tool reads from local LogSeq files and writes directly to the Tana API. No intermediate storage is planned.
**Testing**: pytest
**Target Platform**: macOS, Linux
**Project Type**: CLI application

**Key Technical Decisions**:
- **CLI Framework**: The new functionality will be added as a subcommand to the existing `typer` application in `src/logseq_converter/cli.py`.
- **API Interaction**: The `requests` library will be used for all HTTP communication with the Tana API.
- **Authentication**: The Tana API key will be read from a `TANA_API_KEY` environment variable. The tool will exit with an error if it's not set.
- **API Client**: A dedicated `tana_client.py` module will be created to encapsulate all logic for interacting with the Tana API, including authentication, batching, and throttling.
- **Unknowns**:
    - The Tana API documentation does not specify how to retrieve the `nodeID` of a supertag or field immediately after creation. This is critical for applying a newly created supertag to a content node in a subsequent step. **[NEEDS CLARIFICATION]** We will assume for now that creating schema elements and content nodes must be two separate user-initiated steps, but this needs to be confirmed.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **Modern Python Tooling**: Uses `uv` for dependencies and `ruff` for linting/formatting?
- [X] **Testing Discipline**: Uses `pytest` with independent tests?
- [X] **CLI Standards**: Adheres to exit code and output stream standards?

## Project Structure

### Documentation (this feature)

```text
specs/004-tana-importer/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli-contract.md
└── tasks.md             # NOT created by this command
```

### Source Code (repository root)

The existing source code structure will be extended.

```text
src/logseq_converter/
├── cli.py               # MODIFIED: Add 'tana' subcommand
├── tana/                # NEW: Module for Tana-specific logic
│   ├── __init__.py
│   ├── client.py        # Handles Tana API communication
│   ├── converter.py     # Main conversion logic from LogSeq to Tana format
│   └── models.py        # Pydantic models for Tana API objects
└── ... (existing modules)

tests/
├── integration/
│   └── test_tana_conversion.py # NEW: Full integration test
└── unit/
    └── tana/                   # NEW: Unit tests for the Tana module
        ├── test_client.py
        └── test_converter.py
```

**Structure Decision**: The feature will be implemented by extending the existing `logseq_converter` module. A new `tana` sub-package will be created to encapsulate all Tana-related logic, mirroring the existing structure for the Obsidian converter. This maintains a clear separation of concerns within the application.

## Complexity Tracking

No violations of the constitution are anticipated.
