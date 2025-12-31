import sys
from unittest.mock import patch

import pytest

from logseq_converter.cli import main


@pytest.fixture
def source_vault_content(tmp_path):
    vault = tmp_path / "source_vault_content"
    vault.mkdir()

    (vault / "pages").mkdir()
    (vault / "journals").mkdir()
    (vault / "assets").mkdir()

    # Create a journal with content sections
    content = """- Journal entry
- ## #learnings
  - Learned about Rust
    - It's memory safe
  - Learned Python
- ## #achievements
  - Completed the project
    - It was a great learning opportunity
    - I learned a lot
      - Azure Kubernetes Service
      - Azure Container Registry
      - Azure Key Vault
    - It might be time for Azure certification
- ## #highlights
  - Best day ever
    - Had fun
"""
    with open(vault / "journals" / "2025_11_28.md", "w") as f:
        f.write(content)

    return vault


@pytest.fixture
def dest_vault_content(tmp_path):
    return tmp_path / "dest_vault_content"


def test_content_extraction(source_vault_content, dest_vault_content):
    # Mock sys.argv
    test_args = ["logseq-converter", "obsidian", str(source_vault_content), str(dest_vault_content)]
    with patch.object(sys, "argv", test_args):
        ret = main()
        assert ret == 0

    # Verify journal file processed
    dest_journal = dest_vault_content / "Daily" / "2025-11-28.md"
    assert dest_journal.exists()

    with open(dest_journal, "r") as f:
        content = f.read()
        # Should NOT contain sections
        assert "#learnings" not in content
        assert "#achievements" not in content
        assert "#highlights" not in content
        # Should contain other entries
        assert "- Journal entry" in content

    # Verify extracted files for learnings
    learnings_dir = dest_vault_content / "Learnings"
    assert learnings_dir.exists()

    rust_file = learnings_dir / "Learned Rust.md"
    assert rust_file.exists()
    with open(rust_file, "r") as f:
        c = f.read()
        assert "Learned about Rust" in c
        assert "- It's memory safe" in c

    python_file = learnings_dir / "Learned Python.md"
    assert python_file.exists()

    # Verify achievements
    achievements_dir = dest_vault_content / "Achievements"
    assert achievements_dir.exists()

    project_file = achievements_dir / "Completed project.md"
    assert project_file.exists()
    with open(project_file, "r") as f:
        c = f.read()
        assert "Completed the project" in c
        assert "- It was a great learning opportunity" in c
        assert "- I learned a lot" in c
        assert "  - Azure Kubernetes Service" in c
        assert "  - Azure Container Registry" in c
        assert "  - Azure Key Vault" in c
        assert "- It might be time for Azure certification" in c

    # Verify highlights
    highlights_dir = dest_vault_content / "Highlights"
    assert highlights_dir.exists()

    best_day_file = highlights_dir / "Best day ever.md"
    assert best_day_file.exists()
    with open(best_day_file, "r") as f:
        c = f.read()
        assert "Best day ever" in c
        assert "- Had fun" in c
