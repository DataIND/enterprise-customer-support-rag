# Architecture

## Summary

The Enterprise Customer Support RAG Assistant is a multi-tenant FastAPI service that retrieves knowledge-base chunks from PostgreSQL (pgvector) and generates grounded answers via an OpenAI-compatible LLM provider. Document ingestion runs asynchronously through Celery and Redis.

## Components

| Component | Responsibility |
|---|---|
| FastAPI app | HTTP API, validation, auth/RBAC |
| RAG service | Embed query, retrieve, prompt, generate / abstain |
| Document service | Upload validation, metadata, enqueue ingestion |
| Celery worker | Parse, chunk, embed, persist chunks |
| PostgreSQL + pgvector | Metadata and vector similarity search |
| Redis | Celery broker and result backend |
| LLM / embedding adapters | Provider-agnostic HTTP clients |

## Request paths

### Ask a question

1. Client authenticates with a JWT containing `tenant_id` and `role`.
2. `POST /api/v1/query` accepts the question.
3. The query is embedded; top-k tenant-scoped chunks are retrieved.
4. If no chunks pass the similarity threshold, the system abstains.
5. Otherwise the LLM generates an answer from retrieved context and source references are returned.

### Document ingestion

1. Authenticated agent/admin uploads a document.
2. Metadata is stored with status `pending`; the file is written to storage.
3. Celery task `ingest_document` parses, chunks, embeds, and stores vectors.
4. Status transitions: `pending` → `processing` → `ready` | `failed`.

## Tenant isolation

Every document and chunk row includes `tenant_id`. Retrieval and document reads filter by the authenticated tenant. Application-level filtering is the baseline; PostgreSQL Row-Level Security is a recommended hardening step for stronger threat models.

## Design notes

- Retrieved document content is treated as untrusted input (prompt-injection awareness).
- The JWT auth endpoint is a development reference; production should use a managed IdP / JWKS.
- Embedding dimensions must match the configured embedding model and migration schema.
