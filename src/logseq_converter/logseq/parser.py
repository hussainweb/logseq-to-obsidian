import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

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
        # Expect format: [Caption](URL)
        # Regex to extract caption and url
        # Note: This is a simple regex, might need to be more robust for nested brackets
        match = re.match(r"^\[([^\]]+)\]\(([^)]+)\)", block.content.strip())
        if not match:
            return None

        caption = match.group(1)
        url = match.group(2)
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

    def _parse_blocks(self, content: str) -> List[Block]:
        lines = content.splitlines()
        root_blocks: List[Block] = []
        stack: List[Tuple[int, Block]] = []  # (indent_level, block)

        for line in lines:
            stripped = line.lstrip()
            if not stripped.startswith("- "):
                # Continuation of previous block or property?
                # For now, append to last block's content if exists
                if stack:
                    _, last_block = stack[-1]
                    last_block.content += "\n" + line
                    # Check for properties in continuation
                    self._parse_properties(line, last_block)
                continue

            indent = len(line) - len(stripped)
            block_content = stripped[2:]

            block = Block(content=block_content)
            self._parse_properties(block_content, block)

            # Find parent
            while stack and stack[-1][0] >= indent:
                stack.pop()

            if stack:
                parent = stack[-1][1]
                parent.children.append(block)
            else:
                root_blocks.append(block)

            stack.append((indent, block))

        return root_blocks

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
