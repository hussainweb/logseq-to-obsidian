import re
from typing import List, Union

from logseq_converter.logseq.models import Block, Journal, Page


class BlinkoConverter:
    """
    Converts Logseq Page/Journal models to Blinko-compatible Markdown content.
    """

    def convert_page(self, page: Union[Page, Journal]) -> str:
        """
        Converts a Page or Journal to a single Markdown string.
        Title is added as the first line if it's a Page.
        """
        lines = []

        # Add title for pages (Journals usually rely on date, but we can add it too)
        title = ""
        if isinstance(page, Journal):
            title = page.date.strftime("%Y-%m-%d")
        else:
            # Replace hierarchy separator
            title = page.filename.replace(".md", "").replace("___", "/")
            # Strip tags (e.g. #tag) from title
            title = re.sub(r"#[\w\-_]+", "", title).strip()
            # Clean up extra spaces
            title = re.sub(r"\s+", " ", title).strip()

        # Blinko might not have a separate title field exposed easily in 'upsert',
        # so we put it as a H1 at the top of the content.
        lines.append(f"# {title}")
        lines.append("")

        for block in page.blocks:
            lines.extend(self._convert_block(block, level=0))

        return "\n".join(lines)

    def _convert_block(self, block: Block, level: int) -> List[str]:
        """
        Recursively convert blocks to Markdown list items.
        """
        lines = []
        indent = "  " * level

        content = block.content.strip()
        if content:
            # Handle block properties if necessary, or strip them.
            # For now, just dumping content.
            # Assuming bullet points for blocks
            lines.append(f"{indent}- {content}")

        for child in block.children:
            lines.extend(self._convert_block(child, level + 1))

        return lines
