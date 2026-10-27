# Contributing

Thanks for improving the Enterprise Customer Support RAG Assistant.

## Development setup

1. Copy `.env.example` to `.env` and set local secrets (never commit real credentials).
2. Prefer Docker Compose for PostgreSQL (pgvector) and Redis:

   ```bash
   docker compose up --build
   ```

3. For local Python development:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   alembic upgrade head
   uvicorn app.main:app --reload
   celery -A app.tasks.celery_app.celery_app worker --loglevel=INFO
   ```

## Tests

```bash
pytest -q
```

Keep unit tests free of production credentials and customer data. Integration tests that need PostgreSQL/Redis should use Compose services or CI fixtures.

## Coding guidelines

- Enforce tenant isolation on every document, chunk, and retrieval path.
- Prefer small, focused PRs with clear rationale.
- Update `docs/` when architecture, threats, or operations change.
- Do not log API keys, JWTs, or sensitive customer content.

## Pull requests

- Describe the problem and the approach.
- Note any new environment variables.
- Include test coverage for new behavior when practical.
