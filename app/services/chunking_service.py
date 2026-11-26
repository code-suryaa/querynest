def chunk_pages(
    pages: list[dict],
    chunk_size: int = 800,
    overlap: int = 150,
) -> list[dict]:
    """Split extracted PDF pages into overlapping chunks while keeping page numbers."""
    chunks = []
    chunk_idx = 0

    for item in pages:
        page_num = item["page"]
        text = item["text"].strip()
        if not text:
            continue

        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)

            # Avoid cutting mid-word when possible
            if end < text_len:
                last_space = text.rfind(" ", start, end)
                if last_space > start + int(chunk_size * 0.6):
                    end = last_space

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    {
                        "chunk_id": chunk_idx,
                        "page": page_num,
                        "text": chunk_text,
                    }
                )
                chunk_idx += 1

            if end >= text_len:
                break

            start = max(end - overlap, start + 1)

    return chunks
