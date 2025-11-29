from unittest.mock import MagicMock

from logseq_converter.obsidian.converter import ObsidianConverter
from logseq_converter.stats import ConversionStats


def test_stats_initialization():
    stats = ConversionStats()
    assert stats.journals == 0
    assert stats.pages == 0
    assert stats.assets == 0
    assert stats.block_refs == 0
    assert stats.links == 0
    assert stats.learnings == 0
    assert stats.achievements == 0
    assert stats.highlights == 0


def test_converter_uses_stats():
    stats = ConversionStats()
    converter = ObsidianConverter(stats=stats)
    assert converter.stats is stats


def test_block_ref_tracking():
    stats = ConversionStats()
    scanner = MagicMock()
    file_mock = MagicMock()
    file_mock.name = "test.md"
    scanner.get_file_for_block.return_value = file_mock
    converter = ObsidianConverter(scanner=scanner, stats=stats)

    # Simulate block ref transformation
    content = "((12345678-1234-1234-1234-1234567890ab))"
    converter._transform_block_refs(content)

    assert stats.block_refs == 1


def test_extracted_items_tracking():
    stats = ConversionStats()
    converter = ObsidianConverter(stats=stats)

    # Mock extract methods
    converter._extract_link_items = MagicMock(return_value=[("link1.md", "content")])
    converter._extract_content_items = MagicMock(return_value=[("item1.md", "content")])

    # Mock parser
    parser = MagicMock()
    block_mock = MagicMock()
    block_mock.content = "some content"
    block_mock.cleaned_content = "some content"
    block_mock.children = []
    parser._parse_blocks.return_value = [block_mock]

    # Test Links
    converter._process_section_content([], "#links", MagicMock(), parser)
    assert stats.links == 1

    # Test Learnings
    converter._process_section_content([], "#learnings", MagicMock(), parser)
    assert stats.learnings == 1

    # Test Achievements
    converter._process_section_content([], "#achievements", MagicMock(), parser)
    assert stats.achievements == 1

    # Test Highlights
    converter._process_section_content([], "#highlights", MagicMock(), parser)
    assert stats.highlights == 1
