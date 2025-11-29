from logseq_converter.utils import is_markdown_empty


def test_is_markdown_empty_with_empty_string():
    assert is_markdown_empty("")


def test_is_markdown_empty_with_whitespace():
    assert is_markdown_empty("   \n\n  \t  ")


def test_is_markdown_empty_with_only_hyphens():
    assert is_markdown_empty("---\n---")


def test_is_markdown_empty_with_only_list_markers():
    assert is_markdown_empty("- \n  - \n    - ")


def test_is_markdown_empty_with_hyphens_and_whitespace():
    assert is_markdown_empty("  -  \n  -  \n  ")


def test_is_not_empty_with_content():
    assert not is_markdown_empty("# Heading\nSome content")


def test_is_not_empty_with_text():
    assert not is_markdown_empty("Hello world")


def test_is_not_empty_with_list_content():
    assert not is_markdown_empty("- Item with text")


def test_is_not_empty_with_frontmatter_and_content():
    content = """---
date: 2025-11-29
---
Some actual content"""
    assert not is_markdown_empty(content)
