import re
import urllib.parse
from typing import Dict, Tuple


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
        content_lines = []
        
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
            properties["type"] = "project"
            if len(parts) >= 3:
                properties["area"] = parts[1]
                base_name = parts[-1]
            elif len(parts) == 2:
                base_name = parts[1]
        
        elif base_name.startswith("learnings___"):
            parts = base_name.split("___")
            properties["type"] = "learning"
            base_name = parts[-1]
            
        elif base_name.startswith("Lists___"):
            parts = base_name.split("___")
            properties["type"] = "list"
            base_name = parts[-1]
            
        elif base_name.startswith("Axelerant___"):
            parts = base_name.split("___")
            properties["type"] = "work"
            properties["client"] = "Axelerant"
            base_name = parts[-1]
            
        elif base_name.startswith("Meetings___"):
            parts = base_name.split("___")
            properties["type"] = "meeting"
            if len(parts) >= 3:
                properties["meeting-type"] = parts[1]
                base_name = parts[-1]
            elif len(parts) == 2:
                base_name = parts[1]
                
        elif base_name.startswith("Devices___"):
            parts = base_name.split("___")
            properties["type"] = "device"
            base_name = parts[-1]
            
        elif base_name.startswith("Servers___"):
            parts = base_name.split("___")
            properties["type"] = "server"
            base_name = parts[-1]
            
        elif base_name.startswith("Upkeep___"):
            parts = base_name.split("___")
            properties["type"] = "upkeep"
            base_name = parts[-1]
            
        elif base_name.startswith("content-creation___"):
            parts = base_name.split("___")
            properties["type"] = "content-creation"
            base_name = parts[-1]
            
        elif base_name.startswith("Restaurants___"):
            parts = base_name.split("___")
            properties["type"] = "restaurant"
            base_name = parts[-1]
            
        elif base_name.startswith("prompt-templates___"):
            parts = base_name.split("___")
            properties["type"] = "prompt-template"
            base_name = parts[-1]
            
        elif base_name.startswith("Books___"):
            parts = base_name.split("___")
            properties["type"] = "book"
            base_name = parts[-1]
            
        else:
            # Handle remaining hierarchies gracefully, convert to hyphen
            base_name = base_name.replace("___", " - ")

        # Decode URI encoding
        final_filename = self.decode_filename(base_name) + ".md"
        # Sanitize filename if needed (replace slashes just in case)
        final_filename = final_filename.replace("/", " - ")

        # Build YAML Frontmatter
        frontmatter = []
        if properties:
            frontmatter.append("---")
            for k, v in properties.items():
                frontmatter.append(f"{k}: {v}")
            frontmatter.append("---")
            
        final_content = "\n".join(frontmatter) + "\n\n" + remaining_content.strip()
        
        # Remove remaining block IDs and block refs if necessary, 
        # or just leave them. Tolaria works with Markdown. Let's do a basic cleanup for id::
        final_content = re.sub(r"id::\s*([a-fA-F0-9-]{36})\n?", "", final_content)
        
        return final_filename, final_content

    def transform_journal_filename(self, filename: str) -> str:
        """
        Transforms LogSeq journal filename (YYYY_MM_DD.md) to Tolaria format (YYYY-MM-DD.md).
        """
        match = re.match(r"(\d{4})_(\d{2})_(\d{2})\.md", filename)
        if match:
            year, month, day = match.groups()
            return f"{year}-{month}-{day}.md"
        return filename
