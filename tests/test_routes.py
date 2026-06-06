import pytest
from fastapi.testclient import TestClient

# ── Auth tests ─────────────────────────────────────────────────────────────


def test_no_api_key_returns_403(client):
    response = client.get("/api/v1/documents")
    assert response.status_code == 403


def test_wrong_api_key_returns_401(client):
    response = client.get("/api/v1/documents", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401


def test_valid_api_key_allowed(client, api_key_headers):
    response = client.get("/api/v1/documents", headers=api_key_headers)
    assert response.status_code == 200


# ── Health endpoints ────────────────────────────────────────────────────────


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready_check(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


# ── Create document ─────────────────────────────────────────────────────────


def test_create_document_success(client, api_key_headers):
    response = client.post(
        "/api/v1/documents",
        json={"title": "Test Title", "content": "Test content"},
        headers=api_key_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Title"
    assert data["content"] == "Test content"
    assert "id" in data
    assert "created_at" in data


def test_create_document_empty_title_rejected(client, api_key_headers):
    response = client.post(
        "/api/v1/documents",
        json={"title": "", "content": "Some content"},
        headers=api_key_headers,
    )
    assert response.status_code == 422


def test_create_document_missing_content_rejected(client, api_key_headers):
    response = client.post(
        "/api/v1/documents", json={"title": "A title"}, headers=api_key_headers
    )
    assert response.status_code == 422


def test_create_document_missing_title_rejected(client, api_key_headers):
    response = client.post(
        "/api/v1/documents", json={"content": "Some content"}, headers=api_key_headers
    )
    assert response.status_code == 422


# ── Get document ────────────────────────────────────────────────────────────


def test_get_document_success(client, api_key_headers, sample_document):
    doc_id = sample_document["id"]
    response = client.get(f"/api/v1/documents/{doc_id}", headers=api_key_headers)
    assert response.status_code == 200
    assert response.json()["id"] == doc_id


def test_get_document_not_found(client, api_key_headers):
    response = client.get("/api/v1/documents/nonexistent-id", headers=api_key_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ── List documents ──────────────────────────────────────────────────────────


def test_list_documents_empty(client, api_key_headers):
    response = client.get("/api/v1/documents", headers=api_key_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1


def test_list_documents_returns_created(client, api_key_headers, sample_document):
    response = client.get("/api/v1/documents", headers=api_key_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == sample_document["id"]


def test_list_documents_pagination(client, api_key_headers):
    # Create 3 documents
    for i in range(3):
        client.post(
            "/api/v1/documents",
            json={"title": f"Doc {i}", "content": f"Content {i}"},
            headers=api_key_headers,
        )

    # Page 1 with page_size=2
    response = client.get(
        "/api/v1/documents?page=1&page_size=2", headers=api_key_headers
    )
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["total_pages"] == 2


def test_list_documents_invalid_page_rejected(client, api_key_headers):
    response = client.get("/api/v1/documents?page=0", headers=api_key_headers)
    assert response.status_code == 422


# ── Update document ─────────────────────────────────────────────────────────


def test_update_document_title(client, api_key_headers, sample_document):
    doc_id = sample_document["id"]
    response = client.put(
        f"/api/v1/documents/{doc_id}",
        json={"title": "Updated Title"},
        headers=api_key_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["content"] == sample_document["content"]


def test_update_document_content(client, api_key_headers, sample_document):
    doc_id = sample_document["id"]
    response = client.put(
        f"/api/v1/documents/{doc_id}",
        json={"content": "Completely new content"},
        headers=api_key_headers,
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Completely new content"


def test_update_document_not_found(client, api_key_headers):
    response = client.put(
        "/api/v1/documents/nonexistent-id",
        json={"title": "New Title"},
        headers=api_key_headers,
    )
    assert response.status_code == 404


# ── Delete document ─────────────────────────────────────────────────────────


def test_delete_document_success(client, api_key_headers, sample_document):
    doc_id = sample_document["id"]
    response = client.delete(f"/api/v1/documents/{doc_id}", headers=api_key_headers)
    assert response.status_code == 200
    assert response.json()["deleted"] is True


def test_delete_document_gone_after_deletion(client, api_key_headers, sample_document):
    doc_id = sample_document["id"]
    client.delete(f"/api/v1/documents/{doc_id}", headers=api_key_headers)
    response = client.get(f"/api/v1/documents/{doc_id}", headers=api_key_headers)
    assert response.status_code == 404


def test_delete_document_not_found(client, api_key_headers):
    response = client.delete(
        "/api/v1/documents/nonexistent-id", headers=api_key_headers
    )
    assert response.status_code == 404
