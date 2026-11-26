import os
from typing import Optional
from app.services.vector_service import vector_store


def is_gemini_configured() -> bool:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return bool(key and key != "your_gemini_api_key_here")


def _build_extractive_answer(question: str, matches: list[dict]) -> str:
    """Fallback answer when GEMINI_API_KEY is not set."""
    top = matches[0]
    lines = [
        f"Based on the uploaded document ({top['filename']}, Page {top['page']}), "
        f"here is the most relevant excerpt for your question:",
        "",
        f'"{top["text"][:450].strip()}..."' if len(top["text"]) > 450 else f'"{top["text"].strip()}"',
    ]
    if len(matches) > 1:
        other_pages = sorted({f"{m['filename']} (Page {m['page']})" for m in matches[1:]})
        lines.append("")
        lines.append("Additional related references: " + ", ".join(other_pages) + ".")

    lines.append("")
    lines.append("(Tip: Add GEMINI_API_KEY in .env to enable full AI-generated answers.)")
    return "\n".join(lines)


def _generate_gemini_answer(question: str, matches: list[dict]) -> str:
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    client = genai.Client(api_key=api_key)

    context_blocks = []
    for idx, m in enumerate(matches, start=1):
        context_blocks.append(
            f"[Source {idx} | File: {m['filename']} | Page {m['page']}]\n{m['text']}"
        )

    context_text = "\n\n".join(context_blocks)
    prompt = f"""You are QueryNest, a document intelligence assistant.
Answer the user's question strictly using the provided document excerpts below.
- Cite page numbers inline like [Page 3] whenever you state a fact.
- Be clear, concise, and direct.
- If the excerpts do not contain enough information to answer, clearly say: "I couldn't find this information in the uploaded document(s)."

Document Excerpts:
{context_text}

User Question:
{question}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    return (response.text or "").strip() or "No answer could be generated."


def answer_question(
    question: str,
    doc_id: Optional[str] = None,
    top_k: int = 4,
) -> dict:
    matches = vector_store.search(query=question, doc_id=doc_id, top_k=top_k)

    if not matches:
        return {
            "question": question,
            "answer": "I couldn't find relevant information in the uploaded PDF(s) for that question. Try rephrasing or uploading a relevant document.",
            "sources": [],
            "mode": "gemini" if is_gemini_configured() else "extractive-fallback",
        }

    sources = [
        {
            "doc_id": m["doc_id"],
            "filename": m["filename"],
            "page": m["page"],
            "snippet": m["text"][:280].strip() + ("..." if len(m["text"]) > 280 else ""),
            "score": m["score"],
        }
        for m in matches
    ]

    if is_gemini_configured():
        try:
            answer = _generate_gemini_answer(question, matches)
            mode = "gemini"
        except Exception as exc:
            answer = (
                _build_extractive_answer(question, matches)
                + f"\n\n[Gemini fallback triggered: {exc}]"
            )
            mode = "extractive-fallback"
    else:
        answer = _build_extractive_answer(question, matches)
        mode = "extractive-fallback"

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "mode": mode,
    }
