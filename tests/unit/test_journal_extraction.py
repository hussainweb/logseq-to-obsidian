from logseq_converter.obsidian.converter import ObsidianConverter


def test_extract_sections():
    converter = ObsidianConverter()
    content = """- Journal Entry 1
- #links
  - [Google](https://google.com)
    - search engine
  - [GitHub](https://github.com)
    - github_url:: https://github.com/repo
- Other stuff
"""
    original_filename = "2025_11_27.md"

    modified_content, extracted_files = converter.extract_sections(
        content, original_filename
    )

    # Verify modified content (sections removed)
    assert "- Journal Entry 1" in modified_content
    assert "- Other stuff" in modified_content
    assert "#links" not in modified_content

    # Verify extracted files
    filenames = [f[0] for f in extracted_files]
    assert "Links/Google.md" in filenames
    assert "Links/GitHub.md" in filenames

    # Verify content of extracted file
    for name, content in extracted_files:
        if "Google" in name:
            assert "# Google" in content
            assert "url: https://google.com" in content
            assert "- search engine" in content


def test_remove_logbook():
    converter = ObsidianConverter()
    content = """- Task 1
  :LOGBOOK:
  CLOCK: [2025-11-27 Thu 10:00]--[2025-11-27 Thu 11:00] =>  01:00
  :END:
- Task 2
"""
    result = converter.remove_logbook(content)
    assert ":LOGBOOK:" not in result
    assert "CLOCK:" not in result
    assert ":END:" not in result
    assert "- Task 1" in result
    assert "- Task 2" in result


def test_extract_sections_with_heading_markers():
    """
    Test that sections with heading markers (e.g., - ## #links)
    are properly extracted.
    """
    converter = ObsidianConverter()
    content = """- Journal Entry 1
- ## #links
  - [Google](https://google.com)
    - search engine
  - [GitHub](https://github.com)
    - github_url:: https://github.com/repo
- ### #learnings
  - Learned something new
    - details here
- Other stuff
"""
    original_filename = "2025_11_27.md"

    modified_content, extracted_files = converter.extract_sections(
        content, original_filename
    )

    # Verify modified content (sections removed)
    assert "- Journal Entry 1" in modified_content
    assert "- Other stuff" in modified_content
    assert "#links" not in modified_content
    assert "#learnings" not in modified_content

    # Verify extracted files
    filenames = [f[0] for f in extracted_files]
    assert "Links/Google.md" in filenames
    assert "Links/GitHub.md" in filenames
    assert "Learnings/Learned something new.md" in filenames

    # Verify content of extracted file
    for name, file_content in extracted_files:
        if "Google" in name:
            assert "# Google" in file_content
            assert "url: https://google.com" in file_content
            assert "- search engine" in file_content
        elif "Learned" in name:
            assert "Learned something new" in file_content
            assert "- details here" in file_content
