# Design Document (Current Product Direction)

## Canonical Agent Workbench (CAW)

**Version:** 1.1 (implementation-aligned)  
**Date:** 2026-03-20

---

## 1) Product intent

CAW is a human-directed agent workbench for:

- session-based reasoning (chat + branching)
- source-grounded research and synthesis
- multi-frame deliberation
- controlled workspace actions
- traceable/auditable execution
- evaluation-driven quality tracking

The system prioritizes operator control, inspectability, and workflow composition over "autonomous" behavior.

---

## 2) Core principles

1. **Human approval over silent automation** for risky actions.
2. **Trace everything significant** (provider calls, tools, results, errors).
3. **Composable capability surfaces** (research/deliberation/workspace/chat).
4. **Provider-agnostic orchestration** via registry + routing.
5. **Local-first deployment ergonomics** with explicit hardening path.

---

## 3) User-facing product surfaces

### 3.1 Current backend surface

- HTTP API (`/api/v1/*`)
- WebSocket stream for chat sessions
- CLI for local operations

### 3.2 Target GUI surface (now in progress)

The GUI should be a first-class client of the existing API/gateway, not a separate execution stack.

Required GUI capabilities:

- session lifecycle + message timeline
- streamed assistant responses
- trace explorer and run summary
- research ingest/retrieve/synthesize/export tools
- deliberation frame builder and disagreement viewer
- workspace read/write/patch/execute panel
- approvals queue and decision controls
- provider/skill visibility

---

## 4) Non-goals (current phase)

- multi-tenant auth/identity system
- distributed orchestration across many workers
- real-time collaborative editing across multiple users
- fully autonomous background execution without operator checkpoints

---

## 5) Success criteria for this phase

1. A second agent can implement a production-quality GUI solely against documented API contracts.
2. Every GUI action can be tied to a trace id and inspected.
3. Workspace mutations are always explainable and reviewable.
4. Error and recovery flows are explicit in UX.

---

## 6) Risks acknowledged

- Security hardening is incomplete until auth + rate-limit work lands.
- Some capability state is process-memory and should be externalized for scale.
- Capability payloads can be large; GUI performance work is required.

See `docs/security_roadmap.md` and `docs/roadmap.md` for mitigation plan.
