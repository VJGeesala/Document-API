# Document API

A production-grade REST API for storing and retrieving documents. Built with FastAPI, SQLAlchemy, and SQLite. Includes structured logging, API key authentication, automated tests, Docker support, and CI/CD via GitHub Actions.

This project is the foundation for a RAG (Retrieval-Augmented Generation) system — the document store will later be replaced with a vector database for semantic search.

---

## Features

- **REST API** — Full CRUD operations on documents
- **Authentication** — API key middleware on all endpoints
- **Structured Logging** — JSON logs with request IDs for tracing
- **Pagination** — Built-in for list endpoints
- **Input Validation** — Automatic via Pydantic
- **Health Checks** — `/health` and `/ready` endpoints
- **Tested** — 21 tests, 95% code coverage
- **Containerised** — Dockerfile + docker-compose
- **CI/CD** — GitHub Actions on every pull request

---

## Requirements

- Python 3.12+
- Docker Desktop (for containerised deployment)
- Git

---

## Quick Start (Local Development)

## Common Commands

This project includes a Makefile to simplify common tasks:

| Command          | Description                                  |
| ---------------- | -------------------------------------------- |
| `make help`      | List all available commands                  |
| `make setup`     | Create venv and install dependencies         |
| `make test`      | Run all tests                                |
| `make test-cov`  | Run tests with coverage report               |
| `make check`     | Run all quality checks (lint + types + test) |
| `make format`    | Auto-format code with black                  |
| `make up`        | Start services with docker-compose           |
| `make down`      | Stop services                                |
| `make logs`      | Tail container logs                          |
| `make clean`     | Remove venv, caches, and database files      |

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/document-api.git
cd document-api
```

### 2. Set up a virtual environment

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```
APP_ENV=development
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./documents.db
API_KEY=dev-key-12345
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

The API is now running at `http://localhost:8000`.

Interactive API documentation is available at `http://localhost:8000/docs`.

---

## Quick Start (Docker)

### 1. Build and run with docker-compose

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### 2. Stop the container

```bash
docker compose down
```

### 3. Build the image manually (optional)

```bash
docker build -t document-api:1.0.0 .
docker run -p 8000:8000 --env-file .env document-api:1.0.0
```

---

## API Endpoints

All endpoints (except `/health` and `/ready`) require the `X-API-Key` header.

### Health Checks

| Method | Endpoint  | Description                              |
| ------ | --------- | ---------------------------------------- |
| GET    | `/health` | Service health status                    |
| GET    | `/ready`  | Service readiness (database connection)  |

### Documents

| Method | Endpoint                    | Description                          |
| ------ | --------------------------- | ------------------------------------ |
| POST   | `/api/v1/documents`         | Create a new document                |
| GET    | `/api/v1/documents`         | List documents (paginated)           |
| GET    | `/api/v1/documents/{id}`    | Fetch one document                   |
| PUT    | `/api/v1/documents/{id}`    | Update a document                    |
| DELETE | `/api/v1/documents/{id}`    | Delete a document                    |

### Example Requests

**Create a document:**

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Doc", "content": "Hello from the Document API"}'
```

**List documents (paginated):**

```bash
curl -H "X-API-Key: dev-key-12345" \
  "http://localhost:8000/api/v1/documents?page=1&page_size=10"
```

**Get one document:**

```bash
curl -H "X-API-Key: dev-key-12345" \
  http://localhost:8000/api/v1/documents/{doc_id}
```

**Update a document:**

```bash
curl -X PUT http://localhost:8000/api/v1/documents/{doc_id} \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

**Delete a document:**

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/{doc_id} \
  -H "X-API-Key: dev-key-12345"
```

---

## Testing

### Run all tests

```bash
pytest tests/ -v
```

### Run tests with coverage report

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

Coverage must be above 80% — this is enforced by CI.

### Code quality checks

Before pushing, run all the checks CI will run:

```bash
black --check app/ tests/                      # Formatting
mypy app/ --ignore-missing-imports             # Type checking
pytest tests/ --cov=app --cov-fail-under=80    # Tests + coverage gate
```

Auto-format any unformatted files:

```bash
black app/ tests/
```

---

## Project Structure

```
document-api/
├── app/
│   ├── main.py                # Application entry point
│   ├── config.py              # Configuration loaded from environment
│   ├── database.py            # SQLAlchemy setup and models
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   └── documents.py       # Business logic (database operations)
│   ├── models/
│   │   └── schemas.py         # Pydantic request/response models
│   └── utils/
│       └── logging.py         # Structured JSON logging setup
├── tests/
│   ├── conftest.py            # Shared pytest fixtures
│   └── test_routes.py         # API endpoint tests
├── .github/
│   └── workflows/
│       └── test.yml           # GitHub Actions CI workflow
├── Dockerfile                 # Container build instructions
├── docker-compose.yml         # Local container orchestration
├── requirements.txt           # Python dependencies
├── .env.example               # Template for environment variables
├── .gitignore
├── .dockerignore
└── README.md
```

---

## Environment Variables

| Variable        | Description                          | Default                          |
| --------------- | ------------------------------------ | -------------------------------- |
| `APP_ENV`       | Environment name                     | `development`                    |
| `LOG_LEVEL`     | Logging verbosity                    | `INFO`                           |
| `DATABASE_URL`  | SQLAlchemy connection string         | `sqlite:///./documents.db`       |
| `API_KEY`       | API key for authentication           | _Required, no default_           |

For Docker deployments, the database path should be `sqlite:////app/data/documents.db` (four slashes — three for SQLAlchemy prefix, one for absolute path).

---

## CI/CD

This project uses GitHub Actions to automatically run quality checks on every pull request.

### What runs on each PR

1. **Code formatting** — `black --check`
2. **Type checking** — `mypy`
3. **Tests with coverage** — `pytest` (must pass with > 80% coverage)
4. **Docker build** — Verifies the image builds cleanly

### Branch protection

The `master` branch is protected:

- Direct pushes are blocked
- All changes must go through a pull request
- CI checks must pass before merging
- Pull requests require approval before merging

### Development workflow

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes and commit
git add .
git commit -m "Description of changes"

# 3. Push and open a PR
git push -u origin feature/your-feature-name

# 4. Open the PR on GitHub
# CI runs automatically; merge once green and approved
```

---

## Troubleshooting

### "unable to open database file" in Docker

The container user needs write permission to the data directory. Make sure `/app/data` exists with the correct ownership in your Dockerfile, and that you've created a local `data/` directory mounted as a volume.

### Tests failing with "datatype mismatch"

The database schema has changed. Delete `documents.db` and let it recreate:

```bash
rm documents.db
```

### CI not triggering on PR

The `.github/workflows/test.yml` file must exist on the feature branch, not just on `master`. Verify with:

```bash
git log --all --oneline -- .github/workflows/test.yml
```

### mypy errors after editing routes

When returning SQLAlchemy models from FastAPI endpoints, use `DocumentResponse.model_validate(doc)` to make the type conversion explicit.

---

## License

MIT

---

## Roadmap

This API is a foundation for further development as part of the Applied GenAI / LLM Engineer learning track:

- **Phase 1 (current)** — Document storage with CRUD operations
- **Phase 2** — Add embedding generation on document creation
- **Phase 3** — Replace SQLite with a vector database (Pinecone, Weaviate, or pgvector)
- **Phase 4** — Add semantic search and RAG query endpoints
- **Phase 5** — Add LLM-powered question answering