# Technical Specification (Implemented API/Gateway)

**Project:** Canonical Agent Workbench (CAW)  
**Doc status:** Current implementation reference  
**Last updated:** 2026-03-20

---

## 1) Runtime architecture

CAW is a FastAPI service that builds long-lived app services at startup:

- config loader (`CAWConfig`)
- SQLite database + migrations
- repositories (sessions/messages/traces/sources/evals/approvals)
- trace collector + replay engine
- provider registry
- skill registry
- orchestration engine
- permission gate + approval manager

All routes consume these shared services via dependency injection.

---

## 2) API envelope

Every HTTP endpoint returns:

```json
{
  "status": "ok",
  "data": {},
  "error_code": null,
  "message": null,
  "pagination": null
}
```

On handled domain failures, `status` is `"error"` with `error_code` and `message`.

---

## 3) Endpoint reference

## 3.1 Health

- `GET /api/v1/health`
  - Returns `{ "status": "healthy" }` in `data`.

## 3.2 Sessions + messages

- `POST /api/v1/sessions`
  - body: `{ mode, config_overrides?, skills?, skill_pack? }`
- `GET /api/v1/sessions?limit=50&mode=&state=`
- `GET /api/v1/sessions/{session_id}`
- `PATCH /api/v1/sessions/{session_id}`
  - body: `{ state?, config_overrides? }` (state transition supported)
- `POST /api/v1/sessions/{session_id}/branch`
  - body: `{ branch_point }`
- `DELETE /api/v1/sessions/{session_id}`
- `GET /api/v1/sessions/{session_id}/messages`
- `POST /api/v1/sessions/{session_id}/messages`
  - body: `{ content, provider?, model? }`
  - returns execution payload including `trace_id`.

## 3.3 Streaming

- `WS /api/v1/sessions/{session_id}/stream`
  - client -> server:
    - `{ "type": "message", "content": "..." }`
  - server -> client events:
    - `text`
    - `done`
    - `error`

## 3.4 Skills + providers

- `GET /api/v1/skills`
- `GET /api/v1/skills/{skill_id}`
- `GET /api/v1/skills/packs`
- `GET /api/v1/providers`
- `GET /api/v1/providers/{provider_id}/health`

## 3.5 Traces

- `GET /api/v1/traces/{trace_id}`
- `GET /api/v1/traces/{trace_id}/summary`

## 3.6 Research

Base prefix: `/api/v1/research`

- `POST /ingest` body: `{ session_id, path }`
- `POST /retrieve` body: `{ session_id, query, top_k=10 }`
- `POST /synthesize` body: `{ session_id, query, top_k=10 }`
- `POST /export` body: `{ session_id, query, format="markdown" }`

## 3.7 Deliberation

Base prefix: `/api/v1/deliberation`

- `POST /run`
  - body includes question, frame list, optional rounds + synthesis toggles.
- `GET /{deliberation_id}`
- `GET /{deliberation_id}/surface`

## 3.8 Workspace

Base prefix: `/api/v1/workspace`

- `POST /list`
- `POST /read`
- `POST /write`
- `POST /patch`
- `POST /patch/{patch_id}/apply`
- `POST /execute`

Note: `write` and `execute` can trigger approval-gated flows depending on workspace config.

## 3.9 Approvals

Base prefix: `/api/v1/approvals`

- `GET /pending`
- `POST /{request_id}` body: `{ approved, resolved_by="user", reason? }`

## 3.10 Evaluation

Base prefix: `/api/v1/eval`

- `POST /run`
- `GET /runs?task_id=...`
- `GET /runs/{run_id}`
- `POST /compare`
- `POST /regression`

---

## 4) Configuration contract

Config precedence (highest first):

1. runtime overrides
2. `CAW_*` env vars (`__` for nesting)
3. `~/.config/caw/config.toml`
4. `./config/local.toml` (legacy project override)
5. `./caw.toml`
6. `config/default.toml`

Major config sections:

- `[general]`
- `[storage]`
- `[providers.<id>]`
- `[routing]`
- `[skills]`
- `[workspace]`
- `[evaluation]`
- `[api]`

---

## 5) Workspace safety model

- `sandbox_mode`: `strict | permissive | none`
- `allowed_paths`: checked in strict mode
- `confirm_writes`, `confirm_deletes`, `confirm_executions`: can require explicit approval

When confirmation is required, operations may wait on the approval queue before completing.

---

## 6) Current limitations (important for GUI)

1. No built-in API authentication yet.
2. Some deliberation/workspace in-memory state is process-local (not multi-node durable).
3. WebSocket streaming currently emits coarse chunks, not token deltas.
4. Error payloads are envelope-based but not yet normalized to a formal RFC error schema.

---

## 7) GUI integration checklist

- Implement an API client with envelope unwrapping.
- Persist `session_id` and `trace_id` in client state.
- Add websocket reconnect + done/error handling.
- Add approval polling loop for workspace actions.
- Render trace summary for each operation.
- Surface provider health in settings UI.
