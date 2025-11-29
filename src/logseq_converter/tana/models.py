from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class TanaSupertagRef(BaseModel):
    id: str


class TanaNode(BaseModel):
    name: str
    description: Optional[str] = None
    supertags: Optional[List[TanaSupertagRef]] = None
    children: Optional[List[Union["TanaNode", "TanaField"]]] = None


class TanaField(BaseModel):
    type: Literal["field"] = "field"
    attributeId: str
    children: List[TanaNode]


class TanaAPIPayload(BaseModel):
    targetNodeId: str
    nodes: List[TanaNode] = Field(max_length=100)


TanaNode.model_rebuild()
