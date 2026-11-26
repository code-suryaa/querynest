from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import answer_question
from app.services.vector_service import vector_store

router = APIRouter(prefix="/api", tags=["Query"])


@router.post("/query", response_model=QueryResponse)
def query_documents(payload: QueryRequest):
    if payload.doc_id and not vector_store.get_document(payload.doc_id):
        raise HTTPException(status_code=404, detail="Selected document not found.")

    if not vector_store.list_documents():
        raise HTTPException(
            status_code=400,
            detail="No documents uploaded yet. Please upload a PDF first.",
        )

    result = answer_question(
        question=payload.question,
        doc_id=payload.doc_id,
        top_k=payload.top_k,
    )
    return QueryResponse(**result)
