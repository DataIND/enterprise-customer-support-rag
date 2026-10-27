# Runbook

## Local startup

```bash
cp .env.example .env
# edit secrets and LLM key
docker compose up --build
alembic upgrade head   # if not run by startup
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Common operations

### Issue a development token

```bash
curl -s -X POST http://localhost:8000/api/v1/chat/token \
  -H 'Content-Type: application/json' \
  -d '{"role":"agent"}'
```

### Upload a document

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F file=@./knowledge/faq.txt
```

### Ask a question

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"question":"How do I reset my password?"}'
```

## Failure triage

| Symptom | Check |
|---|---|
| `/health` down | API container logs; port mapping |
| Document stuck `pending` | Celery worker + Redis connectivity |
| Document `failed` | `documents.error_message`; file type support |
| Empty / abstained answers | Ingestion `ready`; similarity threshold; embeddings |
| DB errors on migrate | PostgreSQL up; `vector` extension available |

## Migrations

```bash
alembic upgrade head
alembic downgrade -1
```

## Safe secrets handling

- Never commit `.env`
- Rotate `JWT_SECRET_KEY` and `LLM_API_KEY` if exposed
- Use distinct credentials per environment
