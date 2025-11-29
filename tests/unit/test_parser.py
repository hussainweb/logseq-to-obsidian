from logseq_converter.logseq.parser import LogSeqParser


def test_parse_links_block(tmp_path):
    content = """
- #links
  - [Google](https://google.com)
    - search engine
  - [My Project](https://github.com/me/project)
    - github_url:: https://github.com/me/project
    - A cool project
"""
    f = tmp_path / "2023_11_28.md"
    f.write_text(content.strip())

    parser = LogSeqParser()
    journal = parser.parse(f)

    assert journal is not None

    # Extract link items from the journal
    # The parser returns a Journal object with Blocks.
    # We need a helper method to identify specific items.
    # The task: "Implement parsing logic... to extract Link Items".
    # This could be a method on LogSeqParser or a separate extractor.
    # Given the architecture, maybe `parser.extract_links(journal)`?
    # Or maybe the Journal model should have a `links` field?
    # The plan says "Implement parsing logic ... in parser.py".

    # Let's assume we add a method `extract_link_items(block)`
    # to the parser or a standalone function.
    # Or maybe we extend the Journal model.
    # Let's try `parser.extract_link_items(journal)`.

    links = parser.extract_link_items(journal)

    assert len(links) == 2

    link1 = links[0]
    assert link1.caption == "Google"
    assert link1.url == "https://google.com"
    assert link1.github_url is None
    assert len(link1.sub_items) == 1
    assert link1.sub_items[0] == "- search engine"

    link2 = links[1]
    assert link2.caption == "My Project"
    assert link2.url == "https://github.com/me/project"
    assert link2.github_url == "https://github.com/me/project"
    assert len(link2.sub_items) == 1
    assert link2.sub_items[0] == "- A cool project"
