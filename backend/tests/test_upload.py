from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rejects_unsupported_file_type():
    response = client.post(
        "/documents", files={"file": ("virus.exe", b"abc", "application/octet-stream")}
    )
    assert response.status_code == 415