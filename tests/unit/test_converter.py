from datetime import date

from logseq_converter.logseq.models import LinkItem
from logseq_converter.logseq.parser import BlockReferenceScanner
from logseq_converter.obsidian.converter import ObsidianConverter


def test_convert_link_item():
    scanner = BlockReferenceScanner()
    converter = ObsidianConverter(scanner)

    item = LinkItem(
        caption="My Link",
        url="https://example.com",
        original_content="[My Link](https://example.com)",
        github_url="https://github.com/example",
        sub_items=["- Note 1", "- Note 2"],
    )
    journal_date = date(2023, 11, 28)

    filename, content = converter.convert_link_item(item, journal_date)

    assert filename == "My Link.md"
    assert "url: https://example.com" in content
    assert "github_url: https://github.com/example" in content
    assert "date: 2023-11-28" in content
    assert "# My Link" in content
    assert "- [My Link](https://example.com)" in content
    assert "  - Note 1" in content
    assert "  - Note 2" in content


def test_convert_link_item_no_github():
    scanner = BlockReferenceScanner()
    converter = ObsidianConverter(scanner)

    item = LinkItem(
        caption="Simple Link",
        url="https://simple.com",
        original_content="[Simple Link](https://simple.com)",
        sub_items=[],
    )
    journal_date = date(2023, 11, 28)

    filename, content = converter.convert_link_item(item, journal_date)

    assert filename == "Simple Link.md"
    assert "url: https://simple.com" in content
    assert "github_url" not in content
    assert "date: 2023-11-28" in content
    assert "# Simple Link" in content
    assert "- [Simple Link](https://simple.com)" in content
