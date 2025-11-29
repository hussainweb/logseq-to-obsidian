import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from mistletoe import Document
from mistletoe.block_token import List as MistletoeList
from mistletoe.block_token import ListItem, Paragraph
from mistletoe.markdown_renderer import MarkdownRenderer
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
        sub_items = self._flatten_block_content_with_indent(block.children, depth=0)

        return ContentItem(type=item_type, description=description, sub_items=sub_items)

    def _flatten_block_content_with_indent(
        self, blocks: List[Block], depth: int = 0
    ) -> List[str]:
        """Recursively flatten block hierarchy with indentation preserved."""
        result = []
        indent = "  " * depth  # 2 spaces per level
        for block in blocks:
            result.append(f"{indent}- {block.content.strip()}")
            if block.children:
                result.extend(
                    self._flatten_block_content_with_indent(block.children, depth + 1)
                )
        return result

    def _parse_link_item(self, block: Block) -> Optional[LinkItem]:
        # Get the link token that was stored during parsing
        link_token = getattr(block, "_link_token", None)
        if not link_token:
            return None

        # Extract caption from link children
        caption = self._extract_text_from_token(link_token)
        url = link_token.target

        # Look for a link named "GitHub" (case-insensitive) in the top-level item
        github_url = self._find_github_link_url(block)

        sub_items = []
        for child in block.children:
            # Add child content and recursively add nested children
            sub_items.append(f"- {child.content.strip()}")
            if child.children:
                sub_items.extend(
                    self._flatten_block_content_with_indent(child.children, depth=1)
                )

        return LinkItem(
            caption=caption,
            url=url,
            original_content=block.content.strip(),
            github_url=github_url,
            sub_items=sub_items,
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

    def _find_all_links(self, token) -> List[Link]:
        """Recursively find all Link tokens in the AST."""
        links = []
        if isinstance(token, Link):
            links.append(token)

        children = getattr(token, "children", None)
        if children is not None:
            for child in children:
                links.extend(self._find_all_links(child))

        return links

    def _find_github_link_url(self, block: Block) -> Optional[str]:
        """Find a link with caption 'GitHub' (case-insensitive) in the block content."""
        # Parse the block content to find all links
        doc = Document(block.content)

        for child in doc.children:
            if isinstance(child, Paragraph):
                all_links = self._find_all_links(child)
                for link in all_links:
                    caption = self._extract_text_from_token(link).strip()
                    if caption.lower() == "github":
                        return link.target

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
            # Get the markdown content preserving formatting
            content = self._extract_markdown_from_paragraph(first_child)
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

    def _extract_markdown_from_paragraph(self, paragraph: Paragraph) -> str:
        """Extract markdown content from a Paragraph token."""
        with MarkdownRenderer() as renderer:
            # Render just the children (span tokens) preserving markdown
            parts = []
            for child in paragraph.children:
                if isinstance(child, LineBreak):
                    # Preserve line breaks as newlines
                    parts.append("\n")
                else:
                    rendered = renderer.render(child)
                    # Remove trailing newline added by renderer
                    if rendered and rendered.endswith("\n"):
                        rendered = rendered[:-1]
                    parts.append(rendered)
            return "".join(parts)

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
