from pypdf import PdfReader


def extract_text(file_path: str) -> list[dict]:
    """Extract non-empty text page-by-page from a PDF file."""
    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        cleaned = " ".join(text.split())
        if cleaned:
            pages.append(
                {
                    "page": page_number,
                    "text": cleaned,
                }
            )

    return pages
