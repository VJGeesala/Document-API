import uuid
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.config import config
from app.database import get_db
from app.models.schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    PagedResponse,
)
from app.services.documents import (
    create_document,
    get_document,
    list_documents,
    update_document,
    delete_document,
)
from app.utils.logging import request_id_var

router = APIRouter(prefix="/api/v1", tags=["documents"])
logger = logging.getLogger(__name__)

# Auth
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(key: str = Depends(api_key_header)) -> str:
    if key != config.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key

# Endpoints
@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def create(
    data: DocumentCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
) -> DocumentResponse:
    start = time.time()
    doc = create_document(db, data)
    logger.info("document_created", extra={"extra_fields": {
        "doc_id": doc.id,
        "title": doc.title,
        "latency_ms": round((time.time() - start) * 1000, 2)
    }})
    return doc

@router.get("/documents", response_model=PagedResponse)
async def list_all(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
) -> PagedResponse:
    items, total = list_documents(db, page=page, page_size=page_size)
    return PagedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=-(-total // page_size)
    )

@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_one(
    doc_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
) -> DocumentResponse:
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    return doc

@router.put("/documents/{doc_id}", response_model=DocumentResponse)
async def update(
    doc_id: str,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
) -> DocumentResponse:
    doc = update_document(db, doc_id, data)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    return doc

@router.delete("/documents/{doc_id}")
async def delete(
    doc_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
) -> dict:
    deleted = delete_document(db, doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    logger.info("document_deleted", extra={"extra_fields": {"doc_id": doc_id}})
    return {"deleted": True, "id": doc_id}