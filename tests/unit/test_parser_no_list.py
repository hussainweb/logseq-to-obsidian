from logseq_converter.logseq.parser import LogSeqParser


def test_parse_page_without_list(tmp_path):
    """Test parsing a LogSeq page that doesn't have lists."""
    content = """This is just some plain text content without any list markers."""
    f = tmp_path / "simple_page.md"
    f.write_text(content)

    parser = LogSeqParser()
    page = parser.parse(f)

    assert page is not None
    assert len(page.blocks) == 1
    assert page.blocks[0].content == content


def test_parse_page_without_list_with_frontmatter(tmp_path):
    """Test parsing a LogSeq page with frontmatter but no lists."""
    content = """---
title: My Page
tags: test
---
This is content after frontmatter without list markers."""
    f = tmp_path / "page_with_frontmatter.md"
    f.write_text(content)

    parser = LogSeqParser()
    page = parser.parse(f)

    assert page is not None
    assert len(page.blocks) == 1
    expected = "This is content after frontmatter without list markers."
    assert page.blocks[0].content == expected


def test_parse_page_with_multiline_content_no_list(tmp_path):
    """Test parsing a LogSeq page with multiline content but no lists."""
    content = """This is a first paragraph.

This is a second paragraph after a blank line."""
    f = tmp_path / "multiline.md"
    f.write_text(content)

    parser = LogSeqParser()
    page = parser.parse(f)

    assert page is not None
    # Each paragraph should be a separate block
    assert len(page.blocks) == 2
    assert page.blocks[0].content == "This is a first paragraph."
    assert page.blocks[1].content == "This is a second paragraph after a blank line."


def test_parse_page_with_properties_no_list(tmp_path):
    """Test parsing a LogSeq page with properties but no lists."""
    content = """id:: 12345678-1234-1234-1234-123456789012
This is content with a block ID."""
    f = tmp_path / "props.md"
    f.write_text(content)

    parser = LogSeqParser()
    page = parser.parse(f)

    assert page is not None
    assert len(page.blocks) == 1
    assert page.blocks[0].id == "12345678-1234-1234-1234-123456789012"
    assert "id:: 12345678-1234-1234-1234-123456789012" in page.blocks[0].content


def test_parse_page_mixed_content_and_lists(tmp_path):
    """Test parsing a LogSeq page with both regular content and lists."""
    content = """Some intro text.

- First list item
- Second list item

Some more text."""
    f = tmp_path / "mixed.md"
    f.write_text(content)

    parser = LogSeqParser()
    page = parser.parse(f)

    assert page is not None
    # Should have: intro text, 2 list items, closing text
    assert len(page.blocks) == 4
    assert page.blocks[0].content == "Some intro text."
    assert page.blocks[1].content == "First list item"
    assert page.blocks[2].content == "Second list item"
    assert page.blocks[3].content == "Some more text."


def test_parse_page_with_heading(tmp_path):
    """Test parsing a LogSeq page starting with a heading."""
    content = """# Main Title
Some content under the heading."""
    f = tmp_path / "heading.md"
    f.write_text(content)

    parser = LogSeqParser()
    page = parser.parse(f)

    assert page is not None
    assert len(page.blocks) == 2
    assert page.blocks[0].content == "# Main Title"
    assert page.blocks[1].content == "Some content under the heading."


def test_parse_page_with_heading_and_frontmatter(tmp_path):
    """Test parsing a LogSeq page with frontmatter and heading."""
    content = """---
title: My Doc
---
# Introduction
This is the intro."""
    f = tmp_path / "heading_fm.md"
    f.write_text(content)

    parser = LogSeqParser()
    page = parser.parse(f)

    assert page is not None
    assert len(page.blocks) == 2
    assert page.blocks[0].content == "# Introduction"
    assert page.blocks[1].content == "This is the intro."


def test_parse_page_with_multiple_headings(tmp_path):
    """Test parsing a LogSeq page with multiple heading levels."""
    content = """# Title
## Subtitle
Content here.
### Sub-subtitle
More content."""
    f = tmp_path / "multi_heading.md"
    f.write_text(content)

    parser = LogSeqParser()
    page = parser.parse(f)

    assert page is not None
    assert len(page.blocks) == 5
    assert page.blocks[0].content == "# Title"
    assert page.blocks[1].content == "## Subtitle"
    assert page.blocks[2].content == "Content here."
    assert page.blocks[3].content == "### Sub-subtitle"
    assert page.blocks[4].content == "More content."


def test_parse_page_with_heading_no_list_prefix(tmp_path):
    """Test parsing LogSeq page with heading but no list prefix."""
    content = """## #learnings
- On something...
  - Nested item"""
    f = tmp_path / "heading_section.md"
    f.write_text(content)

    parser = LogSeqParser()
    page = parser.parse(f)

    assert page is not None
    assert len(page.blocks) == 2
    assert page.blocks[0].content == "## #learnings"
    assert page.blocks[1].content == "On something..."
    assert len(page.blocks[1].children) == 1
    assert page.blocks[1].children[0].content == "Nested item"
