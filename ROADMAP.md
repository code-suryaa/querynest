# QueryNest Roadmap

## Phase 1 — Core MVP (Completed)
- [x] FastAPI backend & project architecture
- [x] PDF upload validation & page-wise text extraction (`pypdf`)
- [x] Page-aware overlapping text chunking
- [x] Persistent local TF-IDF search & retrieval store
- [x] `/api/query` endpoint with Gemini AI RAG + extractive fallback
- [x] Dark-mode frontend UI with document switcher & page citations
- [x] Basic `pytest` API test suite

## Phase 2 — Next Upgrades
- [ ] OCR support for scanned/image-based PDFs
- [ ] Dense vector embeddings (ChromaDB / FAISS / Gemini Embeddings)
- [ ] Multi-turn chat memory per document
- [ ] Highlighted PDF viewer side-by-side with citations
- [ ] Deployment on Render / Railway
