# Feature Specification: Parse Journal Blocks

**Feature Branch**: `002-parse-journal-blocks`  
**Created**: 2025-11-28  
**Status**: Draft  
**Input**: User description: "Implement parsing of the daily notes (journals) for blocks of learnings, achievements, highlights, and links. Top level items in each of these blocks will become a separate Markdown file in a corresponding directory. For example, if a journal contains this: ``` - ## #links - [Link Heading](https://example.com) ([GitHub](https://example/example)) #tools - This is an example tool - This is awesome. - [Second link](https://example2.com) #awesome ``` It should: - Create two markdown files: one for 'Link Heading.md', and other for 'Second link.md' in the 'Links' directory. - It should move all the bullet points to those markdown files. - The file name should be generated from the link caption or first few words of the bullet point. - It should set frontmatter proprety for URL, GitHub URL, etc. - It should set a 'date' frontmatter property with the date from the journal. - It should remove these blocks from the journal markdown file. It should work similarly for highlights, achievements, and learnings. Those are simpler and may not have more frontmatter properties (except 'date'). After extracting all the top-level bullet points, the headings themselves are not needed in the journal file, and so they should be removed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract Links from Journals (Priority: P1)

As a user, I want the system to automatically identify and extract link blocks from my daily notes (journals) and convert each top-level link item into a separate Markdown file in a 'Links' directory, populating frontmatter with relevant link details and the journal date, and then remove the extracted block from the original journal file.

**Why this priority**: This is a core part of the feature, as links often contain rich metadata that users want to preserve and organize.

**Independent Test**: Can be fully tested by providing a journal file with a links block and verifying the creation of new Markdown files in the 'Links' directory with correct content and frontmatter, and that the original journal file no longer contains the links block.

**Acceptance Scenarios**:

1.  **Given** a journal file containing a `#links` block with multiple top-level link items (e.g., `[Link Heading](https://example.com) ([GitHub](https://github.com/example/example)) #tools`), **When** the parsing process runs, **Then** a new Markdown file is created for each top-level link item in the 'Links' directory.
2.  **Given** a journal file containing a `#links` block, **When** new Markdown files are created, **Then** each file's name is derived from the link caption or the first few words of the bullet point.
3.  **Given** a journal file containing a `#links` block, **When** new Markdown files are created, **Then** each file contains the bullet points originally associated with the top-level link item.
4.  **Given** a journal file containing a `#links` block, **When** new Markdown files are created, **Then** each file's frontmatter includes properties for `url`, `github_url` (if present), `date` (from the journal), and potentially other relevant link properties.
5.  **Given** a journal file containing a `#links` block, **When** the parsing process runs, **Then** the entire `#links` block (including its heading) is removed from the original journal Markdown file.

### User Story 2 - Extract Learnings, Achievements, and Highlights from Journals (Priority: P1)

As a user, I want the system to identify and extract 'learnings', 'achievements', and 'highlights' blocks from my daily notes (journals) and convert each top-level item into a separate Markdown file in corresponding directories (e.g., 'Learnings', 'Achievements', 'Highlights'), populating frontmatter with the journal date, and then remove the extracted block from the original journal file.

**Why this priority**: These are also core content types that users often want to separate and organize for review and reflection.

**Independent Test**: Can be fully tested by providing a journal file with 'learnings', 'achievements', and 'highlights' blocks and verifying the creation of new Markdown files in the respective directories with correct content and frontmatter, and that the original journal file no longer contains these blocks.

**Acceptance Scenarios**:

1.  **Given** a journal file containing `#learnings`, `#achievements`, or `#highlights` blocks, **When** the parsing process runs, **Then** a new Markdown file is created for each top-level item in the respective directory ('Learnings', 'Achievements', 'Highlights').
2.  **Given** a journal file containing such blocks, **When** new Markdown files are created, **Then** each file's name is derived from the first few words of the top-level bullet point.
3.  **Given** a journal file containing such blocks, **When** new Markdown files are created, **Then** each file contains the bullet points originally associated with the top-level item.
4.  **Given** a journal file containing such blocks, **When** new Markdown files are created, **Then** each file's frontmatter includes a `date` property from the journal.
5.  **Given** a journal file containing such blocks, **When** the parsing process runs, **Then** the entire block (including its heading) is removed from the original journal Markdown file.

### Edge Cases

