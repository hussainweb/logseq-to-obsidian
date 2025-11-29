from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Block:
    content: str
    id: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)
    children: List["Block"] = field(default_factory=list)


@dataclass
class Page:
    filename: str
    content: str
    blocks: List[Block] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class Journal:
    filename: str
    date: date
    content: str
    blocks: List[Block] = field(default_factory=list)


@dataclass
class Asset:
    filename: str
    path: Path


@dataclass
class Graph:
    source_path: Path
    destination_path: Path
    pages: List[Page] = field(default_factory=list)
    journals: List[Journal] = field(default_factory=list)
    assets: List[Asset] = field(default_factory=list)


@dataclass
class LinkItem:
    caption: str
    url: str
    github_url: Optional[str] = None
    sub_items: List[str] = field(default_factory=list)


@dataclass
class ContentItem:
    type: str  # 'learning', 'achievement', 'highlight'
    description: str
    sub_items: List[str] = field(default_factory=list)
