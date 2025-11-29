# Research: Module Refactoring Best Practices

**Decision**: Adhere to standard Python packaging and separation of concerns principles.
- **Parsing & Data Transformation**: Logic responsible for understanding and parsing the source format (Logseq) should reside in its own dedicated module (`logseq_converter.logseq`).
- **Output Generation**: Logic responsible for converting the internal data model into a target format (Obsidian) should be in a separate, dedicated module (`logseq_converter.obsidian`).
- **Core Orchestration & Shared Logic**: The main application module (`logseq_converter`) should handle shared logic (like statistics) and orchestrate the flow from input -> parsing -> output.

**Rationale**: This approach aligns with the Single Responsibility Principle, making the codebase more modular, easier to maintain, and simpler to extend. By decoupling parsing from output generation, we can add new output formats in the future (e.g., for Tana, Roam) with minimal changes to the core parsing logic. This directly supports the goals outlined in the feature specification.

**Alternatives considered**:
- **Monolithic Module**: Keeping all logic in one place. This was rejected as it leads to tightly coupled code that is difficult to maintain and extend, which is the problem this refactoring effort aims to solve.
