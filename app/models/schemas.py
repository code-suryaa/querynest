from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    ai_mode: str


class PagePreview(BaseModel):
    page: int
    preview: str


class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    total_pages: int
    total_chunks: int
    pages_preview: List[PagePreview]
    message: str


class DocumentSummary(BaseModel):
    doc_id: str
    filename: str
    total_pages: int
    total_chunks: int
    uploaded_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentSummary]


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    doc_id: Optional[str] = Field(
        default=None,
        description="Optional document ID to restrict search to a single PDF.",
    )
    top_k: int = Field(default=4, ge=1, le=8)


class SourceCitation(BaseModel):
    doc_id: str
    filename: str
    page: int
    snippet: str
    score: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation]
    mode: str
