from datetime import date

from logseq_converter.logseq.models import ContentItem
from logseq_converter.logseq.parser import BlockReferenceScanner
from logseq_converter.obsidian.converter import ObsidianConverter


def test_convert_content_item_learning():
    scanner = BlockReferenceScanner()
    converter = ObsidianConverter(scanner)

    item = ContentItem(
        type="learnings",
        description="Learned about Python",
        sub_items=["It's great", "Very readable"],
    )
    journal_date = date(2023, 11, 28)

    filename, content = converter.convert_content_item(item, journal_date)

    assert filename == "Learned Python.md"
    assert "date: 2023-11-28" in content
    assert "Learned about Python" in content
    assert "- It's great" in content
    assert "- Very readable" in content


def test_convert_content_item_achievement():
    scanner = BlockReferenceScanner()
    converter = ObsidianConverter(scanner)

    item = ContentItem(
        type="achievements", description="Completed the project", sub_items=[]
    )
    journal_date = date(2023, 11, 28)

    filename, content = converter.convert_content_item(item, journal_date)

    assert filename == "Completed project.md"
    assert "date: 2023-11-28" in content
    assert "Completed the project" in content


def test_convert_content_item_highlight():
    scanner = BlockReferenceScanner()
    converter = ObsidianConverter(scanner)

    item = ContentItem(
        type="highlights",
        description="Best day ever",
        sub_items=["Had fun", "Met friends"],
    )
    journal_date = date(2023, 11, 28)

    filename, content = converter.convert_content_item(item, journal_date)

    assert filename == "Best day ever.md"
    assert "date: 2023-11-28" in content
