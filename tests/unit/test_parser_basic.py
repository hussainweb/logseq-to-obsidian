from logseq_converter.logseq.models import Journal, Page
from logseq_converter.logseq.parser import LogSeqParser


def test_parse_journal(tmp_path):
    f = tmp_path / "2023_11_28.md"
    content = "- Block 1\n  id:: 550e8400-e29b-41d4-a716-446655440000\n  prop:: val\n- Block 2\n  - Child 1"
    f.write_text(content)

    parser = LogSeqParser()
    journal = parser.parse(f)

    assert isinstance(journal, Journal)
    assert len(journal.blocks) == 2
    # Content includes properties lines because I appended them in _parse_blocks logic
    # "Block 1\n  id:: 123\n  prop:: val"
    assert "Block 1" in journal.blocks[0].content
    assert journal.blocks[0].id == "550e8400-e29b-41d4-a716-446655440000"
    assert journal.blocks[0].properties["prop"] == "val"
    assert len(journal.blocks[1].children) == 1
    assert journal.blocks[1].children[0].content == "Child 1"


def test_parse_page(tmp_path):
    f = tmp_path / "Some Page.md"
    f.write_text("- Block 1")

    parser = LogSeqParser()
    page = parser.parse(f)

    assert isinstance(page, Page)
    assert len(page.blocks) == 1
