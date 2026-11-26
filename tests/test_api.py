from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["app"] == "QueryNest"


def test_reject_non_pdf_upload():
    files = {"file": ("notes.txt", b"hello world", "text/plain")}
    res = client.post("/api/documents/upload", files=files)
    assert res.status_code == 400
    assert "Only PDF" in res.json()["detail"]


def test_list_documents_endpoint():
    res = client.get("/api/documents")
    assert res.status_code == 200
    assert "documents" in res.json()