-   What happens when a journal file does not contain any of the specified blocks (links, learnings, achievements, highlights)? The system should process the journal without error and make no changes to the file.
-   How does the system handle duplicate link captions or learning/achievement/highlight descriptions when generating filenames? The system should append a unique identifier (e.g., a counter) to ensure unique filenames.
-   What if a link in the `#links` block does not have a GitHub URL? The `github_url` frontmatter property should simply be omitted.
-   What if a block (e.g., `#links`) is empty or contains only the heading? The system should remove the heading but not create any new files.

## Requirements *(mandatory)*

### Functional Requirements

-   **FR-001**: The system MUST identify and extract specific blocks (`#links`, `#learnings`, `#achievements`, `#highlights`) within Logseq daily notes (journals).
-   **FR-002**: The system MUST create new Markdown files for each top-level item within the identified blocks.
-   **FR-003**: The system MUST generate filenames for the new Markdown files based on the item's caption (for links) or the first few words of the bullet point (for other blocks).
-   **FR-004**: The system MUST move all sub-bullet points associated with a top-level item to its corresponding new Markdown file.
-   **FR-005**: The system MUST populate the frontmatter of new Markdown files created from `#links` blocks with `url` and `github_url` (if present) properties.
-   **FR-006**: The system MUST populate the frontmatter of all newly created Markdown files with a `date` property, derived from the journal's date.
-   **FR-007**: The system MUST remove the entire extracted block (including its heading) from the original journal Markdown file after extraction.
-   **FR-008**: The system MUST ensure unique filenames for newly created Markdown files, even if captions or descriptions are identical.
-   **FR-009**: The system SHOULD gracefully handle journal files that do not contain any target blocks without error or modification.

### Non-Functional Requirements

-   **NFR-001**: The system MUST handle vaults of any size, with performance linearly scaling with the number of files.
-   **NFR-002**: The system MUST log errors and continue processing other files, leaving failed files in their original state.
-   **NFR-003**: The system MUST log essential progress (e.g., file started, file completed, errors) to the console with timestamps.

### Key Entities *(include if feature involves data)*

-   **Journal**: Represents a Logseq daily note, characterized by its date and Markdown content.
-   **Block**: A section within a Journal, identified by a heading (e.g., `#links`, `#learnings`). Contains a list of top-level items and their sub-items.
-   **Link Item**: A top-level item within a `#links` block, containing a URL and potentially a GitHub URL.
-   **Content Item**: A top-level item within `#learnings`, `#achievements`, or `#highlights` blocks.
-   **Markdown File**: The output file for each extracted item, containing the item's content and frontmatter.

## Success Criteria *(mandatory)*

### Measurable Outcomes

-   **SC-001**: For journal files containing identified blocks, 100% of top-level items within these blocks are successfully extracted into separate Markdown files.
-   **SC-002**: For each extracted item, the corresponding original block (including its heading) is removed from the journal file with 100% accuracy.
-   **SC-003**: All newly created Markdown files from `#links` blocks contain accurate `url` and `github_url` (if present) properties in their frontmatter.
-   **SC-004**: All newly created Markdown files contain the correct `date` property in their frontmatter, corresponding to the journal's date.
-   **SC-005**: The conversion process completes for a vault of 100 journal files in under 5 seconds.

## Clarifications

### Session 2025-11-28

- Q: What are the scalability expectations for much larger vaults (e.g., 1000+ journal files)? → A: The system should handle vaults of any size, with performance linearly scaling with the number of files.
- Q: How should the system handle failures during the conversion process (e.g., if the script crashes mid-way? Should it be resumable, or should it revert changes)? → A: The system should log errors and continue processing other files, leaving failed files in their original state.
- Q: Should the system provide any logging or feedback during its operation? If so, what level of detail and where should it be output (e.g., console, file, specific format)? → A: Log essential progress (e.g., file started, file completed, errors) to the console with timestamps.
- Q: Are there any specific technical constraints or preferences for the implementation beyond using Python (e.g., memory usage limits, processing time per file, specific libraries to avoid/prefer)? → A: No specific technical constraints beyond Python; the developer has full autonomy.
- Q: Is there anything that is explicitly NOT part of this feature (e.g., handling non-Markdown files in journals, custom block types not specified, bidirectional links management)? → A: Only the explicitly defined functional requirements are in scope; anything not mentioned is implicitly out of scope.
