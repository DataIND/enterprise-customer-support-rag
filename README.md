# Enterprise Customer Support RAG Assistant

An AI-powered customer support assistant that uses **Retrieval-Augmented Generation (RAG)** to answer customer questions using trusted knowledge-base documents. Built with Python and FastAPI, the project demonstrates backend engineering, LLM integration, asynchronous processing, tenant isolation, and production-oriented system design.

## Overview

Traditional customer support systems often require customers to search documentation manually or wait for support agents. This project uses semantic retrieval and a Large Language Model (LLM) to generate context-aware answers grounded in relevant knowledge-base content.

The assistant retrieves relevant document chunks, supplies them as context to the LLM, and returns an answer with source references. When sufficient evidence is unavailable, the system should abstain rather than invent an answer.

## Key Features

- **Retrieval-Augmented Generation:** Retrieve relevant knowledge-base content before generating answers.
- **REST API:** FastAPI endpoints with request validation and OpenAPI documentation.
- **Document ingestion:** Upload and process knowledge-base documents asynchronously.
- **Semantic search:** PostgreSQL with pgvector for vector similarity search.
- **Background processing:** Celery and Redis for asynchronous ingestion tasks.
- **Authentication:** JWT-based authentication reference implementation.
- **Tenant isolation:** Scope document access and retrieval to the authenticated tenant.
- **Access control:** Role-based access control for protected operations.
- **LLM integration:** Provider abstraction for language-model integration.
- **Containerization:** Docker and Docker Compose development environment.
- **Automated testing:** Pytest-based tests and CI workflow.
- **Operational documentation:** Architecture, threat model, runbook, and RAG evaluation guidance.

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python |
| API framework | FastAPI |
| Data validation | Pydantic |
| Database | PostgreSQL |
| Vector search | pgvector |
| ORM and migrations | SQLAlchemy, Alembic |
| Background jobs | Celery |
| Message broker / cache | Redis |
| LLM integration | OpenAI-compatible provider adapter |
| Authentication | JWT reference implementation |
| Containers | Docker, Docker Compose |
| Testing | Pytest |
| CI | GitHub Actions |

## Architecture

```text
                    Client / Support Agent
                              |
                              v
                     FastAPI Application
                              |
                  Authentication / RBAC
                              |
                              v
                    Customer Query API
                              |
                              v
                       RAG Service
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
          Embedding / Retrieval      LLM Provider
                  |                       ^
                  v                       |
          PostgreSQL + pgvector           |
                  |                       |
                  +---- Retrieved Context-+
                              |
                              v
                    Answer + Source References


        Document Upload API
                |
                v
        PostgreSQL Metadata
                |
                v
        Celery Background Worker <---- Redis
                |
                v
        Parse / Chunk / Embed
                |
                v
        PostgreSQL + pgvector
```

## Project Structure

```text
enterprise-customer-support-rag/
├── app/
│   ├── api/              # API routes and request handling
│   ├── core/             # Configuration and security
│   ├── db/               # Database setup and models
│   ├── rag/              # Retrieval and answer generation
│   ├── services/         # Business logic and integrations
│   └── tasks/            # Background processing
├── alembic/              # Database migrations
├── docs/
│   ├── architecture.md
│   ├── threat-model.md
│   ├── runbook.md
│   └── rag-evaluation.md
├── tests/                # Automated tests
├── .github/workflows/    # CI configuration
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── CONTRIBUTING.md
└── README.md
```

*The directory names above describe the intended organization; adjust them to match the actual files in your repository.*

## Getting Started

### Prerequisites

- Python 3.11 or a compatible version specified by the project configuration
- Docker and Docker Compose
- PostgreSQL with the pgvector extension
- Redis
- An API key for the configured LLM provider

### 1. Clone the repository

```bash
git clone https://github.com/DataIND/enterprise-customer-support-rag.git
cd enterprise-customer-support-rag
```


### 2. Configure environment variables

```bash
cp .env.example .env
```

Update `.env` with the required database, Redis, authentication, and LLM provider settings. Use strong secrets and never commit real credentials.

### 3. Start the services

```bash
docker compose up --build
```

Check the Compose configuration and required environment variables before starting the application.

### 4. Apply database migrations

If migrations are not automatically applied by the configured startup process, run the migration command in the application environment:

```bash
alembic upgrade head
```

Ensure PostgreSQL is ready and the database has the required extensions before running migrations.

### 5. Access the API

When the application is running locally, the FastAPI documentation is typically available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health endpoint: `http://localhost:8000/health`

