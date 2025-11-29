from pathlib import Path
from unittest.mock import MagicMock

from logseq_converter.logseq.parser import BlockReferenceScanner
from logseq_converter.obsidian.converter import ObsidianConverter


def test_transform_properties():
    converter = ObsidianConverter()
    content = """title:: My Page
tags:: tag1, tag2
alias:: alias1

- Block 1
"""
    # Note: title is filtered out as it's an excluded property
    expected = """---
tags: tag1, tag2
alias: alias1
---

- Block 1
"""
    assert converter._transform_properties(content) == expected


def test_transform_block_ids():
    converter = ObsidianConverter()
    content = "- Block content id:: 12345678-1234-1234-1234-1234567890ab"
    expected = "- Block content ^12345678-1234-1234-1234-1234567890ab"
    assert converter._transform_block_ids(content) == expected


def test_transform_block_refs():
    scanner = MagicMock(spec=BlockReferenceScanner)

    converter = ObsidianConverter(scanner)
    content = "Reference to ((12345678-1234-1234-1234-1234567890ab))"

    # Target___Page.md -> Target/Page.md
    expected = "Reference to [[Target/Page#^12345678-1234-1234-1234-1234567890ab]]"

    # Mock return value
    scanner.get_file_for_block.side_effect = (
        lambda uuid: Path("pages/Target___Page.md")
        if uuid == "12345678-1234-1234-1234-1234567890ab"
        else None
    )

    assert converter._transform_block_refs(content) == expected


def test_transform_date_links():
    converter = ObsidianConverter()
    content = "Link to [[15 Nov 2025]]"
    expected = "Link to [[Daily/2025-11-15]]"
    assert converter._transform_date_links(content) == expected

    content2 = "Link to [[Nov 15, 2025]]"
    assert converter._transform_date_links(content2) == expected
