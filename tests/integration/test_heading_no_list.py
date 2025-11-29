import sys
from unittest.mock import patch

import pytest

from logseq_converter.cli import main


@pytest.fixture
def source_vault_heading(tmp_path):
    vault = tmp_path / "source_vault_heading"
    vault.mkdir()

    (vault / "pages").mkdir()
    (vault / "journals").mkdir()
    (vault / "assets").mkdir()

    # Create a journal with heading without list prefix
    content = """## #learnings
- Discovered that LogSeq can have headings without list prefixes
  - This is common in pages with single implicit list items
  - The parser needs to handle BlockToken types generically
- Another learning about markdown parsing
  - Mistletoe provides different token types for different blocks"""
    with open(vault / "journals" / "2025_11_29.md", "w") as f:
        f.write(content)

    # Create a page with heading and frontmatter
    page_content = """---
title: Project Notes
tags: documentation
---
# Overview
This is a project overview without a list prefix.

## Details
- First detail
- Second detail"""
    with open(vault / "pages" / "Project Notes.md", "w") as f:
        f.write(page_content)

    return vault


@pytest.fixture
def dest_vault_heading(tmp_path):
    return tmp_path / "dest_vault_heading"


def test_heading_without_list_conversion(source_vault_heading, dest_vault_heading):
    # Mock sys.argv
    test_args = [
        "logseq-converter",
        str(source_vault_heading),
        str(dest_vault_heading),
    ]
    with patch.object(sys, "argv", test_args):
        ret = main()
        assert ret == 0

    # Verify journal file processed
    dest_journal = dest_vault_heading / "Daily" / "2025-11-29.md"
    assert dest_journal.exists()

    with open(dest_journal, "r") as f:
        content = f.read()
        # #learnings section should be removed from journal
        assert "## #learnings" not in content
        assert "#learnings" not in content
        assert "LogSeq can have headings without list prefixes" not in content

    # Verify extracted learnings files
    learnings_dir = dest_vault_heading / "Learnings"
    assert learnings_dir.exists()

    # First learning (filename based on content)
    learning1_file = "Discovered that LogSeq headings without list prefixes.md"
    learning1 = learnings_dir / learning1_file
    assert learning1.exists()
    with open(learning1, "r") as f:
        c = f.read()
        assert "date: 2025-11-29" in c
        content_line = "Discovered that LogSeq can have headings without list prefixes"
        assert content_line in c
        assert "This is common in pages with single implicit list items" in c
        assert "The parser needs to handle BlockToken types generically" in c

    # Second learning (filename based on content)
    learning2_file = "Another learning markdown parsing.md"
    learning2 = learnings_dir / learning2_file
    assert learning2.exists()
    with open(learning2, "r") as f:
        c = f.read()
        assert "date: 2025-11-29" in c
        assert "Another learning about markdown parsing" in c
        assert "Mistletoe provides different token types for different blocks" in c

    # Verify page file processed
    dest_page = dest_vault_heading / "Project Notes.md"
    assert dest_page.exists()

    with open(dest_page, "r") as f:
        content = f.read()
        # Frontmatter should be preserved (title is excluded by converter)
        assert "---" in content
        assert "tags: documentation" in content
        # Headings should be preserved
        assert "# Overview" in content
        assert "## Details" in content
        # Content should be preserved
        assert "This is a project overview without a list prefix." in content
        assert "- First detail" in content
        assert "- Second detail" in content
