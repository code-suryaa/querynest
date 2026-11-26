import json
import math
import os
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

STORE_PATH = os.path.join("uploads", "store.json")

STOPWORDS = {
    "the", "is", "in", "at", "of", "on", "and", "a", "to", "for", "with",
    "as", "by", "an", "be", "this", "that", "it", "from", "or", "are",
    "was", "were", "can", "will", "what", "which", "who", "how", "when",
    "where", "why", "do", "does", "did", "about", "into", "their", "there",
    "have", "has", "had", "not", "but", "you", "your", "we", "our", "they",
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if len(w) > 1 and w not in STOPWORDS]


class LocalVectorStore:
    """Lightweight, zero-bloat TF-IDF vector store with JSON persistence."""

    def __init__(self, store_path: str = STORE_PATH):
        self.store_path = store_path
        self.data = {"documents": {}, "chunks": []}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.data = {"documents": {}, "chunks": []}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_document(
        self,
        doc_id: str,
        filename: str,
        file_path: str,
        total_pages: int,
        chunks: list[dict],
    ) -> None:
        self.data["documents"][doc_id] = {
            "doc_id": doc_id,
            "filename": filename,
            "file_path": file_path,
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

        for chunk in chunks:
            tokens = tokenize(chunk["text"])
            self.data["chunks"].append(
                {
                    "doc_id": doc_id,
                    "filename": filename,
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "term_counts": dict(Counter(tokens)),
                    "length": max(len(tokens), 1),
                }
            )

        self._save()

    def list_documents(self) -> list[dict]:
        docs = list(self.data["documents"].values())
        docs.sort(key=lambda d: d.get("uploaded_at", ""), reverse=True)
        return docs

    def get_document(self, doc_id: str) -> Optional[dict]:
        return self.data["documents"].get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        doc = self.data["documents"].pop(doc_id, None)
        if not doc:
            return False

        self.data["chunks"] = [
            c for c in self.data["chunks"] if c["doc_id"] != doc_id
        ]

        file_path = doc.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

        self._save()
        return True

    def search(
        self,
        query: str,
        doc_id: Optional[str] = None,
        top_k: int = 4,
    ) -> list[dict]:
        candidates = self.data["chunks"]
        if doc_id:
            candidates = [c for c in candidates if c["doc_id"] == doc_id]

        if not candidates:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        total_chunks = len(candidates)
        doc_freq = Counter()
        for chunk in candidates:
            for term in chunk["term_counts"].keys():
                doc_freq[term] += 1

        def idf(term: str) -> float:
            return math.log((1 + total_chunks) / (1 + doc_freq.get(term, 0))) + 1.0

        query_counts = Counter(query_tokens)
        query_vec = {
            t: (cnt / len(query_tokens)) * idf(t)
            for t, cnt in query_counts.items()
        }
        query_norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1.0

        scored = []
        for chunk in candidates:
            term_counts = chunk["term_counts"]
            chunk_len = chunk["length"]

            dot = 0.0
            for t, q_weight in query_vec.items():
                if t in term_counts:
                    c_weight = (term_counts[t] / chunk_len) * idf(t)
                    dot += q_weight * c_weight

            if dot <= 0:
                continue

            chunk_norm = math.sqrt(
                sum(
                    ((cnt / chunk_len) * idf(t)) ** 2
                    for t, cnt in term_counts.items()
                )
            ) or 1.0

            score = dot / (query_norm * chunk_norm)
            scored.append(
                {
                    "doc_id": chunk["doc_id"],
                    "filename": chunk["filename"],
                    "page": chunk["page"],
                    "text": chunk["text"],
                    "score": round(score, 4),
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


vector_store = LocalVectorStore()
