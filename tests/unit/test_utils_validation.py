import pytest

from logseq_converter.utils import validate_logseq_source


def test_validate_logseq_source_valid_pages(tmp_path):
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    validate_logseq_source(tmp_path)


def test_validate_logseq_source_valid_journals(tmp_path):
    journals_dir = tmp_path / "journals"
    journals_dir.mkdir()
    validate_logseq_source(tmp_path)


def test_validate_logseq_source_missing_dir(tmp_path):
    non_existent = tmp_path / "non_existent"
    with pytest.raises(FileNotFoundError):
        validate_logseq_source(non_existent)


def test_validate_logseq_source_not_a_dir(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.touch()
    with pytest.raises(NotADirectoryError):
        validate_logseq_source(file_path)


def test_validate_logseq_source_invalid_structure(tmp_path):
    # Empty directory
    with pytest.raises(ValueError, match="does not appear to be a valid LogSeq graph"):
        validate_logseq_source(tmp_path)
