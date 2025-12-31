import sys
from unittest.mock import patch

import pytest

from logseq_converter.cli import main


@pytest.fixture
def source_vault(tmp_path):
    vault = tmp_path / "source_vault"
    vault.mkdir()

    (vault / "pages").mkdir()
    (vault / "journals").mkdir()
    (vault / "assets").mkdir()

    # Create a journal
    with open(vault / "journals" / "2025_11_27.md", "w") as f:
        f.write("- Journal entry")

    # Create a page
    with open(vault / "pages" / "Category___Topic.md", "w") as f:
        f.write("- Page content")

    # Create an asset
    with open(vault / "assets" / "image.png", "w") as f:
        f.write("fake image content")

    return vault


@pytest.fixture
def dest_vault(tmp_path):
    return tmp_path / "dest_vault"


def test_full_vault_conversion(source_vault, dest_vault):
    # Mock sys.argv
    test_args = ["logseq-converter", "obsidian", str(source_vault), str(dest_vault)]
    with patch.object(sys, "argv", test_args):
        ret = main()
        assert ret == 0

    # Verify structure
    assert (dest_vault / "Daily" / "2025-11-27.md").exists()
    assert (dest_vault / "Category" / "Topic.md").exists()
    assert (dest_vault / "assets" / "image.png").exists()

    # Verify content
    with open(dest_vault / "Daily" / "2025-11-27.md", "r") as f:
        assert f.read() == "- Journal entry"

    with open(dest_vault / "Category" / "Topic.md", "r") as f:
        assert f.read() == "- Page content"
