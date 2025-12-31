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
  - [GitHub Site](https://github.com) ([GitHub](https://github.com/repo))
    - GitHub repository
  - [I'm Absolutely Right](https://absolutelyright.lol/) ([GitHub](https://github.com/yoavf/absolutelyright)) #jokes
	- Fun project that captures how many times Claude says, "You're absolutely right."
      - I can host it myself from the GitHub repository.
	- Works by watching Claude's projects directory, so it only works with Claude code.
	- The front-end visualization is quite interesting;
"""
    with open(vault / "journals" / "2025_11_28.md", "w") as f:
        f.write(content)

    return vault


@pytest.fixture
def dest_vault_links(tmp_path):
    return tmp_path / "dest_vault_links"


def test_links_extraction(source_vault_links, dest_vault_links):
    # Mock sys.argv
    test_args = ["logseq-converter", "obsidian", str(source_vault_links), str(dest_vault_links)]
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
        assert '- Fun project that captures how many times Claude says, "You\'re absolutely right."' not in content

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

    absolutely_right_file = links_dir / "Im Absolutely Right.md"
    assert absolutely_right_file.exists()
    with open(absolutely_right_file, "r") as f:
        c = f.read()
        assert "url: https://absolutelyright.lol/" in c
        assert "github_url: https://github.com/yoavf/absolutelyright" in c
        assert "# I'm Absolutely Right" in c
        assert '- Fun project that captures how many times Claude says, "You\'re absolutely right."' in c
        assert "  - I can host it myself from the GitHub repository." in c

    github_file = links_dir / "GitHub Site.md"
    assert github_file.exists()
    with open(github_file, "r") as f:
        c = f.read()
        assert "url: https://github.com" in c
        assert "github_url: https://github.com/repo" in c
