from dataclasses import dataclass, field
from typing import List, Literal, Optional

NodeType = Literal["field", "image", "codeblock", "node", "date"]
FlagType = Literal["section"]
ViewType = Literal["list", "table"]
DataType = Literal["any", "url", "email", "number", "date", "checkbox"]
TodoState = Literal["todo", "done"]


@dataclass
class TanaIntermediateSummary:
    """Summary of the Tana Intermediate File contents."""

    leafNodes: int
    topLevelNodes: int
    totalNodes: int
    calendarNodes: int
    fields: int
    brokenRefs: int


@dataclass
class TanaIntermediateAttribute:
    """Definition of a Tana attribute (field)."""

    name: str
    values: List[str]
    count: int
    dataType: Optional[DataType] = "any"


@dataclass
class TanaIntermediateSupertag:
    """Definition of a Tana supertag."""

    uid: str
    name: str


@dataclass
class TanaIntermediateNode:
    """Represents a node in the Tana Intermediate Format."""

    uid: str
    name: str
    createdAt: int
    editedAt: int
    type: NodeType = "node"
    description: Optional[str] = None
    children: List["TanaIntermediateNode"] = field(default_factory=list)
    refs: List[str] = field(default_factory=list)
    mediaUrl: Optional[str] = None
    codeLanguage: Optional[str] = None
    supertags: List[str] = field(default_factory=list)
    flags: List[FlagType] = field(default_factory=list)
    viewType: Optional[ViewType] = None
    todoState: Optional[TodoState] = None


@dataclass
class TanaIntermediateFile:
    """Root object for the Tana Intermediate Format file."""

    summary: TanaIntermediateSummary
    nodes: List[TanaIntermediateNode]
    version: str = "TanaIntermediateFile V0.1"
    homeNodeIds: List[str] = field(default_factory=list)
    attributes: List[TanaIntermediateAttribute] = field(default_factory=list)
    supertags: List[TanaIntermediateSupertag] = field(default_factory=list)
