# Logseq to Obsidian Constitution

## Core Principles

### I. Modern Python Tooling
**Dependency Management & Code Quality**: The project MUST use `uv` for dependency management and `ruff` for all linting and formatting. `pyproject.toml` is the Single Source of Truth for tool configuration.
- **Rationale**: `uv` provides a unified, fast, and reliable package management experience. `ruff` consolidates multiple linting tools into one high-performance tool, ensuring consistent code style and quality without configuration sprawl.

### II. Testing Discipline
**Independent & Comprehensive Testing**: All features MUST be tested using `pytest`. Tests MUST be independent (no shared state between tests) and deterministic.
- **Rationale**: `pytest` is the industry standard for Python testing. Independence ensures that tests can be run in parallel and failures are isolated, making debugging easier and CI faster.

### III. CLI Standards
**Predictable Interface**: The application MUST adhere to standard CLI practices.
- Exit codes: 0 for success, non-zero for failure.
- Output streams: Structured data/results to `stdout`, logs/errors to `stderr`.
- **Rationale**: Ensures composability with other tools and scripts (Unix philosophy).

## Governance

**Supremacy**: This Constitution supersedes all other project documentation and practices.
**Amendments**: Changes to this document require a Pull Request with a "Sync Impact Report" and explicit approval from the project owner.
**Compliance**: All Pull Requests must be verified against these principles before merging.

**Version**: 1.0.0 | **Ratified**: 2025-11-27 | **Last Amended**: 2025-11-27
