import sys
from unittest.mock import patch

import pytest

from logseq_converter.cli import main


@pytest.fixture
def source_vault_empty(tmp_path):
    vault = tmp_path / "source_vault_empty"
    vault.mkdir()

    (vault / "pages").mkdir()
    (vault / "journals").mkdir()

    # Create a journal with ONLY sections - no other content
    # After extraction, the journal file should be empty and not written
    content = """- ## #learnings
  - Learned about empty file handling
    - Files with no meaningful content should be skipped
  - Another learning about Markdown
- ## #links
  - [Empty File Detection](https://example.com/empty-files)
    - This is important for clean output
"""
    with open(vault / "journals" / "2025_11_29.md", "w") as f:
        f.write(content)

    return vault


@pytest.fixture
def dest_vault_empty(tmp_path):
    return tmp_path / "dest_vault_empty"


def test_empty_journal_after_extraction_not_written(source_vault_empty, dest_vault_empty):
    """Test that journal files are not written when empty after extraction."""
    # Mock sys.argv
    test_args = [
        "logseq-converter",
        "obsidian",
        str(source_vault_empty),
        str(dest_vault_empty),
    ]
    with patch.object(sys, "argv", test_args):
        ret = main()
        assert ret == 0

    # Verify journal file was NOT created (empty after extraction)
    dest_journal = dest_vault_empty / "Daily" / "2025-11-29.md"
    assert not dest_journal.exists(), "Journal file should not exist when empty after extraction"

    # Verify that Learnings directory was created with extracted files
    learnings_dir = dest_vault_empty / "Learnings"
    assert learnings_dir.exists()

    learning1 = learnings_dir / "Learned empty file handling.md"
    assert learning1.exists()
    with open(learning1, "r") as f:
        content = f.read()
        assert "date: 2025-11-29" in content
        assert "Learned about empty file handling" in content
        assert "Files with no meaningful content should be skipped" in content

    learning2 = learnings_dir / "Another learning Markdown.md"
    assert learning2.exists()
    with open(learning2, "r") as f:
        content = f.read()
        assert "date: 2025-11-29" in content
        assert "Another learning about Markdown" in content

    # Verify that Links directory was created with extracted files
    links_dir = dest_vault_empty / "Links"
    assert links_dir.exists()

    link1 = links_dir / "Empty File Detection.md"
    assert link1.exists()
    with open(link1, "r") as f:
        content = f.read()
        assert "url: https://example.com/empty-files" in content
        assert "date: 2025-11-29" in content
        assert "Empty File Detection" in content
        assert "This is important for clean output" in content
