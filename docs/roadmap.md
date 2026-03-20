# Delivery Roadmap (Post-Implementation, GUI-Oriented)

**Date:** 2026-03-20  
**Scope:** Prioritized work for GUI client integration + backend hardening.

---

## Milestone A — GUI contract stabilization

### A1. Publish frozen OpenAPI snapshot
- Export and version OpenAPI schema.
- Add schema diff check in CI.

### A2. Formalize envelope/error schema
- Standardize error `code`, `message`, `details`, recoverability hint.
- Document per-endpoint error codes.

### A3. WebSocket event schema v1
- Define typed event contracts (`text`, `done`, `error`, future `delta`).
- Add reconnect guidance and idempotency notes.

### A4. Pagination normalization
- Add cursor-based pagination to list-heavy endpoints where needed.

**Exit criteria:** GUI can codegen client models and rely on contract stability.

---

## Milestone B — Security baseline for non-local usage

### B1. API authentication middleware
- Bearer token support for all HTTP endpoints.
- Matching auth for WebSocket upgrade.

### B2. Rate limiting
- Global and per-session limits.

### B3. Host exposure guardrails
- Safe defaults for non-loopback binds.

### B4. Security docs + operator setup
- Key generation/rotation procedures.

**Exit criteria:** server safe for controlled network exposure.

---

## Milestone C — GUI feature completion

### C1. Session + chat UI
- session list/detail/create/branch/delete
- chat timeline with message metadata

### C2. Trace explorer
- event timeline, summary panel, provider/tool call filters

### C3. Research workbench
- ingest panel
- retrieval results viewer
- synthesis claim/citation browser
- export artifact links

### C4. Deliberation studio
- frame composer
- rounds controls
- disagreement surface rendering

### C5. Workspace + approvals
- file browser + editor
- patch preview/apply
- command execution console
- approvals inbox with approve/deny flow

### C6. Evaluation dashboard
- run launch
- run history
- compare matrix
- regression report view

**Exit criteria:** GUI covers all major capability endpoints with operator-safe UX.

---

## Milestone D — Reliability and scale-up

### D1. Persist currently in-memory API state
- deliberation run cache
- workspace patch proposal cache

### D2. Background job support for long-running tasks
- queue + status endpoints for synthesis/evaluation jobs.

### D3. Structured observability
- metrics + structured logs aligned with trace ids.

### D4. Performance passes
- large-response handling and compression
- query optimization for traces and eval runs

**Exit criteria:** stable behavior under prolonged and heavy GUI-driven usage.
