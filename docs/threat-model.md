# Threat Model

## Assets

- Customer questions and generated answers
- Knowledge-base documents and embeddings
- Tenant boundaries and access tokens
- LLM API keys and service credentials

## Trust boundaries

| Boundary | Notes |
|---|---|
| Client → API | Authenticated over HTTPS in production |
| API → Database | Least-privilege DB credentials |
| API / Worker → LLM provider | External network; secrets in env/secret manager |
| Worker → Object/file storage | Uploaded files may contain malicious content |

## Key threats and mitigations

| Threat | Mitigation |
|---|---|
| Cross-tenant data leakage | Mandatory `tenant_id` filters; consider RLS |
| Prompt injection via documents | System prompt treats context as data; abstain when weak evidence |
| Unauthorized privileged actions | JWT + RBAC (`admin`, `agent`, `viewer`) |
| Malicious uploads | Extension allowlist, size limits, sandboxed parsing |
| Secret exposure in logs | Never log tokens, API keys, or full PII payloads |
| Cost / DoS via LLM calls | Rate limits, timeouts, quotas (production hardening) |
| Weak JWT secret | Strong secret / managed IdP in production |

## Out of scope (starter)

- Full IdP federation
- Database-enforced RLS
- Formal penetration test attestation

Revisit this document before production deployment.
