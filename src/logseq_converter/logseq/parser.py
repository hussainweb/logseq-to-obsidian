import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from mistletoe import Document
from mistletoe.block_token import List as MistletoeList
from mistletoe.block_token import ListItem, Paragraph
from mistletoe.span_token import LineBreak, Link, RawText

from logseq_converter.logseq.models import Block, ContentItem, Journal, LinkItem, Page
from logseq_converter.utils import parse_journal_date


class BlockReferenceScanner:
    def __init__(self):
        self.block_map: Dict[str, Path] = {}  # id -> file_path

    def scan_file(self, file_path: Path) -> None:
        """
        Scans a file for block IDs (id:: uuid) and updates the map.
        """
        if not file_path.exists():
            return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex for id:: uuid
        # It usually appears on its own line or at end of line?
        # LogSeq: `id:: 638...`
        matches = re.findall(r"id::\s*([a-fA-F0-9-]{36})", content)
        for block_id in matches:
            self.block_map[block_id] = file_path

    def get_file_for_block(self, block_id: str) -> Optional[Path]:
        return self.block_map.get(block_id)


class LogSeqParser:
    def parse(self, file_path: Path) -> Union[Page, Journal, None]:
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        blocks = self._parse_blocks(content)

        filename = file_path.name
        journal_date = parse_journal_date(filename)

        if journal_date:
            return Journal(
                filename=filename, date=journal_date, content=content, blocks=blocks
            )
        else:
            return Page(filename=filename, content=content, blocks=blocks)

    def extract_link_items(self, journal: Journal) -> List[LinkItem]:
        link_items: List[LinkItem] = []

        for block in journal.blocks:
            # Check if block content matches #links (case insensitive)
            # It might have other text, but usually it's just #links
            if block.content.strip().lower() == "#links":
                for child in block.children:
                    item = self._parse_link_item(child)
                    if item:
                        link_items.append(item)

        return link_items

    def extract_content_items(self, journal: Journal) -> List[ContentItem]:
        content_items: List[ContentItem] = []
        target_sections = {"#learnings", "#achievements", "#highlights"}

        for block in journal.blocks:
            content_lower = block.content.strip().lower()
            if content_lower in target_sections:
                section_type = content_lower.lstrip("#")
                for child in block.children:
                    item = self._parse_content_item(child, section_type)
                    if item:
                        content_items.append(item)

        return content_items

    def _parse_content_item(
        self, block: Block, item_type: str
    ) -> Optional[ContentItem]:
        description = block.content.strip()
        sub_items = [child.content.strip() for child in block.children]

        return ContentItem(type=item_type, description=description, sub_items=sub_items)

    def _parse_link_item(self, block: Block) -> Optional[LinkItem]:
        # Get the link token that was stored during parsing
        link_token = getattr(block, "_link_token", None)
        if not link_token:
            return None

        # Extract caption from link children
        caption = self._extract_text_from_token(link_token)
        url = link_token.target
        github_url = block.properties.get("github_url")

        sub_items = []
        for child in block.children:
            # Check if child is a property definition
            # Logseq properties in children: key:: value
            prop_match = re.match(r"^([a-zA-Z0-9_-]+)::\s*(.+)", child.content.strip())
            if prop_match:
                key = prop_match.group(1)
                value = prop_match.group(2)
                if key == "github_url":
                    github_url = value
                # We don't add property blocks to sub_items
                continue

            sub_items.append(child.content.strip())

        return LinkItem(
            caption=caption, url=url, github_url=github_url, sub_items=sub_items
        )

    def _find_first_link(self, token) -> Optional[Link]:
        """Recursively search for the first Link token in the AST."""
        if isinstance(token, Link):
            return token

        children = getattr(token, "children", None)
        if children is not None:
            for child in children:
                result = self._find_first_link(child)
                if result:
                    return result

        return None

    def _parse_blocks(self, content: str) -> List[Block]:
        """Parse LogSeq blocks using mistletoe for markdown list structure."""
        doc = Document(content)
        root_blocks: List[Block] = []

        # Find the root list in the document
        for child in doc.children:
            if isinstance(child, MistletoeList):
                # Process each top-level list item as a root block
                for list_item in child.children:
                    block = self._parse_list_item(list_item)
                    if block:
                        root_blocks.append(block)

        return root_blocks

    def _parse_list_item(self, list_item: ListItem) -> Optional[Block]:
        """Convert a mistletoe ListItem to a LogSeq Block."""
        if not list_item.children:
            return None

        # Extract the content from the first paragraph
        first_child = list_item.children[0]
        if isinstance(first_child, Paragraph):
            # Get the full text content including properties
            content = self._extract_text_from_token(first_child)
            # Store any link token found in this paragraph for later extraction
            link_token = self._find_first_link(first_child)
        else:
            content = ""
            link_token = None

        # Create the block
        block = Block(content=content)
        self._parse_properties(content, block)

        # Store the link token as a private attribute for later use
        if link_token:
            block._link_token = link_token

        # Process nested lists as children
        for child in list_item.children[1:]:
            if isinstance(child, MistletoeList):
                for nested_item in child.children:
                    nested_block = self._parse_list_item(nested_item)
                    if nested_block:
                        block.children.append(nested_block)

        return block

    def _extract_text_from_token(self, token) -> str:
        """Extract plain text content from any token, recursively."""
        if isinstance(token, RawText):
            return token.content

        if isinstance(token, LineBreak):
            return "\n"

        children = getattr(token, "children", None)
        if children is not None:
            return "".join(self._extract_text_from_token(child) for child in children)

        return ""

    def _parse_properties(self, text: str, block: Block) -> None:
        # Regex for key:: value
        # Check for id:: specifically for the block ID
        id_match = re.search(r"id::\s*([a-fA-F0-9-]{36})", text)
        if id_match:
            block.id = id_match.group(1)

        # General properties
        props = re.findall(r"([a-zA-Z0-9_-]+)::\s*(.+)", text)
        for key, value in props:
            if key == "id":
                continue
            block.properties[key] = value.strip()
