from datetime import datetime
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """Shape of the request body when creating a document."""

    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)


class DocumentUpdate(BaseModel):
    """Shape of the request body when updating a document."""

    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = None


class DocumentResponse(BaseModel):
    """Shape of the response when returning a document."""

    id: str
    title: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}  # Allows converting from SQLAlchemy model


class PagedResponse(BaseModel):
    """Shape for paginated list responses."""

    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
