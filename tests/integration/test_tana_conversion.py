import json

from logseq_converter.cli import convert_to_tana


def test_end_to_end_conversion(tmp_path):
    # Setup LogSeq vault
    source = tmp_path / "logseq_vault"
    pages = source / "pages"
    journals = source / "journals"
    pages.mkdir(parents=True)
    journals.mkdir(parents=True)

    # Create a page
    page_content = """
- Block 1
  - Child 1
- Block 2 #tag
"""
    (pages / "Page1.md").write_text(page_content, encoding="utf-8")

    # Create a journal
    journal_content = """
- Journal Block
"""
    (journals / "2023_11_30.md").write_text(journal_content, encoding="utf-8")

    # Destination - now a file path
    destination = tmp_path / "tana_output" / "export.json"

    # Run conversion
    ret = convert_to_tana(source, destination, verbose=True, force=False, dry_run=False)
    assert ret == 0

    # Verify output
    assert destination.exists()
    assert destination.is_file()

    # Verify content
    with open(destination) as f:
        data = json.load(f)
        assert data["version"] == "TanaIntermediateFile V0.1"
        # Should have 2 root nodes (Page1 and Journal)
        assert len(data["nodes"]) == 2

        # Find Page1 node
        page_node = next((n for n in data["nodes"] if n["name"] == "Page1"), None)
        assert page_node is not None
        assert len(page_node["children"]) == 2

        # Check tag (should be in global supertags list)
        assert "tag" in [t["name"] for t in data["supertags"]]
