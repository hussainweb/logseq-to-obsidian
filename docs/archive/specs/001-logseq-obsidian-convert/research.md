# Research: LogSeq to Obsidian Converter

**Date**: 2025-11-27
**Status**: Done

## 1. Markdown Parsing Library

### Decision
The project will use the `mistletoe` library for parsing Markdown files.

### Rationale
The conversion process requires transforming LogSeq-specific syntax (like block properties `key:: value` and block references `((uuid))`) into Obsidian-compliant Markdown. This requires a parser that can produce an Abstract Syntax Tree (AST) which can be traversed and modified before rendering.

`mistletoe` was chosen because:
- It is a pure-Python, spec-compliant CommonMark parser.
- It builds an AST that is easy to traverse and manipulate.
- It is highly extensible, allowing for the creation of custom tokens and renderers to handle LogSeq's non-standard syntax. This is critical for accurately parsing and converting the source files.

### Alternatives Considered
- **Python-Markdown**: While popular, its primary focus is on HTML conversion and its extension API is less straightforward for AST manipulation compared to `mistletoe`.
- **Mistune**: Known for speed, but its extensibility for complex syntax transformation is not as well-documented as `mistletoe`'s.

## 2. CLI Application Best Practices

### Decision
The CLI will be built using Python's standard `argparse` module for simplicity and to avoid external dependencies for argument parsing. It will follow standard conventions for exit codes and output streams as defined in the constitution.

### Rationale
- **`argparse`**: It is part of the standard library, well-documented, and sufficient for the specified requirements (source and destination paths, verbosity flag). It avoids adding another dependency to the project.
- **Exit Codes**: Adhering to standard exit codes (0 for success, non-zero for failure) ensures predictability and allows the tool to be used in scripts.
- **Streams**: Using `stdout` for results and `stderr` for logs/errors is a fundamental principle of CLI design that ensures composability. The progress indicator will write to `stderr` to avoid polluting `stdout`.

### Alternatives Considered
- **`click` / `typer`**: These are excellent third-party libraries for building complex CLIs. However, for the simple needs of this project (two arguments and a flag), they would be an unnecessary dependency. If the tool's complexity grows, this decision could be revisited.