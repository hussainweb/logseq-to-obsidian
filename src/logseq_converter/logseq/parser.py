import re
from pathlib import Path
from typing import Dict, Optional, Union

from logseq_converter.logseq.models import Journal, Page


class BlockReferenceScanner:
    def __init__(self):
        self.block_map: Dict[str, Path] = {} # id -> file_path

    def scan_file(self, file_path: Path) -> None:
        """
        Scans a file for block IDs (id:: uuid) and updates the map.
        """
        if not file_path.exists():
            return
            
        with open(file_path, 'r', encoding='utf-8') as f:
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
        
        # TODO: Implement full parsing logic to populate models
        
        return None
