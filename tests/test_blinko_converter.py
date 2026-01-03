import unittest
from datetime import datetime

from logseq_converter.blinko.converter import BlinkoConverter
from logseq_converter.logseq.models import Block, Journal, Page


class TestBlinkoConverter(unittest.TestCase):
    def setUp(self):
        self.converter = BlinkoConverter()

    def test_convert_page(self):
        blocks = [
            Block(content="Block 1", properties={}),
            Block(content="Block 2", properties={}, children=[Block(content="Child 2.1", properties={})]),
        ]
        # Test cleaning of tags from filename/title
        page = Page(filename="My___Page #tag1 #tag-2.md", content="", blocks=blocks)

        result = self.converter.convert_page(page)

        self.assertIn("# My/Page", result)
        self.assertNotIn("#tag1", result.split("\n")[0])  # Check title line
        self.assertNotIn("#tag-2", result.split("\n")[0])
        self.assertIn("- Block 1", result)
        self.assertIn("- Block 2", result)
        self.assertIn("  - Child 2.1", result)

    def test_convert_journal(self):
        blocks = [Block(content="Journal Entry", properties={})]
        date = datetime(2023, 10, 27)
        journal = Journal(filename="2023_10_27.md", content="", blocks=blocks, date=date)

        result = self.converter.convert_page(journal)

        self.assertIn("# 2023-10-27", result)
        self.assertIn("- Journal Entry", result)
