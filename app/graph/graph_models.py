from typing import Literal, Optional, Any
from pydantic import BaseModel, Field


NodeType = Literal["party", "term_metric", "asset", "clause", "risk_finding", "evidence", "concept"]


class GraphNode(BaseModel):
    id: str
    label: str
    node_type: NodeType
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None
    section: Optional[str] = None
    quote: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)


class SerializedGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    links: list[GraphEdge] = Field(default_factory=list)
