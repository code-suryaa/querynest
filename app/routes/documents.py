
import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import extract_text

router = APIRouter()

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 10 MB limit."
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )

    file_id = str(uuid.uuid4())
    saved_filename = f"{file_id}.pdf"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    pages = extract_text(file_path)


    return {
        "message": "Document uploaded successfully",
        "file_id": file_id,
        "filename": file.filename,
        "status": "uploaded"
        "total_pages": len(pages),
        "extracted_pages": len(pages),
    }
