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


def test_obsidian_convert_content_tasks_and_schedules():
    converter = ObsidianConverter()
    content = """- TODO Buy groceries
  SCHEDULED: <2025-11-28 Fri>
- DOING Working on migration DEADLINE: <2025-12-01 Mon>
- DONE Done with task
- CANCELLED Obsolete task
- WAITING Awaiting response
"""
    result = converter.convert_content(content)
    assert "- [ ] Buy groceries ⏳ 2025-11-28" in result
    assert "- [/] Working on migration 📅 2025-12-01" in result
    assert "- [x] Done with task" in result
    assert "- [-] Obsolete task" in result
    assert "- [?] Awaiting response" in result


def test_obsidian_should_ignore():
    converter = ObsidianConverter()
    assert converter.should_ignore("Readwise.md") is True
    assert converter.should_ignore("articles___Highlights___Post1.md") is True
    assert converter.should_ignore("books___Highlights___Book1.md") is True
    assert converter.should_ignore("projects___MyProject.md") is False
