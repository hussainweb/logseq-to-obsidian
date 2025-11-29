from dataclasses import dataclass


@dataclass
class ConversionStats:
    journals: int = 0
    pages: int = 0
    assets: int = 0
    block_refs: int = 0
    links: int = 0
    learnings: int = 0
    achievements: int = 0
    highlights: int = 0
