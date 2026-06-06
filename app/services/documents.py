import uuid
from sqlalchemy.orm import Session
from app.database import DocumentModel
from app.models.schemas import DocumentCreate, DocumentUpdate


def create_document(db: Session, data: DocumentCreate) -> DocumentModel:
    """Insert a new document into the database."""
    doc = DocumentModel(id=str(uuid.uuid4()), title=data.title, content=data.content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, doc_id: str) -> DocumentModel | None:
    """Fetch one document by ID. Returns None if not found."""
    return db.get(DocumentModel, doc_id)


def list_documents(
    db: Session, page: int = 1, page_size: int = 10
) -> tuple[list[DocumentModel], int]:
    """Return a paginated list of documents and total count."""
    offset = (page - 1) * page_size
    total = db.query(DocumentModel).count()
    items = (
        db.query(DocumentModel)
        .order_by(DocumentModel.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return items, total


def update_document(
    db: Session, doc_id: str, data: DocumentUpdate
) -> DocumentModel | None:
    """Update title and/or content. Returns None if not found."""
    doc = db.get(DocumentModel, doc_id)
    if not doc:
        return None
    if data.title is not None:
        doc.title = data.title
    if data.content is not None:
        doc.content = data.content
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc_id: str) -> bool:
    """Delete a document. Returns True if deleted, False if not found."""
    doc = db.get(DocumentModel, doc_id)
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True
