import sys
from unittest.mock import patch

import pytest

from logseq_converter.cli import main


@pytest.fixture
def source_vault_links(tmp_path):
    vault = tmp_path / "source_vault_links"
    vault.mkdir()

    (vault / "pages").mkdir()
    (vault / "journals").mkdir()
    (vault / "assets").mkdir()

    # Create a journal with #links
    content = """- Journal entry
- ## #links
  - [Google](https://google.com)
    - search engine
  - [GitHub](https://github.com)
    - github_url:: https://github.com/repo
"""
    with open(vault / "journals" / "2025_11_28.md", "w") as f:
        f.write(content)

    return vault


@pytest.fixture
def dest_vault_links(tmp_path):
    return tmp_path / "dest_vault_links"


def test_links_extraction(source_vault_links, dest_vault_links):
    # Mock sys.argv
    test_args = ["logseq-converter", str(source_vault_links), str(dest_vault_links)]
    with patch.object(sys, "argv", test_args):
        ret = main()
        assert ret == 0

    # Verify journal file processed
    dest_journal = dest_vault_links / "Daily" / "2025-11-28.md"
    assert dest_journal.exists()

    with open(dest_journal, "r") as f:
        content = f.read()
        # Should NOT contain #links
        assert "#links" not in content
        assert "Google" not in content
        assert "GitHub" not in content
        # Should contain other entries
        assert "- Journal entry" in content

    # Verify extracted files
    links_dir = dest_vault_links / "Links"
    assert links_dir.exists()

    google_file = links_dir / "Google.md"
    assert google_file.exists()
    with open(google_file, "r") as f:
        c = f.read()
        assert "url: https://google.com" in c
        assert "# Google" in c
        assert "- search engine" in c

    github_file = links_dir / "GitHub.md"
    assert github_file.exists()
    with open(github_file, "r") as f:
        c = f.read()
        assert "url: https://github.com" in c
        assert "github_url: https://github.com/repo" in c
