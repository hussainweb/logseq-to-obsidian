import re
from datetime import date, datetime
from typing import Optional, Tuple

from logseq_converter.logseq.models import ContentItem, LinkItem
from logseq_converter.logseq.parser import BlockReferenceScanner
from logseq_converter.utils import generate_content_filename, sanitize_filename


class ObsidianConverter:
    def __init__(self, scanner: Optional[BlockReferenceScanner] = None):
        self.scanner = scanner

    def transform_journal_filename(self, filename: str) -> Optional[str]:
        """
        Transforms LogSeq journal filename (YYYY_MM_DD.md) to Obsidian
        format (Daily/YYYY-MM-DD.md).
        """
        # Match YYYY_MM_DD.md
        match = re.match(r"(\d{4})_(\d{2})_(\d{2})\.md", filename)
        if match:
            year, month, day = match.groups()
            return f"Daily/{year}-{month}-{day}.md"
        return None

    def transform_page_filename(self, filename: str) -> str:
        """
        Transforms LogSeq page filename (A___B.md) to Obsidian format (A/B.md).
        """
        # Replace ___ with /
        new_name = filename.replace("___", "/")
        return new_name

    def convert_content(self, content: str) -> str:
        """
        Converts LogSeq content to Obsidian content.
        """
        try:
            # 0. Remove Logbook
            content = self.remove_logbook(content)

            # 1. Properties to Frontmatter
            content = self._transform_properties(content)

            # 2. Block IDs
            content = self._transform_block_ids(content)

            # 3. Block Refs
            content = self._transform_block_refs(content)

            # 4. Date Links
            content = self._transform_date_links(content)

            return content
        except Exception as e:
            from logseq_converter.utils import log_warning

            log_warning(f"Error converting content: {e}. Returning original content.")
            return content

    def remove_logbook(self, content: str) -> str:
        # Remove :LOGBOOK: ... :END:
        return re.sub(r":LOGBOOK:.*?:END:", "", content, flags=re.DOTALL)

    def extract_sections(
        self, content: str, original_filename: str
    ) -> tuple[str, list[tuple[str, str]]]:
        """
        Extracts specific sections from journal entries.
        Returns (modified_content, list_of_extracted_files).
        """
        from logseq_converter.logseq.parser import LogSeqParser
        from logseq_converter.utils import parse_journal_date

        extracted_files = []
        lines = content.split("\n")
        new_lines = []

        parser = LogSeqParser()
        journal_date = parse_journal_date(original_filename)
        if not journal_date:
            # If we can't parse date, we can't properly set frontmatter date
            # But we should probably still try?
            # For now, default to today or skip?
            # Let's use today as fallback or error?
            # The original filename is passed, e.g. 2023_11_28.md
            pass

        i = 0
        while i < len(lines):
            line = lines[i]
            # Match #links (case insensitive)
            # Support both "- #links" and "- ## #links" formats
            match = re.match(
                r"^-\s+(#{1,6}\s+)?(#links|#learnings|#achievements|#highlights)\s*$",
                line,
                re.IGNORECASE,
            )

            if match:
                section_name = match.group(2).lower()  # e.g., #links
                # (group 2 because group 1 is optional heading marker)
                initial_indent = len(line) - len(line.lstrip())
                section_lines = [line]
                i += 1  # Move to the next line after the section header

                # Capture children lines that are more indented or continuation lines
                while i < len(lines):
                    child_line = lines[i]

                    # If the line is empty or only contains whitespace,
                    # it's considered part of the current section
                    if not child_line.strip():
                        section_lines.append(child_line)
                        i += 1
                        continue

                    current_indent = len(child_line) - len(child_line.lstrip())

                    # A new top-level block is identified if:
                    # 1. It starts with a list item marker ('-' or '*')
                    # 2. Its indentation is less than or equal to the initial
                    #    section header's indentation
                    is_new_block_at_or_above_section_level = (
                        re.match(r"^(-|\*)\s+", child_line)
                        and current_indent <= initial_indent
                    )

                    if is_new_block_at_or_above_section_level:
                        break  # End of current section content

                    section_lines.append(child_line)
                    i += 1

                # Construct block text
                block_text = "\n".join(section_lines)

                # Parse this block
                blocks = parser._parse_blocks(block_text)

                if blocks:
                    root_block = blocks[0]

                    if section_name == "#links":
                        # Extract link items from this block
                        if journal_date:
                            for child in root_block.children:
                                link_item = parser._parse_link_item(child)
                                if link_item:
                                    filename, file_content = self.convert_link_item(
                                        link_item, journal_date
                                    )
                                    full_filename = f"Links/{filename}"
                                    extracted_files.append(
                                        (full_filename, file_content)
                                    )

                    elif section_name in {
                        "#learnings",
                        "#achievements",
                        "#highlights",
                    }:
                        # Handle content sections
                        if journal_date:
                            section_type = section_name.lstrip("#")
                            for child in root_block.children:
                                content_item = parser._parse_content_item(
                                    child, section_type
                                )
                                if content_item:
                                    filename, file_content = self.convert_content_item(
                                        content_item, journal_date
                                    )
                                    dir_name = section_type.capitalize()
                                    full_filename = f"{dir_name}/{filename}"
                                    extracted_files.append(
                                        (full_filename, file_content)
                                    )

                continue

            new_lines.append(line)
            i += 1

        return "\n".join(new_lines), extracted_files

    def _transform_properties(self, content: str) -> str:
        lines = content.split("\n")
        extracted_props = {}

        # Regex for key:: value
        prop_regex = re.compile(r"^\s*([a-zA-Z0-9_-]+)::\s*(.+)$")

        idx = 0
        # Extract properties from the top of the file
        while idx < len(lines):
            line = lines[idx]
            match = prop_regex.match(line)
            if match:
                key, value = match.groups()
                extracted_props[key] = value
                idx += 1
            elif line.strip() == "":
                idx += 1
            else:
                break

        if extracted_props:
            frontmatter = ["---"]
            for k, v in extracted_props.items():
                frontmatter.append(f"{k}: {v}")
            frontmatter.append("---\n")

            return "\n".join(frontmatter) + "\n" + "\n".join(lines[idx:])

        return content

    def _transform_block_ids(self, content: str) -> str:
        # id:: uuid -> ^uuid
        return re.sub(r"id::\s*([a-fA-F0-9-]{36})", r"^\1", content)

    def _transform_block_refs(self, content: str) -> str:
        # ((uuid)) -> [[file#^uuid]]

        def replace_ref(match):
            uuid = match.group(1)
            if self.scanner:
                file_path = self.scanner.get_file_for_block(uuid)
                if file_path:
                    filename = file_path.name
                    dest_name = self.transform_journal_filename(
                        filename
                    ) or self.transform_page_filename(filename)
                    link_path = dest_name.replace(".md", "")
                    return f"[[{link_path}#^{uuid}]]"

            return f"(({uuid}))"  # Keep original if not found

        return re.sub(r"\(\(([a-fA-F0-9-]{36})\)\)", replace_ref, content)

    def _transform_date_links(self, content: str) -> str:
        # [[Date]] -> [[Daily/YYYY-MM-DD]]

        def replace_date(match):
            link_text = match.group(1)
            # Try parsing date
            for fmt in ["%d %b %Y", "%b %d, %Y", "%Y-%m-%d", "%Y/%m/%d"]:
                try:
                    dt = datetime.strptime(link_text, fmt)
                    return f"[[Daily/{dt.strftime('%Y-%m-%d')}]]"
                except ValueError:
                    continue
            return match.group(0)

        return re.sub(r"\[\[(.*?)\]\]", replace_date, content)

    def convert_link_item(self, item: LinkItem, journal_date: date) -> Tuple[str, str]:
        """
        Converts a LinkItem to an Obsidian markdown file content.
        Returns (filename, content).
        """

        filename = f"{sanitize_filename(generate_content_filename(item.caption))}.md"

        frontmatter = [
            "---",
            f"url: {item.url}",
        ]
        if item.github_url:
            frontmatter.append(f"github_url: {item.github_url}")

        frontmatter.append(f"date: {journal_date.isoformat()}")
        frontmatter.append("---\n")

        content_lines = frontmatter
        content_lines.append(f"# {item.caption}\n")

        for sub in item.sub_items:
            content_lines.append(f"- {sub}")

        return filename, "\n".join(content_lines)

    def convert_content_item(
        self, item: ContentItem, journal_date: date
    ) -> Tuple[str, str]:
        """
        Converts a ContentItem to an Obsidian markdown file content.
        Returns (filename, content).
        """
        filename = (
            f"{sanitize_filename(generate_content_filename(item.description))}.md"
        )

        frontmatter = [
            "---",
            f"date: {journal_date.isoformat()}",
            "---\n",
        ]

        content_lines = frontmatter
        content_lines.append(f"{item.description}\n")

        for sub in item.sub_items:
            content_lines.append(f"- {sub}")

        return filename, "\n".join(content_lines)
