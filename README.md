# QueryNest — Turn Documents into Answers

QueryNest is a lightweight, full-stack Document Intelligence platform built with **FastAPI**, **Python**, and **Vanilla HTML/CSS/JS**. Upload any PDF, ask questions in natural language, and get context-aware answers backed by exact **page references**.

## Features
- **PDF Upload & Page-Wise Extraction**: Validates PDFs, extracts text page-by-page using `pypdf`.
- **Smart Overlapping Chunking**: Preserves page numbers across chunks for accurate citations.
- **Fast Local Search + Gemini RAG**: Works immediately out-of-the-box with built-in TF-IDF retrieval, and upgrades automatically to **Gemini AI** answers when `GEMINI_API_KEY` is added to `.env`.
- **Clean Web UI + Swagger Docs**: Built-in dark-mode frontend served directly by FastAPI, plus interactive API docs at `/docs`.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional, recommended) Add your Gemini API key
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY

# 3. Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:
- **App UI**: `http://localhost:8000`
- **API Swagger Docs**: `http://localhost:8000/docs`

## Run Tests
```bash
pytest
```

## API Endpoints
- `GET /health` — Server status & active AI mode
- `POST /api/documents/upload` — Upload and index a PDF
- `GET /api/documents` — List indexed documents
- `DELETE /api/documents/{doc_id}` — Delete a document
- `POST /api/query` — Ask a question and get an answer with page citations