Confirm the actual routes and exposed ports in the application configuration.

## Typical RAG Workflow

1. Authenticate the user and identify the tenant.
2. Upload a knowledge-base document.
3. Create document metadata and schedule ingestion.
4. Extract text and split it into overlapping chunks.
5. Generate embeddings for each chunk.
6. Store chunks, embeddings, and metadata in PostgreSQL with pgvector.
7. Accept a customer question.
8. Embed the question and retrieve relevant chunks within the tenant's permitted scope.
9. Build a prompt using the retrieved context and question.
10. Generate an answer using the configured LLM.
11. Return the answer and source references.
12. Evaluate retrieval quality, groundedness, latency, and cost.

## Example API Workflow

The exact endpoints depend on the implementation. A typical workflow includes:

| Operation | Purpose |
|---|---|
| Authentication | Obtain credentials or a token |
| Document upload | Add knowledge-base content |
| Ingestion status | Track document processing |
| Ask a question | Retrieve context and generate an answer |
| Health check | Check application health |

Use the Swagger UI to inspect the actual endpoint paths, request schemas, and authentication requirements.

## Configuration

Use `.env.example` as the source of truth for supported configuration variables.

Typical configuration categories include:

- Application environment and log level
- Database connection
- Redis and Celery
- LLM provider and API key
- Embedding model
- Chunk size and chunk overlap
- Retrieval top-k and similarity threshold
- JWT settings

Do not assume every setting listed above is implemented. Verify the variables supported by the current code before deployment.

## Testing

Install the project and its development dependencies using the commands supported by `pyproject.toml`. For example:

```bash
pip install -e ".[dev]"
pytest -q
```

If the project does not define a `dev` extra, install the development dependencies using the method specified in its configuration.

Integration tests may require PostgreSQL, pgvector, Redis, and test credentials. Do not use production credentials or production customer data in tests.

## Security Considerations

Security controls to implement and verify before production deployment include:

- Enforce tenant isolation for every document, chunk, and retrieval query.
- Validate uploaded file types, file sizes, and content.
- Keep secrets in a secret manager or secure deployment environment.
- Use a managed identity provider or validated JWT/JWKS configuration in production.
- Apply rate limits, request timeouts, and resource limits.
- Protect against prompt injection and malicious instructions in retrieved documents.
- Treat retrieved document content as untrusted input.
- Avoid logging API keys, access tokens, or sensitive customer information.
- Apply least-privilege database and service credentials.
- Define retention and deletion policies for documents, embeddings, and conversation data.
- Audit privileged operations and monitor failures.

Application-level tenant filtering is not equivalent to database-enforced isolation. Consider PostgreSQL Row-Level Security (RLS) or stronger database isolation where the threat model requires it.

## Production Readiness

This repository is intended as a **production-oriented engineering starter**, not a claim of production certification.

Before deploying to real customers, validate:

- Database migrations and rollback procedures
- Concurrent document ingestion and idempotency
- Reliable job delivery and retry behavior
- Transactional consistency between database writes and background jobs
- Tenant-isolation tests and authorization boundaries
- Retrieval thresholds and answer-grounding evaluation
- Prompt-injection defenses and output validation
- Rate limiting, quotas, and cost controls
- Structured logs, metrics, traces, and alerting
- Load, failure-recovery, and security testing
- Backup, restore, retention, and disaster-recovery procedures

Review `docs/` for the architecture, threat model, operational runbook, and RAG evaluation guidance.

## Future Enhancements

- Hybrid retrieval combining vector and keyword search
- Reranking with a dedicated reranker
- Document versioning and incremental re-indexing
- Streaming responses
- Conversation history with tenant-aware access control
- Human handoff to a support agent
- Feedback collection and answer-quality analytics
- RAG evaluation datasets and regression tests
- OpenTelemetry tracing and operational dashboards
- PostgreSQL Row-Level Security
- Transactional outbox for reliable ingestion scheduling
- Support for multiple LLM and embedding providers

## Contributing

Contributions are welcome. Please read `CONTRIBUTING.md`, create a focused branch, add or update tests, and run the test suite before opening a pull request.

## License

Choose a license before publishing this repository. If you intend to make the project open source, add a `LICENSE` file containing the license you select.

## Author

**Akash Jadhav**

Senior Python Backend Engineer | GenAI & RAG | FastAPI | LLM Applications | System Design

GitHub: `https://github.com/DataIND`

LinkedIn: `https://www.linkedin.com/in/akash-jadhav-087666b6/`
