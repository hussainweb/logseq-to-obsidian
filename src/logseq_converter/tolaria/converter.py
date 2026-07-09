import re
import urllib.parse
from datetime import date, datetime
from typing import Dict, Optional, Tuple

from logseq_converter.logseq.models import ContentItem, LinkItem
from logseq_converter.logseq.parser import BlockReferenceScanner, LogSeqParser


class TolariaConverter:
    # Pages to completely ignore
    IGNORE_EXACT = {
        "Readwise.md",
        "author.md",
        "category.md",
        "url.md",
        "full-title.md",
        "contents.md",
    }
    
    IGNORE_PREFIXES = (
        "articles___Highlights___",
        "books___Highlights___",
        "podcasts___Highlights___",
        "tweets___Highlights___",
        "hls__",
    )

    def __init__(
        self,
        scanner: Optional[BlockReferenceScanner] = None,
        env: Optional[dict[str, str]] = None,
    ):
        self.scanner = scanner
        self.stats_block_refs = 0
        self.stats_links = 0
        self.stats_learnings = 0
        self.stats_achievements = 0
        self.stats_highlights = 0
        from logseq_converter.llm import LLMFilenameGenerator
        self.llm_generator = LLMFilenameGenerator(env=env or {})

    def should_ignore(self, filename: str) -> bool:
        if filename in self.IGNORE_EXACT:
            return True
        if filename.startswith(self.IGNORE_PREFIXES):
            return True
        return False

    def decode_filename(self, filename: str) -> str:
        return urllib.parse.unquote(filename)

    def extract_and_remove_frontmatter(self, content: str) -> Tuple[str, Dict[str, str]]:
        """
        Extracts existing YAML frontmatter and key:: value LogSeq properties 
        from the content, returning the remaining content and a dict of properties.
        """
        lines = content.split("\n")
        properties = {}
        
        idx = 0
        # Parse YAML Frontmatter
        if lines and lines[0].strip() == "---":
            idx = 1
            while idx < len(lines):
                line = lines[idx]
                if line.strip() == "---":
                    idx += 1
                    break
                
                # Match yaml key: value
                yaml_match = re.match(r"^\s*([a-zA-Z0-9_-]+):\s*(.*)$", line)
                if yaml_match:
                    key = yaml_match.group(1)
                    val = yaml_match.group(2).strip("'\"")
                    properties[key] = val
                idx += 1

        # Parse LogSeq key:: value properties at the top of the remaining content
        while idx < len(lines):
            line = lines[idx]
            prop_match = re.match(r"^\s*([a-zA-Z0-9_-]+)::\s*(.+)$", line)
            if prop_match:
                key = prop_match.group(1)
                val = prop_match.group(2).strip()
                properties[key] = val
                idx += 1
            elif not line.strip():
                # Skip empty lines at the top
                idx += 1
            else:
                break
                
        # The rest is content
        content_lines = lines[idx:]
        
        return "\n".join(content_lines), properties

    def transform_page_filename(self, filename: str) -> str:
        """
        Transforms Logseq page filename to the final Tolaria page filename (without .md).
        """
        base_name = filename
        if base_name.endswith(".md"):
            base_name = base_name[:-3]
            
        if base_name.startswith("projects___"):
            parts = base_name.split("___")
            if len(parts) >= 3:
                base_name = parts[-1]
            elif len(parts) == 2:
                base_name = parts[1]
        elif base_name.startswith("learnings___"):
            base_name = base_name.split("___")[-1]
        elif base_name.startswith("Lists___"):
            base_name = base_name.split("___")[-1]
        elif base_name.startswith("Axelerant___"):
            base_name = base_name.split("___")[-1]
        elif base_name.startswith("Meetings___"):
            parts = base_name.split("___")
            if len(parts) >= 3:
                base_name = parts[-1]
            elif len(parts) == 2:
                base_name = parts[1]
        elif base_name.startswith("Devices___"):
            base_name = base_name.split("___")[-1]
        elif base_name.startswith("Servers___"):
            base_name = base_name.split("___")[-1]
        elif base_name.startswith("Upkeep___"):
            base_name = base_name.split("___")[-1]
        elif base_name.startswith("content-creation___"):
            base_name = base_name.split("___")[-1]
        elif base_name.startswith("Restaurants___"):
            base_name = base_name.split("___")[-1]
        elif base_name.startswith("prompt-templates___"):
            base_name = base_name.split("___")[-1]
        elif base_name.startswith("Books___"):
            base_name = base_name.split("___")[-1]
        else:
            base_name = base_name.replace("___", " - ")

        final_name = self.decode_filename(base_name)
        final_name = final_name.replace("/", " - ")
        return final_name

    def transform_journal_filename(self, filename: str) -> str:
        """
        Transforms LogSeq journal filename (YYYY_MM_DD.md) to Tolaria format (YYYY-MM-DD.md).
        """
        match = re.match(r"(\d{4})_(\d{2})_(\d{2})\.md", filename)
        if match:
            year, month, day = match.groups()
            return f"{year}-{month}-{day}.md"
        return filename

    def remove_logbook(self, content: str) -> str:
        return re.sub(r":LOGBOOK:.*?:END:", "", content, flags=re.DOTALL)

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
                    self.stats_block_refs += 1
                    filename = file_path.name
                    match_journal = re.match(r"(\d{4})_(\d{2})_(\d{2})\.md", filename)
                    if match_journal:
                        year, month, day = match_journal.groups()
                        link_path = f"journal/{year}-{month}-{day}"
                    else:
                        link_path = self.transform_page_filename(filename)
                    return f"[[{link_path}#^{uuid}]]"
            return f"(({uuid}))"

        return re.sub(r"\(\(([a-fA-F0-9-]{36})\)\)", replace_ref, content)

    def _transform_date_links(self, content: str) -> str:
        # [[Date]] -> [[journal/YYYY-MM-DD]]
        def replace_date(match):
            link_text = match.group(1)
            for fmt in ["%d %b %Y", "%b %d, %Y", "%Y-%m-%d", "%Y/%m/%d"]:
                try:
                    dt = datetime.strptime(link_text, fmt)
                    return f"[[journal/{dt.strftime('%Y-%m-%d')}]]"
                except ValueError:
                    continue
            return match.group(0)

        return re.sub(r"\[\[(.*?)\]\]", replace_date, content)

    def convert_content(self, content: str) -> str:
        try:
            content = self.remove_logbook(content)
            content = self._transform_block_ids(content)
            content = self._transform_block_refs(content)
            content = self._transform_date_links(content)
            return content
        except Exception as e:
            from logseq_converter.utils import log_warning
            log_warning(f"Error converting content: {e}. Returning original content.")
            return content

    def process_metadata(self, filename: str, content: str) -> Tuple[str, str]:
        """
        Parses filename to extract type and properties, merges with existing properties,
        and returns the new filename and updated content with YAML frontmatter.
        """
        base_name = filename
        if base_name.endswith(".md"):
            base_name = base_name[:-3]
            
        remaining_content, properties = self.extract_and_remove_frontmatter(content)
        
        # Mappings based on Logseq conventions
        if base_name.startswith("projects___"):
            parts = base_name.split("___")
            properties["type"] = "Project"
            if len(parts) >= 3:
                properties["area"] = parts[1]
                base_name = parts[-1]
            elif len(parts) == 2:
                base_name = parts[1]
        
        elif base_name.startswith("learnings___"):
            parts = base_name.split("___")
            properties["type"] = "Learning"
            base_name = parts[-1]
            
        elif base_name.startswith("Lists___"):
            parts = base_name.split("___")
            properties["type"] = "List"
            base_name = parts[-1]
            
        elif base_name.startswith("Axelerant___"):
            parts = base_name.split("___")
            properties["type"] = "Work"
            properties["client"] = "Axelerant"
            base_name = parts[-1]
            
        elif base_name.startswith("Meetings___"):
            parts = base_name.split("___")
            properties["type"] = "Meeting"
            if len(parts) >= 3:
                properties["meeting-type"] = parts[1]
                base_name = parts[-1]
            elif len(parts) == 2:
                base_name = parts[1]
                
        elif base_name.startswith("Devices___"):
            parts = base_name.split("___")
            properties["type"] = "Device"
            base_name = parts[-1]
            
        elif base_name.startswith("Servers___"):
            parts = base_name.split("___")
            properties["type"] = "Server"
            base_name = parts[-1]
            
        elif base_name.startswith("Upkeep___"):
            parts = base_name.split("___")
            properties["type"] = "Upkeep"
            base_name = parts[-1]
            
        elif base_name.startswith("content-creation___"):
            parts = base_name.split("___")
            properties["type"] = "Content Creation"
            base_name = parts[-1]
            
        elif base_name.startswith("Restaurants___"):
            parts = base_name.split("___")
            properties["type"] = "Restaurant"
            base_name = parts[-1]
            
        elif base_name.startswith("prompt-templates___"):
            parts = base_name.split("___")
            properties["type"] = "Prompt Template"
            base_name = parts[-1]
            
        elif base_name.startswith("Books___"):
            parts = base_name.split("___")
            properties["type"] = "Book"
            base_name = parts[-1]
            
        else:
            # Handle remaining hierarchies gracefully, convert to hyphen
            base_name = base_name.replace("___", " - ")

        # Decode URI encoding
        final_filename = self.decode_filename(base_name) + ".md"
        # Sanitize filename if needed (replace slashes just in case)
        final_filename = final_filename.replace("/", " - ")

        # Convert remaining_content body
        transformed_body = self.convert_content(remaining_content)

        # Build YAML Frontmatter
        frontmatter = []
        if properties:
            frontmatter.append("---")
            for k, v in properties.items():
                frontmatter.append(f"{k}: {v}")
            frontmatter.append("---")
            
        final_content = "\n".join(frontmatter) + "\n\n" + transformed_body.strip()
        
        return final_filename, final_content

    def extract_sections(self, content: str, original_filename: str) -> tuple[str, list[tuple[str, str]]]:
        """
        Extracts specific sections from journal entries.
        Returns (modified_content, list_of_extracted_files).
        """
        extracted_files = []
        lines = content.split("\n")
        new_lines = []

        parser = LogSeqParser()
        from logseq_converter.utils import parse_journal_date
        journal_date = parse_journal_date(original_filename)

        i = 0
        while i < len(lines):
            line = lines[i]
            section_match = self._match_section_header(line)

            if section_match:
                section_name = section_match.group(2).lower()
                initial_indent = len(line) - len(line.lstrip())

                # Capture section lines
                section_lines, next_idx = self._capture_section_lines(lines, i, initial_indent)
                i = next_idx

                # Process the captured section
                new_extracted = self._process_section_content(section_lines, section_name, journal_date, parser)
                extracted_files.extend(new_extracted)
                continue

            new_lines.append(line)
            i += 1

        return "\n".join(new_lines), extracted_files

    def _match_section_header(self, line: str) -> Optional[re.Match]:
        """Check if line is a section header."""
        return re.match(
            r"^(?:-\s+)?(#{1,6}\s+)?(#links|#learnings|#achievements|#highlights)\s*$",
            line,
            re.IGNORECASE,
        )

    def _capture_section_lines(self, lines: list[str], start_idx: int, initial_indent: int) -> tuple[list[str], int]:
        """
        Captures lines belonging to a section starting at start_idx.
        Returns (captured_lines, next_line_index).
        """
        section_lines = [lines[start_idx]]
        i = start_idx + 1

        while i < len(lines):
            line = lines[i]

            # Empty lines are part of the section
            if not line.strip():
                section_lines.append(line)
                i += 1
                continue

            current_indent = len(line) - len(line.lstrip())

            # Check for heading boundaries
            # If we started with a heading (initial_indent == 0 and starts with #),
            # we stop at the next heading.
            is_root_heading = initial_indent == 0 and re.match(r"^#{1,6}\s+", lines[start_idx])
            if is_root_heading:
                if re.match(r"^#{1,6}\s+", line):
                    break
                section_lines.append(line)
                i += 1
                continue

            # Check for list item boundaries
            # Stop if we find a new list item at same or lower indentation level
            is_new_block = re.match(r"^(-|\*)\s+", line) and current_indent <= initial_indent

            if is_new_block:
                break

            section_lines.append(line)
            i += 1

        return section_lines, i

    def _process_section_content(
        self,
        section_lines: list[str],
        section_name: str,
        journal_date: Optional[date],
        parser: "LogSeqParser",
    ) -> list[tuple[str, str]]:
        """
        Parses and converts content from a captured section.
        """
        if not journal_date:
            return []

        extracted = []
        block_text = "\n".join(section_lines)
        blocks = parser._parse_blocks(block_text)

        if not blocks:
            return []

        # Determine content blocks
        if re.match(r"^#{1,6}\s+", blocks[0].cleaned_content):
            content_blocks = blocks[1:]
        else:
            content_blocks = blocks[0].children

        if section_name == "#links":
            items = self._extract_link_items(content_blocks, journal_date, parser)
            self.stats_links += len(items)
            extracted.extend(items)
        elif section_name in {"#learnings", "#achievements", "#highlights"}:
            section_type = section_name.lstrip("#")
            items = self._extract_content_items(content_blocks, section_type, journal_date, parser)
            if section_name == "#learnings":
                self.stats_learnings += len(items)
            elif section_name == "#achievements":
                self.stats_achievements += len(items)
            elif section_name == "#highlights":
                self.stats_highlights += len(items)
            extracted.extend(items)

        return extracted

    def _extract_link_items(self, blocks: list, journal_date: date, parser: "LogSeqParser") -> list[tuple[str, str]]:
        results = []
        from logseq_converter.utils import is_markdown_empty

        for child in blocks:
            link_item = parser._parse_link_item(child)
            if link_item:
                filename, file_content = self.convert_link_item(link_item, journal_date)
                if not is_markdown_empty(file_content):
                    results.append((filename, file_content))
        return results

    def _extract_content_items(
        self,
        blocks: list,
        section_type: str,
        journal_date: date,
        parser: "LogSeqParser",
    ) -> list[tuple[str, str]]:
        results = []
        from logseq_converter.utils import is_markdown_empty

        for child in blocks:
            content_item = parser._parse_content_item(child, section_type)
            if content_item:
                filename, file_content = self.convert_content_item(content_item, journal_date)
                if not is_markdown_empty(file_content):
                    results.append((filename, file_content))
        return results

    def convert_link_item(self, item: LinkItem, journal_date: date) -> Tuple[str, str]:
        """
        Converts a LinkItem to Tolaria markdown file content.
        """
        from logseq_converter.utils import generate_content_filename, sanitize_filename

        filename = f"{sanitize_filename(generate_content_filename(item.caption))}.md"

        frontmatter = [
            "---",
            "type: Link",
            f"url: {item.url}",
        ]
        if item.github_url:
            frontmatter.append(f"github_url: {item.github_url}")

        frontmatter.append(f"date: {journal_date.isoformat()}")
        frontmatter.append("---")

        content_lines = frontmatter
        content_lines.append(f"\n# {item.caption}\n")

        transformed_original = self.convert_content(item.original_content)
        content_lines.append(f"- {transformed_original}")

        for sub in item.sub_items:
            transformed_sub = self.convert_content(sub)
            content_lines.append(f"  {transformed_sub}")

        return filename, "\n".join(content_lines)

    def convert_content_item(self, item: ContentItem, journal_date: date) -> Tuple[str, str]:
        """
        Converts a ContentItem to Tolaria markdown file content.
        """
        from logseq_converter.utils import generate_content_filename, sanitize_filename

        fallback_name = sanitize_filename(generate_content_filename(item.description))

        if self.llm_generator and self.llm_generator.provider != "none":
            checksum = self.llm_generator.get_content_hash(item.description, item.sub_items)
            if checksum in self.llm_generator.cache:
                filename = f"{self.llm_generator.cache[checksum]}.md"
            else:
                filename = f"__PENDING_LLM__{checksum}__{fallback_name}.md"
        else:
            filename = f"{fallback_name}.md"

        t_type = item.type
        if t_type.endswith("s"):
            t_type = t_type[:-1]

        type_mapping = {
            "learning": "Learning",
            "achievement": "Achievement",
            "highlight": "Highlight",
        }
        mapped_type = type_mapping.get(t_type, t_type.capitalize())

        frontmatter = [
            "---",
            f"type: {mapped_type}",
            f"date: {journal_date.isoformat()}",
            "---",
        ]

        content_lines = frontmatter
        transformed_desc = self.convert_content(item.description)
        content_lines.append(f"\n{transformed_desc}\n")

        for sub in item.sub_items:
            transformed_sub = self.convert_content(sub)
            content_lines.append(f"{transformed_sub}")

        return filename, "\n".join(content_lines)
