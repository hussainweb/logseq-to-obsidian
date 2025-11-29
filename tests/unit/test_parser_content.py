from logseq_converter.logseq.parser import LogSeqParser


def test_parse_content_blocks(tmp_path):
    content = """
- #learnings
  - Learned about Rust
    - It's memory safe
- #achievements
  - Completed the project
- #highlights
  - Best day ever
"""
    f = tmp_path / "2023_11_28.md"
    f.write_text(content.strip())

    parser = LogSeqParser()
    journal = parser.parse(f)

    items = parser.extract_content_items(journal)

    assert len(items) == 3

    learning = next(i for i in items if i.type == "learnings")
    assert learning.description == "Learned about Rust"
    assert len(learning.sub_items) == 1
    assert learning.sub_items[0] == "- It's memory safe"

    achievement = next(i for i in items if i.type == "achievements")
    assert achievement.description == "Completed the project"
    assert len(achievement.sub_items) == 0

    highlight = next(i for i in items if i.type == "highlights")
    assert highlight.description == "Best day ever"
