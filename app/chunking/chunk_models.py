from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    page_number: int
    text: str
    section: str | None = None
    metadata: dict = Field(default_factory=dict)