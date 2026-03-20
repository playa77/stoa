# CAW API/Gateway — Start Here for GUI Client Development

This document is the **implementation handoff** for a GUI client being built against the current CAW backend.

If you only read one file, read this one first.

---

## 1) What is stable today

- The backend is a FastAPI application mounted under `/api/v1` with a consistent response envelope:
  - `status` (`"ok"` or `"error"`)
  - `data` (payload)
  - optional `error_code`, `message`, `pagination`
- Core surfaces are implemented and covered by unit/integration tests:
  - sessions + chat
  - websocket streaming
  - research
  - deliberation
  - workspace operations
  - approvals
  - traces
  - evaluation
  - skills/providers discovery
- The API currently has **no built-in auth middleware**. Treat this as local/dev-only unless you put it behind your own auth gateway.

---

## 2) Build-order recommendation for the GUI

1. **Session shell + health check**
   - `GET /api/v1/health`
   - `POST /api/v1/sessions`
   - `GET /api/v1/sessions/{session_id}`
2. **Chat panel (HTTP first)**
   - `POST /api/v1/sessions/{session_id}/messages`
   - `GET /api/v1/sessions/{session_id}/messages`
3. **Live streaming (WebSocket)**
   - `WS /api/v1/sessions/{session_id}/stream`
4. **Trace viewer**
   - `GET /api/v1/traces/{trace_id}`
   - `GET /api/v1/traces/{trace_id}/summary`
5. **Approvals drawer**
   - `GET /api/v1/approvals/pending`
   - `POST /api/v1/approvals/{request_id}`
6. **Capability tabs**
   - Research, Deliberation, Workspace, Evaluation, Skills/Providers.

This order gives you fast end-to-end usability and makes debugging easier.

---

## 3) Contract rules the GUI should assume

- Always parse the response envelope first (`status`, then `data`).
- Never assume non-null `data` on errors.
- For errors, show `error_code` when present (important for operator troubleshooting).
- Persist `session_id` and `trace_id` aggressively in your client state:
  - `session_id` = conversation/workflow context
  - `trace_id` = audit/debug link
- Workspace writes/executions may block waiting for approval; implement a pending state and poll approvals.

---

## 4) WebSocket behavior (chat stream)

Endpoint: `ws://<host>/api/v1/sessions/{session_id}/stream`

Client sends:
```json
{"type":"message","content":"hello"}
```

Server emits sequence:
- one or more `{"type":"text","content":"..."}` events
- final `{"type":"done","trace_id":"..."}` event
- on failure: `{"type":"error","error_code":"...","message":"..."}`

The current implementation sends a complete text chunk then done (not token-by-token yet).

---

## 5) Critical UX notes

- **Approval loop is mandatory** for safe workspace UX:
  - Show pending requests in a dedicated panel.
  - Let user approve/deny with reason.
  - Reflect resulting success/failure in originating action.
- **Research + Deliberation can return large payloads**; use virtualized views and collapsible sections.
- **Provider/model selectors** should be optional; backend has defaults.

---

## 6) Read next

1. `docs/quickstart.md` — run instructions and first API calls.
2. `docs/tech_spec.md` — endpoint-by-endpoint contract details.
3. `docs/security_roadmap.md` — required hardening before broad deployment.
4. `docs/roadmap.md` — practical backlog focused on GUI-client enablement.
