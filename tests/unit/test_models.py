from datetime import date

from logseq_converter.logseq.models import Block, ContentItem, Journal, LinkItem


def test_block_creation():
    block = Block(content="test content", id="123")
    assert block.content == "test content"
    assert block.id == "123"
    assert block.properties == {}
    assert block.children == []


def test_journal_creation():
    journal = Journal(
        filename="2023_01_01.md", date=date(2023, 1, 1), content="some content"
    )
    assert journal.filename == "2023_01_01.md"
    assert journal.date == date(2023, 1, 1)
    assert journal.content == "some content"
    assert journal.blocks == []


def test_link_item_creation():
    item = LinkItem(
        caption="My Link",
        url="https://example.com",
        original_content="[My Link](https://example.com)",
        github_url="https://github.com/example",
    )
    assert item.caption == "My Link"
    assert item.url == "https://example.com"
    assert item.original_content == "[My Link](https://example.com)"
    assert item.github_url == "https://github.com/example"
    assert item.sub_items == []


def test_content_item_creation():
    item = ContentItem(type="learning", description="Learned something new")
    assert item.type == "learning"
    assert item.description == "Learned something new"
    assert item.sub_items == []
