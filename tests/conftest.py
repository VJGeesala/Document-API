import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite for tests — fast and disposable
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine once for the whole session."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Give each test a clean database session, rolled back after."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Test client wired to the test database."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def api_key_headers():
    """Valid API key headers — reads from config so it works in any environment."""
    from app.config import config

    return {"X-API-Key": config.api_key}


@pytest.fixture
def sample_document(client, api_key_headers):
    """Create one document and return it — reusable across tests."""
    response = client.post(
        "/api/v1/documents",
        json={"title": "Sample Doc", "content": "Sample content for testing"},
        headers=api_key_headers,
    )
    return response.json()
