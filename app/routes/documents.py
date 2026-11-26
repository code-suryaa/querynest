import os
import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.models.schemas import (
    DocumentListResponse,
    DocumentSummary,
    DocumentUploadResponse,
    PagePreview,
)
from app.services.chunking_service import chunk_pages
from app.services.pdf_service import extract_text
from app.services.vector_service import vector_store

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF (.pdf) files are supported.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum allowed size is 15 MB.",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    doc_id = uuid.uuid4().hex[:10]
    safe_name = os.path.basename(file.filename)
    saved_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{safe_name}")

    with open(saved_path, "wb") as f:
        f.write(content)

    try:
        pages = extract_text(saved_path)
    except Exception as exc:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read PDF: {exc}",
        ) from exc

    if not pages:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=400,
            detail="No selectable text found in this PDF (scanned image PDFs are not supported yet).",
        )

    chunks = chunk_pages(pages)
    vector_store.add_document(
        doc_id=doc_id,
        filename=safe_name,
        file_path=saved_path,
        total_pages=len(pages),
        chunks=chunks,
    )

    previews = [
        PagePreview(
            page=p["page"],
            preview=p["text"][:160] + ("..." if len(p["text"]) > 160 else ""),
        )
        for p in pages[:3]
    ]

    return DocumentUploadResponse(
        doc_id=doc_id,
        filename=safe_name,
        total_pages=len(pages),
        total_chunks=len(chunks),
        pages_preview=previews,
        message="PDF uploaded, extracted, and indexed successfully.",
    )


@router.get("", response_model=DocumentListResponse)
def list_documents():
    docs = [DocumentSummary(**d) for d in vector_store.list_documents()]
    return DocumentListResponse(documents=docs)


@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    deleted = vector_store.delete_document(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"status": "deleted", "doc_id": doc_id}
