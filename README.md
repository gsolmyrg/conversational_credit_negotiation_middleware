# Conversational Credit Negotiation — Middleware

FastAPI service that exposes the [conversational negotiation flow](https://github.com/gsolmyrg/conversational_credit_negotiation_flow) over authenticated HTTP endpoints and bridges it to a WhatsApp messaging channel.

> Reference implementation. No client data, credentials, or production configuration is included; all secrets are read from the environment.

## What it demonstrates

**A boundary between the agent and the channel.** The LLM flow does not know what WhatsApp is, and the messaging channel does not know what an agent is. The middleware owns that translation, which is what keeps either side replaceable.

**Authentication at the edge.** Every endpoint depends on `verify_api_key`, which extracts a bearer token and compares it against an environment-provided key. Nothing reaches the agent without passing that check.

**Typed request contracts.** `DebtNegotiationRequestBody` and `WhatsappRequestBody` are Pydantic models, so malformed payloads fail at the boundary with a clear error instead of surfacing as a confusing agent failure three layers in.

**Structured logging around every agent invocation.** Entry, success and failure are all logged with the serialized payload. In LLM systems the request and the response *are* the audit trail — without them, a bad answer in production is unreproducible.

**A health endpoint that answers GET and HEAD.** Small detail, but it is what lets a load balancer or uptime monitor probe the service correctly.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` / `HEAD` | `/` | Health check |
| `POST` | `/start-negotiation` | Starts a negotiation from a persona and financial profile |
| `POST` | `/messages-upsert` | Receives inbound WhatsApp messages and continues the conversation |

Both `POST` endpoints require `Authorization: Bearer <UVICORN_API_KEY>`.

## Layout

```
main.py        FastAPI app, auth dependency, routes
models.py      request body contracts
services.py    MessageSubmissionService - orchestrates flow invocation
clients/       outbound integrations
```

## Stack

Python · FastAPI · Uvicorn · Pydantic · [uv](https://docs.astral.sh/uv/)

## Running it

```bash
pip install uv
uv sync
cp .env.example .env   # set UVICORN_API_KEY, UVICORN_HOST, UVICORN_PORT
uv run python main.py
```

## Author

**Guilherme Candeloro Padilha** — AI Solutions Architect
[LinkedIn](https://www.linkedin.com/in/guilherme-candeloro-72113426b) · guilherme@aiveon.com
