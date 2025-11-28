import re
from datetime import datetime
from typing import Optional

from logseq_converter.logseq.parser import BlockReferenceScanner


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
        
        extracted_files = []
        lines = content.split('\n')
        new_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            match = re.match(
                r"^-\s+(Achievements|Highlights|Learnings|Links)\s*$", line
            )
            if match:
                section_name = match.group(1)
                i += 1
                
                section_lines = []
                while i < len(lines):
                    child_line = lines[i]
                    # Check if next top-level block
                    if re.match(r"^-\s+", child_line):
                        break
                    section_lines.append(child_line)
                    i += 1
                
                self._process_section_items(
                    section_name, section_lines, original_filename, extracted_files
                )
                continue
            
            new_lines.append(line)
            i += 1
            
        return "\n".join(new_lines), extracted_files

    def _process_section_items(
        self,
        section_name: str,
        lines: list[str],
        original_filename: str,
        extracted_files: list,
    ):
        
        current_item_lines = []
        current_item_title = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check for item start (indentation + bullet)
            # Assume 2 spaces or tab for first level under section
            match = re.match(r"^\s+(?:-|\*)\s+(.+)$", line)
            if match:
                if current_item_title:
                    self._save_item(
                        section_name,
                        current_item_title,
                        current_item_lines,
                        original_filename,
                        extracted_files,
                    )
                
                current_item_title = match.group(1)
                current_item_lines = [line.strip()]
                i += 1
                
                # Capture all child lines (more indented)
                while i < len(lines):
                    next_line = lines[i]
                    # If it's more indented than the item, it's a child
                    if next_line.startswith("    ") or next_line.startswith("\t\t"):
                        current_item_lines.append(next_line.strip())
                        i += 1
                    else:
                        break
            else:
                i += 1
                    
        if current_item_title:
            self._save_item(
                section_name,
                current_item_title,
                current_item_lines,
                original_filename,
                extracted_files,
            )

    def _save_item(
        self,
        section_name: str,
        title: str,
        lines: list[str],
        original_filename: str,
        extracted_files: list,
    ):
        from logseq_converter.utils import sanitize_filename
        
        # Clean title for filename (remove block refs, links, etc if needed)
        # For now just sanitize
        safe_title = sanitize_filename(title)
        if not safe_title:
            safe_title = "Untitled"
            
        date_str = original_filename.replace(".md", "").replace("_", "-")
        
        filename = f"{section_name}/{date_str} - {safe_title}.md"
        content = "\n".join(lines)
        
        extracted_files.append((filename, content))

    def _transform_properties(self, content: str) -> str:
        lines = content.split('\n')
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
            
            return f"(({uuid}))" # Keep original if not found
            
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
