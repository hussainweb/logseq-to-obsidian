# Research: Module Refactoring and Data Flow

**Decision**: Adhere to a staged data transformation pipeline pattern, aligned with standard Python module separation.
- **Parsing & Cleaning (`logseq_converter.logseq`)**: This module is responsible for both parsing the raw Logseq files and cleaning the content. It ingests raw text and outputs structured data models (`Page`, `Block`) that are fully populated, including the `cleaned_content` field where Logseq-specific properties have been removed.
- **Core Orchestration & Shared Logic (`logseq_converter`)**: This main module handles orchestrating the flow from input -> parsing -> output generation. It will also house any logic that is truly shared across all modules, such as statistics calculation.
- **Output Generation (`logseq_converter.obsidian`)**: This module's sole responsibility is to take the clean, structured data models from the parsing stage and convert them into the target format (Obsidian Markdown). It should not contain any parsing or cleaning logic.

**Rationale**: This approach creates a clear, unidirectional data flow (`raw file -> clean data model -> output file`). This enhances the Single Responsibility Principle, making the codebase more modular and easier to debug. By ensuring the `logseq` module provides a "complete" and clean data model, the contract between the modules is simplified, and future output modules can be added with minimal effort, as they can rely on the same clean data source.

**Alternatives considered**:
- **Cleaning in the Output Module**: This was rejected. Having the `obsidian` module perform the cleaning would mean this logic would have to be duplicated for any new output format added in the future. It violates the DRY (Don't Repeat Yourself) principle and complicates the output modules unnecessarily.