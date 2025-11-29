from logseq_converter.logseq.models import Block, Page
from logseq_converter.logseq.parser import LogSeqParser


def test_block_cleaned_content_initialization():
    block = Block(content="test")
    assert block.cleaned_content == ""


def test_page_cleaned_content_initialization():
    page = Page(filename="test.md", content="test")
    assert page.cleaned_content == ""


def test_parser_populates_cleaned_content():
    # Note: This test is expected to fail until T005 is implemented
    content = "- Block content\n  id:: 12345\n  prop:: value"
    parser = LogSeqParser()
    blocks = parser._parse_blocks(content)

    assert len(blocks) == 1
    block = blocks[0]
    assert block.cleaned_content == "Block content"
