# Research Summary: Export LogSeq to Tana Intermediate Format

## Decision: LogSeq Parsing

**Decision**: The existing `logseq` module's parser will be used to handle LogSeq markdown.
**Rationale**: User confirmation explicitly stated that "the existing logseq module already has everything you need", indicating a preference for leveraging existing project components.
**Alternatives considered**:
- Using an external, third-party LogSeq parsing library.
- Building a new, custom LogSeq parser from scratch.

## Decision: Out-of-Scope Features

**Decision**: The following LogSeq-specific features are explicitly out-of-scope for the initial conversion: Advanced LogSeq queries, Templates, and Diagram/whiteboard features.
**Rationale**: User selection prioritized core functionality and acknowledged the complexity and potential lack of direct Tana equivalents for these features, preventing scope creep for the initial release.
**Alternatives considered**:
- Attempting to convert all LogSeq features, which would significantly increase complexity and development time.
- Handling embedded assets and custom CSS/themes, which were also considered but deemed less critical for the initial conversion.

## Decision: Handling LogSeq Block Properties

**Decision**: LogSeq block properties (other than `tags`) that do not have a direct or obvious equivalent in Tana's predefined fields will be ignored.
**Rationale**: User selection indicated a preference for simplicity and avoiding over-engineering for properties that may not have clear mappings in Tana.
**Alternatives considered**:
- Converting them into Tana "fields" with a prefix (e.g., `logseq_`) to avoid name collisions.
- Attempting to intelligently map them to Tana's more general "description" or "content" fields.

## Decision: Error Reporting and Logging Strategy

**Decision**: Detailed error messages will always be presented to the user, with no separate logging.
**Rationale**: User preference prioritizes immediate and comprehensive feedback directly to the user over background logging for a CLI tool.
**Alternatives considered**:
- Minimal error messages for the user with detailed technical logging to a file.
- User-friendly error messages for critical issues with detailed technical logging to a file for debugging.

## Decision: Tana Intermediate Format Version

**Decision**: The converter will target the latest stable version of the Tana Intermediate Format available at the time of implementation.
**Rationale**: User preference allows for flexibility and ensures compatibility with the most up-to-date Tana specification, minimizing potential for outdated format issues.
**Alternatives considered**:
- Pinning to a specific, immutable version number of the Tana Intermediate Format.

## Formal Definition of the Tana Intermediate Format

**Source**: `https://raw.githubusercontent.com/tanainc/tana-import-tools/refs/heads/main/src/types/types.ts`
**Rationale**: This URL provides the canonical TypeScript definition of the Tana Intermediate Format, which will serve as the definitive reference for implementing the conversion logic and ensuring 100% compliance (SC-004).
