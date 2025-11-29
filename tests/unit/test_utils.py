from datetime import date

from logseq_converter.utils import (
    generate_content_filename,
    parse_journal_date,
    sanitize_filename,
)


def test_parse_journal_date_underscore():
    d = parse_journal_date("2023_11_28.md")
    assert d == date(2023, 11, 28)


def test_parse_journal_date_hyphen():
    d = parse_journal_date("2023-11-28.md")
    assert d == date(2023, 11, 28)


def test_parse_journal_date_invalid():
    d = parse_journal_date("invalid.md")
    assert d is None


def test_parse_journal_date_path():
    d = parse_journal_date("/path/to/2023_11_28.md")
    assert d == date(2023, 11, 28)


def test_sanitize_filename():
    assert sanitize_filename("Hello World.md") == "Hello World.md"
    assert sanitize_filename("invalid/chars?.md") == "invalidchars.md"


def test_generate_content_filename_filters_filler_words():
    """Test that common filler words are filtered out"""
    description = "This is a test to see if the filler words are removed"
    result = generate_content_filename(description)
    # Should remove: is, a, to, see, if, the, are
    assert result == "This test filler words removed"


def test_generate_content_filename_limits_to_10_words():
    """Test that only first 10 meaningful words are used"""
    description = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10 Word11 Word12"
    result = generate_content_filename(description)
    assert result == "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10"


def test_generate_content_filename_with_mixed_case():
    """Test that filler word filtering is case-insensitive"""
    description = "Learning about Python AND JavaScript OR Ruby"
    result = generate_content_filename(description)
    # Should remove: about, AND, OR (case-insensitive)
    assert result == "Learning Python JavaScript Ruby"


def test_generate_content_filename_all_filler_words():
    """Test behavior when description contains only filler words"""
    description = "is to and or the a an"
    result = generate_content_filename(description)
    # Should return empty string when all words are filtered
    assert result == ""


def test_generate_content_filename_with_special_chars():
    """Test that special characters are sanitized"""
    description = "Learning Python/Django with REST APIs"
    result = generate_content_filename(description)
    # Should remove: with
    # Should sanitize: /
    assert result == "Learning PythonDjango REST APIs"


def test_generate_content_filename_custom_max_words():
    """Test custom max_words parameter"""
    description = "Word1 Word2 Word3 Word4 Word5"
    result = generate_content_filename(description, max_words=3)
    assert result == "Word1 Word2 Word3"
