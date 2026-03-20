# Security Roadmap (Current-State Aligned)

**Date:** 2026-03-20  
**Status:** Required before broad deployment

---

## 1) Current security posture

The API/gateway currently runs well for local trusted development, but has key gaps for exposed environments:

1. No built-in authentication on HTTP routes.
2. No built-in authentication on WebSocket stream endpoint.
3. No request rate limiting.
4. Approval decision endpoints are reachable by any caller with network access.

If the server is bound beyond localhost or tunneled, this is high risk.

---

## 2) Priority fixes

## P0 — Access control

- Add bearer-token middleware for all `/api/v1/*` routes.
- Enforce auth during WebSocket handshake.
- Return uniform `401` envelope for missing/invalid token.

## P1 — Abuse resistance

- Add global + per-session rate limiting.
- Add configurable burst controls for paid-provider endpoints.

## P2 — Safe exposure defaults

- Block startup on non-loopback host unless auth is enabled.
- Emit explicit startup warning when running without auth.

## P3 — Secret and key hygiene

- Generate local API token on first run.
- Store with strict filesystem permissions.
- Provide token rotation command in CLI.

---

## 3) GUI-side compensating controls (until P0-P3 land)

- Do not expose backend directly to public internet.
- Run backend behind a trusted reverse proxy that enforces auth.
- Keep frontend and backend on same trusted network boundary.
- Avoid storing provider secrets in frontend runtime entirely.

---

## 4) Validation plan

- Unit tests: auth middleware, websocket auth, token parser.
- Integration tests: unauthorized calls rejected across all route groups.
- Load tests: rate-limit behavior under burst traffic.
- Regression tests: approval endpoints reject unauthenticated requests.
