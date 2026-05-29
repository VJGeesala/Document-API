from datetime import datetime
from sqlalchemy import create_engine, String, Text
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column
from app.config import config

# Create the database engine
engine = create_engine(
    config.database_url,
    connect_args={"check_same_thread": False},
)

class Base(DeclarativeBase):
    pass

class DocumentModel(Base):
    """Database table for documents."""
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

def create_tables():
    """Create the database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Yield a database session, always close it after use."""
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()