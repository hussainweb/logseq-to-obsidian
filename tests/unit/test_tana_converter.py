import pytest

from logseq_converter.logseq.models import Block, Page
from logseq_converter.tana.converter import TanaConverter


@pytest.fixture
def converter():
    return TanaConverter()


def test_process_links_extraction(converter):
    text = "Link to [[Page One]] and [[Page Two]]"
    cleaned, refs = converter.process_links(text)

    # Verify refs are UIDs (UUIDs)
    assert len(refs) == 2
    # We can verify they are valid UUIDs if we want, or just that they are not the names
    assert "Page One" not in refs
    assert "Page Two" not in refs

    # Verify cleaned text contains UIDs
    for uid in refs:
        assert f"[[{uid}]]" in cleaned


def test_process_tags_extraction(converter):
    text = "Hello #tag1 and #tag2"
    cleaned, tags = converter.process_tags(text)
    assert "tag1" in tags
    assert "tag2" in tags
    assert "#tag1" not in cleaned
    assert "#tag2" not in cleaned


def test_convert_block_simple(converter):
    block = Block(content="Simple block")
    node = converter.convert_block(block)
    assert node.name == "Simple block"
    assert node.type == "node"


def test_convert_block_with_children(converter):
    child = Block(content="Child")
    parent = Block(content="Parent", children=[child])
    node = converter.convert_block(parent)
    assert node.name == "Parent"
    assert len(node.children) == 1
    assert node.children[0].name == "Child"


def test_convert_page(converter):
    block = Block(content="Block 1")
    page = Page(filename="page.md", content="", blocks=[block])
    node = converter.convert_page(page)
    assert node.name == "page"  # filename without extension
    assert len(node.children) == 1
    assert node.children[0].name == "Block 1"
