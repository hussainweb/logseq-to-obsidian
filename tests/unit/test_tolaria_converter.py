from logseq_converter.logseq.parser import BlockReferenceScanner
from logseq_converter.tolaria.converter import TolariaConverter


def test_tolaria_extract_sections():
    converter = TolariaConverter()
    content = """- Journal Entry 1
- #links
  - [Google](https://google.com)
    - search engine
  - [GitHub](https://github.com)
    - github_url:: https://github.com/repo
- #learnings
  - Learned something new
    - details here
- Other stuff
"""
    original_filename = "2025_11_27.md"

    modified_content, extracted_files = converter.extract_sections(content, original_filename)

    # Verify modified content (sections removed)
    assert "- Journal Entry 1" in modified_content
    assert "- Other stuff" in modified_content
    assert "#links" not in modified_content
    assert "#learnings" not in modified_content

    # Verify extracted files (directly in root, no directories)
    filenames = [f[0] for f in extracted_files]
    assert "Google.md" in filenames
    assert "GitHub.md" in filenames
    assert "Learned something new.md" in filenames

    # Verify contents of extracted files
    found_google = False
    found_learning = False
    for name, file_content in extracted_files:
        if name == "Google.md":
            found_google = True
            assert "type: link" in file_content
            assert "url: https://google.com" in file_content
            assert "date: 2025-11-27" in file_content
            assert "# Google" in file_content
            assert "- search engine" in file_content
        elif name == "Learned something new.md":
            found_learning = True
            assert "type: learning" in file_content
            assert "date: 2025-11-27" in file_content
            assert "Learned something new" in file_content
            assert "- details here" in file_content

    assert found_google
    assert found_learning


def test_tolaria_convert_content_block_refs_and_date_links():
    # Setup scanner with a mock block
    scanner = BlockReferenceScanner()
    # Add a block definition to block map manually
    from pathlib import Path
    scanner.block_map["11111111-1111-1111-1111-111111111111"] = Path("pages/learnings___Networking___VLAN.md")
    scanner.block_map["22222222-2222-2222-2222-222222222222"] = Path("journals/2025_11_27.md")

    converter = TolariaConverter(scanner=scanner)
    content = """- This is a bullet with block ID id:: 11111111-1111-1111-1111-111111111111
- This is a reference ((11111111-1111-1111-1111-111111111111))
- Another reference to journal ((22222222-2222-2222-2222-222222222222))
- A date link [[15 Nov 2025]]
- A logbook to be removed
  :LOGBOOK:
  CLOCK: [2025-11-27 Thu 10:00]--[2025-11-27 Thu 11:00] =>  01:00
  :END:
"""
    result = converter.convert_content(content)

    # id:: uuid -> ^uuid
    assert "^11111111-1111-1111-1111-111111111111" in result
    assert "id:: 11111111-1111-1111-1111-111111111111" not in result

    # ((uuid)) -> [[VLAN#^uuid]] (page path transformed)
    assert "[[VLAN#^11111111-1111-1111-1111-111111111111]]" in result

    # ((uuid)) -> [[journal/2025-11-27#^uuid]] (journal path transformed)
    assert "[[journal/2025-11-27#^22222222-2222-2222-2222-222222222222]]" in result

    # [[15 Nov 2025]] -> [[journal/2025-11-15]]
    assert "[[journal/2025-11-15]]" in result

    # LOGBOOK removed
    assert ":LOGBOOK:" not in result
    assert "CLOCK:" not in result


def test_tolaria_process_metadata_transforms_body():
    converter = TolariaConverter()
    content = """---
title: My Test Learning
---
learnings-prop:: test
- Some content with id:: 11111111-1111-1111-1111-111111111111
- Another line with date link [[15 Nov 2025]]
"""
    filename = "learnings___Subcategory___My Test Learning.md"
    final_name, final_content = converter.process_metadata(filename, content)

    assert final_name == "My Test Learning.md"
    assert "type: learning" in final_content
    # Frontmatter is preserved and merged
    assert "title: My Test Learning" in final_content
    assert "learnings-prop: test" in final_content
    # Content is transformed
    assert "^11111111-1111-1111-1111-111111111111" in final_content
    assert "[[journal/2025-11-15]]" in final_content
