import re
import time
import uuid
from typing import Dict, List, Set, Tuple, Union

from logseq_converter.logseq.models import Block, Journal, Page
from logseq_converter.tana.models import (
    TanaIntermediateFile,
    TanaIntermediateNode,
    TanaIntermediateSummary,
    TanaIntermediateSupertag,
)


class TanaConverter:
    """
    Converts LogSeq entities to Tana Intermediate Format.
    """

    def __init__(self):
        self.namespace = uuid.NAMESPACE_URL
        self.supertags: Dict[str, TanaIntermediateSupertag] = {}

    def _generate_uid(self, key: str, prefix: str = "") -> str:
        """Generate a consistent UID based on the key (e.g. page name or tag name)."""
        full_key = f"logseq:{prefix}:{key}"
        return str(uuid.uuid5(self.namespace, full_key))

    def _get_timestamp(self) -> int:
        """Current timestamp in milliseconds."""
        return int(time.time() * 1000)

    def _remove_properties(self, content: str, properties: Dict[str, str]) -> str:
        """Remove lines that are properties from the content."""
        if not properties:
            return content

        lines = content.split("\n")
        cleaned_lines = []
        for line in lines:
            is_property = False
            for key in properties:
                # LogSeq properties are usually "key:: value"
                # Check for key:: at start of line (ignoring whitespace)
                if line.strip().lower().startswith(f"{key.lower()}::"):
                    is_property = True
                    break
            if not is_property:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    def process_links(self, text: str) -> Tuple[str, List[str]]:
        """
        Find [[wiki-links]] and convert to Tana format [[uid]].
        Returns (cleaned_text, list_of_ref_uids).
        """
        # Find [[wiki-links]]
        # Tana format: [[uid]]
        # We replace [[Page Name]] with [[uid_of_page_name]]
        refs = []

        def replace_link(match):
            page_name = match.group(1)
            uid = self._generate_uid(page_name, "page")
            refs.append(uid)
            return f"[[{uid}]]"

        # Regex for [[Page Name]]
        cleaned_text = re.sub(r"\[\[(.*?)\]\]", replace_link, text)
        return cleaned_text, refs

    def process_tags(self, text: str) -> Tuple[str, List[str]]:
        """
        Find #tags and remove them from text.
        Returns (cleaned_text, list_of_tag_names).
        """
        # Find #tags
        # Remove from text and return list of tag names
        tags = []

        def replace_tag(match):
            tag_name = match.group(1)
            tags.append(tag_name)
            return ""

        # Regex for #tag (alphanumeric, underscores, hyphens)
        cleaned_text = re.sub(r"#([\w\-_]+)", replace_tag, text)
        # Clean up extra spaces left by tag removal
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        return cleaned_text, tags

    def convert_block(self, block: Block) -> TanaIntermediateNode:
        """Convert a LogSeq Block to a TanaIntermediateNode."""
        # Process content
        content = self._remove_properties(block.content, block.properties)

        # Handle properties
        # We only care about 'tags' property
        block_tags = []
        if "tags" in block.properties:
            # tags property is usually comma separated
            p_tags = block.properties["tags"].split(",")
            block_tags.extend([t.strip() for t in p_tags if t.strip()])

        # Process inline tags and links
        content, inline_tags = self.process_tags(content)
        content, refs = self.process_links(content)

        all_tags = block_tags + inline_tags
        supertags_uids = []

        for tag in all_tags:
            uid = self._generate_uid(tag, "tag")
            supertags_uids.append(uid)
            if tag not in self.supertags:
                self.supertags[tag] = TanaIntermediateSupertag(uid=uid, name=tag)

        # Create Node
        # Use block.id if available, else generate one
        if block.id:
            uid = block.id  # LogSeq block IDs are UUIDs usually
        else:
            uid = str(uuid.uuid4())

        node = TanaIntermediateNode(
            uid=uid,
            name=content,
            createdAt=self._get_timestamp(),
            editedAt=self._get_timestamp(),
            type="node",
            children=[self.convert_block(child) for child in block.children],
            refs=refs,
            supertags=supertags_uids,
        )

        return node

    def convert_page(self, page: Union[Page, Journal]) -> TanaIntermediateNode:
        """Convert a LogSeq Page or Journal to a TanaIntermediateNode."""
        page_name = page.filename.replace(".md", "")
        uid = self._generate_uid(page_name, "page")

        # Determine node type and name based on whether this is a journal
        node_type = "node"
        display_name = page_name

        # Handle journals as date nodes
        if isinstance(page, Journal):
            node_type = "date"
            # Format date as YYYY-MM-DD for Tana
            display_name = page.date.strftime("%Y-%m-%d")
        else:
            # Handle page hierarchy: convert triple underscores to forward slashes
            # LogSeq uses ___ in filenames which represent / in the page name
            display_name = page_name.replace("___", "/")

        # Page properties
        page_tags = []
        if hasattr(page, "properties") and "tags" in page.properties:
            p_tags = page.properties["tags"].split(",")
            page_tags.extend([t.strip() for t in p_tags if t.strip()])

        supertags_uids = []
        for tag in page_tags:
            uid_tag = self._generate_uid(tag, "tag")
            supertags_uids.append(uid_tag)
            if tag not in self.supertags:
                self.supertags[tag] = TanaIntermediateSupertag(uid=uid_tag, name=tag)

        node = TanaIntermediateNode(
            uid=uid,
            name=display_name,
            createdAt=self._get_timestamp(),
            editedAt=self._get_timestamp(),
            type=node_type,
            children=[self.convert_block(block) for block in page.blocks],
            supertags=supertags_uids,
        )

        return node

    def _collect_supertag_uids(self, node: TanaIntermediateNode) -> Set[str]:
        uids = set(node.supertags)
        for child in node.children:
            uids.update(self._collect_supertag_uids(child))
        return uids

    def _count_descendants(self, node: TanaIntermediateNode) -> int:
        count = 0
        for child in node.children:
            count += 1 + self._count_descendants(child)
        return count

    def _count_leaf_nodes(self, node: TanaIntermediateNode) -> int:
        if not node.children:
            return 1
        count = 0
        for child in node.children:
            count += self._count_leaf_nodes(child)
        return count

    def create_tana_file(self, node: TanaIntermediateNode) -> TanaIntermediateFile:
        """Create a TanaIntermediateFile from a root node, including summary and used supertags."""
        return self.create_tana_file_from_nodes([node])

    def _count_calendar_nodes(self, node: TanaIntermediateNode) -> int:
        """Count nodes with type='date' in the tree."""
        count = 1 if node.type == "date" else 0
        for child in node.children:
            count += self._count_calendar_nodes(child)
        return count

    def create_tana_file_from_nodes(self, nodes: List[TanaIntermediateNode]) -> TanaIntermediateFile:
        """Create a TanaIntermediateFile from a list of root nodes, including summary and used supertags."""
        # Collect supertags used in these nodes
        used_uids = set()
        for node in nodes:
            used_uids.update(self._collect_supertag_uids(node))

        used_supertags = [tag for tag in self.supertags.values() if tag.uid in used_uids]

        # Identify root level pages for homeNodeIds
        # Root level pages are those whose names do not contain "/" AND are not date nodes
        home_node_ids = []
        for node in nodes:
            if "/" not in node.name and node.type != "date":
                home_node_ids.append(node.uid)

        # Calculate summary
        total_nodes = 0
        leaf_nodes = 0
        calendar_nodes = 0
        for node in nodes:
            total_nodes += 1 + self._count_descendants(node)
            leaf_nodes += self._count_leaf_nodes(node)
            calendar_nodes += self._count_calendar_nodes(node)

        summary = TanaIntermediateSummary(
            leafNodes=leaf_nodes,
            topLevelNodes=len(nodes),
            totalNodes=total_nodes,
            calendarNodes=calendar_nodes,
            fields=0,
            brokenRefs=0,
        )

        return TanaIntermediateFile(
            summary=summary,
            nodes=nodes,
            supertags=used_supertags,
            homeNodeIds=home_node_ids,
        )
