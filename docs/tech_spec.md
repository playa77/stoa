# Technical Specification

## Canonical Agent Workbench

**Version:** 1.0.0
**Status:** Draft
**Companion to:** Design Document v1.0
**Date:** 2026-03-08

---

## 0. Document Purpose and Audience

This document translates the Design Document into implementable architecture. Every module, interface, data model, state flow, and protocol surface described here must be traceable to a design principle, scope item, or strategic decision in the Design Document.

The primary audiences are:

- The human operator (Dan) as architectural decision-maker.
- Implementation agents of varying capability (from Claude Opus down to Gemini Flash, Haiku, or DeepSeek) who must be able to follow the companion Atomic Roadmap without ambiguity.
- Future contributors who need to understand not just what the system does but why each architectural choice was made.

Decision records are embedded inline using the format specified in Design Document §26.

---

## 1. System Identity

**Name:** Canonical Agent Workbench (working title; referred to as "CAW" or "the workbench" throughout this document)

**One-line:** A human-directed platform for high-fidelity compression, analysis, deliberation, and action across information and real workspaces, with an integrated evaluation spine.

**Runtime identity:** The workbench is a single deployable system with two user-facing surfaces (the product layer and the evaluation layer) sharing one orchestration core, one data layer, and one protocol substrate.

---

## 2. Technology Decisions

### 2.1 Primary language: Python

**Rationale:** Dan's stated preference; largest LLM tooling ecosystem; OpenClaw ecosystem is Python-native; strongest library coverage for document processing, retrieval, embedding, and evaluation. Bash is used only for orchestration glue where unavoidable.

**Alternatives considered:** TypeScript (strong for UI, weaker for ML/eval tooling, would split the stack), Rust (performance overkill for orchestration layer, high iteration cost), Elixir (excellent concurrency model but ecosystem mismatch).

**Downstream consequence:** Frontend will be a separate concern (see §2.3), communicating with the Python backend over well-defined APIs.

### 2.2 Minimum Python version: 3.11

**Rationale:** Required for `ExceptionGroup`, `TaskGroup`, and `tomllib` in stdlib. 3.12+ is acceptable but not required.

### 2.3 Frontend: Web-based SPA

**Technology:** React + TypeScript, served separately, communicating with the backend via HTTP REST + WebSocket (for streaming and live run updates).

**Rationale:** Platform-agnostic delivery; avoids Electron overhead; allows the interface to be accessed from any machine on the local network when running locally. Terminal UI (TUI) is a secondary interface and may be added later but is not architecturally required.

**Decision:** The frontend is out of scope for the first implementation wave. The backend exposes a complete API surface. A minimal developer UI (possibly terminal-based or a thin HTML page) is sufficient until the API stabilizes. This avoids premature polish over brittle internals (Design Document §20.5).

### 2.4 Database: SQLite

**Rationale:** Local-first (Design Document §5.8); zero-configuration; single-file portability; sufficient for single-user and small-team workloads; WAL mode provides adequate concurrent read performance. If scale demands change, the storage layer abstraction (§8) allows migration to PostgreSQL without architectural surgery.

**Alternatives considered:** PostgreSQL (overkill for local-first single-user MVP), DuckDB (excellent for analytics but weaker for transactional workloads), flat files (insufficient for relational queries across runs, traces, and artifacts).

### 2.5 Configuration format: TOML

**Rationale:** Python 3.11+ has `tomllib` in stdlib; human-readable; widely adopted for Python projects; avoids YAML's implicit typing hazards.

### 2.6 Package management: uv

**Rationale:** Fast, reliable, replaces pip/pip-tools/venv; deterministic lockfiles; actively maintained.

### 2.7 Versioning discipline: Semantic Versioning 2.0.0

All versioned artifacts in this project (the platform itself, skills, skill packs, API schemas, configuration schemas, trace formats) follow SemVer strictly. Version strings use the format `MAJOR.MINOR.PATCH` with optional pre-release identifiers (`-alpha.1`, `-rc.2`). MAJOR increments on breaking changes to public interfaces. MINOR increments on backward-compatible additions. PATCH increments on backward-compatible fixes.

The project repository maintains a `CHANGELOG.md` in Keep a Changelog format, updated with every version bump.

---

## 3. Repository Structure

The consolidated repository replaces all existing repositories under `github.com/playa77/`. The monorepo uses a flat top-level layout with clear package boundaries.

```
canonical-agent-workbench/
├── CHANGELOG.md
├── LICENSE
├── README.md
├── pyproject.toml                  # Root project config, workspace definition
├── uv.lock                        # Deterministic lockfile
│
├── docs/
│   ├── design_document.md          # Design Document (v1.0)
│   ├── technical_specification.md  # This document
│   ├── roadmap.md                  # Atomic Roadmap
│   └── decisions/                  # Standalone ADRs if needed beyond inline
│
├── src/
│   └── caw/                        # Main Python package
│       ├── __init__.py
│       ├── __version__.py          # Single source of truth for version string
│       │
│       ├── core/                   # Orchestration layer (§6)
│       │   ├── __init__.py
│       │   ├── engine.py           # Central orchestration engine
│       │   ├── session.py          # Session lifecycle management
│       │   ├── router.py           # Model and workflow routing
│       │   ├── checkpoint.py       # State checkpointing and recovery
│       │   └── permissions.py      # Permission model and gates
│       │
│       ├── skills/                 # Skill system (§7)
│       │   ├── __init__.py
│       │   ├── loader.py           # Skill discovery and loading
│       │   ├── resolver.py         # Skill resolution and precedence
│       │   ├── registry.py         # Skill registry and metadata
│       │   ├── pack.py             # Skill pack composition
│       │   └── validator.py        # Skill document validation
│       │
│       ├── storage/                # Storage layer (§8)
│       │   ├── __init__.py
│       │   ├── database.py         # SQLite connection and migration management
│       │   ├── models.py           # SQLAlchemy/dataclass models
│       │   ├── repository.py       # Data access patterns
│       │   └── migrations/         # Schema migration scripts
│       │
│       ├── capabilities/           # Capability layer (§9)
│       │   ├── __init__.py
│       │   ├── research/           # Research pillar
│       │   │   ├── __init__.py
│       │   │   ├── ingest.py       # Source ingestion pipeline
│       │   │   ├── retrieve.py     # Retrieval and search
│       │   │   ├── synthesize.py   # Citation-aware synthesis
│       │   │   └── export.py       # Report and artifact export
│       │   │
│       │   ├── deliberation/       # Deliberation pillar
│       │   │   ├── __init__.py
│       │   │   ├── frames.py       # Perspective frame management
│       │   │   ├── critique.py     # Adversarial review engine
│       │   │   ├── rhetoric.py     # Rhetorical/sophistic analysis
│       │   │   └── consensus.py    # Agreement/disagreement surfaces
│       │   │
│       │   ├── workspace/          # Action pillar
│       │   │   ├── __init__.py
│       │   │   ├── local.py        # Local file operations
│       │   │   ├── remote.py       # Remote workspace operations
│       │   │   ├── patch.py        # Patch proposal and application
│       │   │   └── executor.py     # Constrained command execution
│       │   │
│       │   └── chat/               # Chat mode
│       │       ├── __init__.py
│       │       ├── handler.py      # Message handling and streaming
│       │       └── history.py      # Conversation history management
│       │
│       ├── protocols/              # Protocol layer (§10)
│       │   ├── __init__.py
│       │   ├── provider.py         # Model provider abstraction
│       │   ├── mcp.py              # MCP client integration
│       │   └── tools.py            # Tool server abstraction
│       │
│       ├── traces/                 # Trace and audit system (§11)
│       │   ├── __init__.py
│       │   ├── collector.py        # Event collection
│       │   ├── store.py            # Trace persistence
│       │   ├── replay.py           # Run replay engine
│       │   └── schemas.py          # Trace event schemas
│       │
│       ├── evaluation/             # Evaluation layer (§12)
│       │   ├── __init__.py
│       │   ├── runner.py           # Benchmark task runner
│       │   ├── scorer.py           # Scoring framework
│       │   ├── comparator.py       # Side-by-side comparison
│       │   ├── regression.py       # Regression detection
│       │   └── tasks/              # Benchmark task definitions
│       │
│       ├── api/                    # API surface (§13)
│       │   ├── __init__.py
│       │   ├── app.py              # FastAPI application
│       │   ├── routes/             # Route modules per domain
│       │   ├── schemas.py          # Pydantic request/response models
│       │   └── websocket.py        # WebSocket handlers for streaming
│       │
│       └── cli/                    # CLI entry points
│           ├── __init__.py
│           └── main.py             # Click-based CLI
│
├── skills/                         # Skill documents (Claude Skills standard)
│   ├── builtin/                    # Ships with the platform
│   │   ├── research_operator.md
│   │   ├── deliberation_director.md
│   │   ├── workspace_operator.md
│   │   ├── critique_agent.md
│   │   ├── synthesis_agent.md
│   │   └── rhetoric_analyst.md
│   ├── packs/                      # Composed skill packs
│   │   ├── deep_research.toml
│   │   ├── adversarial_review.toml
│   │   └── workspace_ops.toml
│   └── user/                       # User-created skills (gitignored)
│
├── tasks/                          # Evaluation task definitions
│   ├── benchmarks/
│   └── regression/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── config/
│   ├── default.toml                # Default configuration
│   └── example.toml                # Annotated example for users
│
└── scripts/
    ├── setup.py                    # First-run setup
    └── migrate.py                  # Database migration runner
```

### 3.1 Decision: Monorepo over multi-repo

**Rationale:** The design document (§19) explicitly calls for convergence of existing repos into one architecture. A monorepo eliminates cross-repo version synchronization, simplifies CI, and allows atomic commits across layers. The existing repos (MADS for deliberation, icebox/madbox for environment configs, etc.) contribute ideas and patterns, not code to be mechanically merged.

**Tradeoff:** Monorepo requires discipline in package boundaries. This is enforced by the module structure above and by import linting rules defined in §14.

---

## 4. Architectural Layers

The system implements the five-layer conceptual model from Design Document §11. Each layer has a defined responsibility boundary, a public interface surface, and explicit dependencies.

```
┌─────────────────────────────────────────────────────────┐
│                   INTERACTION LAYER                      │
│  API (REST + WebSocket) │ CLI │ Future: Web UI / TUI     │
├─────────────────────────────────────────────────────────┤
│                  ORCHESTRATION LAYER                     │
│  Engine │ Session │ Router │ Checkpoint │ Permissions     │
├─────────────────────────────────────────────────────────┤
│                   CAPABILITY LAYER                       │
│  Research │ Deliberation │ Workspace │ Chat               │
├─────────────────────────────────────────────────────────┤
│                    PROTOCOL LAYER                        │
│  Provider Abstraction │ MCP │ Tool Servers                │
├─────────────────────────────────────────────────────────┤
│                   EVALUATION LAYER                       │
│  Runner │ Scorer │ Comparator │ Regression                │
├─────────────────────────────────────────────────────────┤
│              CROSS-CUTTING CONCERNS                      │
│  Traces │ Storage │ Skills │ Configuration                │
└─────────────────────────────────────────────────────────┘
```

### 4.1 Dependency rules

- **Interaction** depends on **Orchestration** only. Never directly on Capability or Protocol.
- **Orchestration** depends on **Capability**, **Protocol**, **Skills**, **Traces**, and **Storage**.
- **Capability** depends on **Protocol**, **Skills**, **Traces**, and **Storage**. Never on Orchestration (no upward dependency).
- **Protocol** depends on nothing internal (it wraps external APIs).
- **Evaluation** depends on **Orchestration** (it drives runs), **Traces** (it reads them), **Storage** (it persists results), and **Skills** (it loads them for eval runs).
- **Traces**, **Storage**, **Skills**, and **Configuration** are cross-cutting and may be imported by any layer above Protocol.

These rules are enforced by import linting (§14.3).

---

## 5. Module Specifications

### 5.1 Configuration System

#### 5.1.1 Configuration hierarchy (highest precedence first)

1. **Runtime overrides** — passed via CLI flags or API parameters per-request.
2. **Environment variables** — prefixed `CAW_`, nested with `__` (e.g., `CAW_STORAGE__DB_PATH`).
3. **User config file** — `~/.config/caw/config.toml` (XDG-compliant on Linux).
4. **Project config file** — `./caw.toml` in the working directory (if present).
5. **Default config** — `config/default.toml` shipped with the package.

#### 5.1.2 Configuration schema

```toml
[general]
version = "1.0.0"                       # Config schema version (SemVer)
log_level = "INFO"                      # DEBUG | INFO | WARNING | ERROR
data_dir = "~/.local/share/caw"         # XDG-compliant default

[storage]
db_path = "${data_dir}/caw.db"          # SQLite database path
trace_dir = "${data_dir}/traces"        # Trace event storage
artifact_dir = "${data_dir}/artifacts"  # Generated artifact storage

[providers]
default = "anthropic"                   # Default model provider key

[providers.anthropic]
type = "anthropic"
api_key_env = "ANTHROPIC_API_KEY"       # Env var name, never stored in config
default_model = "claude-sonnet-4-20250514"
max_tokens = 8192
timeout_seconds = 120

[providers.openai]
type = "openai"
api_key_env = "OPENAI_API_KEY"
default_model = "gpt-4o"
max_tokens = 4096
timeout_seconds = 120

[providers.local]
type = "openai_compatible"
base_url = "http://localhost:11434/v1"  # e.g., Ollama
api_key_env = ""                        # Often not required for local
default_model = "llama3.1:70b"
max_tokens = 4096
timeout_seconds = 300

[routing]
strategy = "config"                     # config | cost | capability | latency
fallback_chain = ["anthropic", "local"] # Ordered fallback if primary fails

[skills]
builtin_dir = "skills/builtin"          # Relative to package root
user_dir = "skills/user"                # Relative to project root
packs_dir = "skills/packs"

[workspace]
sandbox_mode = "permissive"             # strict | permissive | none
allowed_paths = ["~", "/tmp"]           # Paths accessible in strict mode
confirm_writes = true                   # Require human confirmation for writes
confirm_deletes = true                  # Require human confirmation for deletes
confirm_executions = true               # Require human confirmation for commands

[evaluation]
tasks_dir = "tasks"
results_dir = "${data_dir}/eval_results"
default_scorer = "composite"

[api]
host = "127.0.0.1"
port = 8420
cors_origins = ["http://localhost:3000"]
```

#### 5.1.3 Configuration validation

On startup, the configuration is loaded, merged according to the precedence hierarchy, and validated against a Pydantic model. Validation failures produce specific, actionable error messages and prevent startup. Unknown keys are warnings, not errors (forward compatibility).

```python
# src/caw/core/config.py

from pydantic import BaseModel, field_validator
from pathlib import Path

class StorageConfig(BaseModel):
    db_path: Path
    trace_dir: Path
    artifact_dir: Path

class ProviderConfig(BaseModel):
    type: str                          # anthropic | openai | openai_compatible
    api_key_env: str
    default_model: str
    max_tokens: int = 4096
    timeout_seconds: int = 120
    base_url: str | None = None

class WorkspaceConfig(BaseModel):
    sandbox_mode: str = "permissive"   # strict | permissive | none
    allowed_paths: list[str] = ["~", "/tmp"]
    confirm_writes: bool = True
    confirm_deletes: bool = True
    confirm_executions: bool = True

    @field_validator("sandbox_mode")
    @classmethod
    def validate_sandbox_mode(cls, v: str) -> str:
        if v not in ("strict", "permissive", "none"):
            raise ValueError(f"sandbox_mode must be strict|permissive|none, got '{v}'")
        return v

class CAWConfig(BaseModel):
    """Top-level validated configuration for the workbench."""
    general: GeneralConfig
    storage: StorageConfig
    providers: dict[str, ProviderConfig]
    routing: RoutingConfig
    skills: SkillsConfig
    workspace: WorkspaceConfig
    evaluation: EvaluationConfig
    api: APIConfig
```

---

## 6. Orchestration Layer

The orchestration layer is the central nervous system. It receives requests from the interaction layer, resolves skills and workflows, routes to providers, manages state, enforces permissions, and emits trace events.

### 6.1 Engine

The engine is the single entry point for all orchestrated work. Every mode (chat, research, deliberation, workspace, arena) passes through the engine.

```python
# Simplified interface — full implementation in src/caw/core/engine.py

class Engine:
    """Central orchestration engine.

    All work flows through this class. It resolves skills,
    selects providers, manages sessions, enforces permissions,
    and emits trace events for every significant action.
    """

    def __init__(self, config: CAWConfig) -> None: ...

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a single orchestrated request.

        Lifecycle:
        1. Validate request against permissions.
        2. Resolve applicable skills (§7).
        3. Route to provider (§6.3).
        4. Execute capability (§9).
        5. Emit trace events (§11).
        6. Checkpoint state if needed (§6.4).
        7. Return result.
        """
        ...

    async def execute_workflow(self, workflow: Workflow) -> WorkflowResult:
        """Execute a multi-step workflow.

        A workflow is a DAG of ExecutionRequests with
        dependency edges, conditional branches, and
        human approval gates.
        """
        ...
```

### 6.2 Sessions

A session represents a coherent unit of user interaction. Sessions have identity, state, history, and lifecycle.

```python
class SessionState(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"        # User paused; can resume
    CHECKPOINTED = "checkpointed"  # Saved for later
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Session:
    id: str                          # UUIDv7 (time-ordered)
    created_at: datetime
    updated_at: datetime
    state: SessionState
    mode: SessionMode                # chat | research | deliberation | workspace | arena
    parent_id: str | None            # For branched sessions
    config_overrides: dict           # Per-session config overrides
    active_skills: list[str]         # Resolved skill IDs for this session
    active_skill_pack: str | None    # Skill pack ID if one was loaded
    message_history: list[Message]   # Full message sequence
    artifacts: list[ArtifactRef]     # Artifacts produced in this session
    trace_id: str                    # Links to trace store
```

#### 6.2.1 Session branching

A user can branch a session at any point, creating a new session that inherits the parent's history up to the branch point. The parent session remains unmodified. This supports the "explore alternative paths" use case from Design Document §8.1.A.

```python
async def branch_session(self, session_id: str, branch_point: int) -> Session:
    """Create a new session branching from an existing one.

    Args:
        session_id: The parent session to branch from.
        branch_point: Message index at which to branch (inclusive).

    Returns:
        A new Session with state ACTIVE, parent_id set,
        and message_history copied up to branch_point.
    """
    ...
```

### 6.3 Router

The router selects which model provider handles a given request. Routing decisions are logged as trace events.

```python
class RoutingStrategy(str, Enum):
    CONFIG = "config"          # Use provider specified in config/request
    COST = "cost"              # Minimize cost (prefer cheaper models)
    CAPABILITY = "capability"  # Match model to task requirements
    LATENCY = "latency"        # Minimize response time

class Router:
    """Selects model provider for each request.

    Routing is deterministic given the same inputs.
    Every routing decision is logged as a trace event
    including: strategy used, candidates considered,
    selection rationale, and fallback chain position.
    """

    async def route(self, request: ExecutionRequest) -> ProviderSelection:
        """Select a provider for the request.

        Process:
        1. Check for explicit provider in request.
        2. Check for skill-level provider preference.
        3. Apply routing strategy from config.
        4. Validate provider availability (health check cache).
        5. Return selection with fallback chain.
        """
        ...
```

#### 6.3.1 Decision: Routing as explicit infrastructure

**Rationale:** The design document (§5.7, §22.5) demands provider-agnostic architecture. Routing is the mechanism that delivers this. By making routing explicit and traced, the system avoids silent provider lock-in and enables the evaluation layer to compare provider performance.

**Alternatives considered:** Hardcoded provider per mode (too rigid), LLM-based meta-routing (too slow and circular), pure environment-variable switching (invisible and untraceable).

### 6.4 Checkpointing

Long-running workflows (research-to-report, multi-turn deliberation) must survive interruption. The checkpoint system serializes session state to storage at defined points.

```python
class CheckpointManager:
    """Manages session state checkpointing.

    Checkpoints are taken:
    - After each completed step in a multi-step workflow.
    - On explicit user request (pause).
    - Before any destructive workspace operation.
    - On graceful shutdown.

    Checkpoint data includes:
    - Full session state.
    - Message history.
    - Active skills and their resolved content.
    - Workflow position (step index, branch state).
    - Pending approval gates.
    """

    async def save(self, session: Session) -> CheckpointRef: ...
    async def restore(self, checkpoint_ref: CheckpointRef) -> Session: ...
    async def list_checkpoints(self, session_id: str) -> list[CheckpointRef]: ...
```

### 6.5 Permissions

The permission model implements Design Document §17 (Safety and Control Philosophy) and §5.1 (Human-first agency).

#### 6.5.1 Permission levels

| Level | Description | Examples | Gate |
|-------|-------------|----------|------|
| `read` | Read-only access to data | File read, search, retrieval | None |
| `suggest` | Propose changes without applying | Patch proposal, command preview | None |
| `write` | Modify files or state | File write, database update | Configurable (default: confirm) |
| `execute` | Run commands or scripts | Shell commands, API calls | Configurable (default: confirm) |
| `delete` | Remove files or data | File deletion, record removal | Always confirm |
| `admin` | System configuration changes | Config modification, skill install | Always confirm |

#### 6.5.2 Approval gates

When a permission gate requires confirmation, the engine pauses execution, emits a `gate:approval_required` trace event, and surfaces the pending action to the user through the interaction layer. The action includes: what will be done, what resources are affected, whether it is reversible, and the estimated impact.

```python
@dataclass
class ApprovalRequest:
    id: str
    session_id: str
    action: str                    # Human-readable description
    permission_level: str          # write | execute | delete | admin
    resources: list[str]           # Paths, URLs, or identifiers affected
    reversible: bool               # Whether the action can be undone
    preview: str | None            # Diff, command text, or description
    timeout_seconds: int = 300     # Auto-deny after timeout

@dataclass
class ApprovalResponse:
    request_id: str
    approved: bool
    modifier: str | None           # Optional user modification to the action
    timestamp: datetime
```

---

## 7. Skill System

The skill system is the primary internal control surface (Design Document §5.6, §22.7). It replaces monolithic system prompts with modular, versioned, composable skill documents.

### 7.1 Skill document format

Skills follow the Claude Skills standard format used by OpenClaw. Each skill is a Markdown file with YAML frontmatter.

```markdown
---
skill_id: "caw.builtin.research_operator"
version: "1.0.0"
name: "Research Operator"
description: "Guides source ingestion, retrieval, citation-aware synthesis, and report generation."
author: "CAW"
tags: ["research", "synthesis", "citation"]
requires_tools: ["retrieval", "file_read"]
requires_permissions: ["read"]
conflicts_with: []
priority: 100                          # Higher = loaded later = overrides earlier
---

# Research Operator

## Role

You are a research operator responsible for...

## Constraints

- Always preserve source citations...
- Never synthesize claims without evidentiary grounding...

## Tool Usage

When using the retrieval tool...

## Output Format

Research outputs must include...
```

#### 7.1.1 Frontmatter schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `skill_id` | string | yes | Dot-namespaced unique identifier |
| `version` | string (SemVer) | yes | Skill version |
| `name` | string | yes | Human-readable name |
| `description` | string | yes | Purpose summary |
| `author` | string | yes | Creator identifier |
| `tags` | list[string] | no | Searchable tags |
| `requires_tools` | list[string] | no | Tools this skill needs |
| `requires_permissions` | list[string] | no | Minimum permissions |
| `conflicts_with` | list[string] | no | Skill IDs that cannot coexist |
| `priority` | int | no | Resolution precedence (default: 100) |
| `provider_preference` | string | no | Preferred model provider key |
| `min_context_window` | int | no | Minimum context window in tokens |

### 7.2 Skill resolution

When a session starts or a mode is invoked, the skill resolver determines which skills to activate.

#### 7.2.1 Resolution order

1. **Explicit request** — skills specified by the user in the session or request.
2. **Skill pack** — if a skill pack is active, all skills in the pack are loaded.
3. **Mode default** — each mode has a default set of skills.
4. **Builtin base** — core safety and tracing skills always load.

#### 7.2.2 Conflict resolution

If two active skills declare `conflicts_with` each other, the skill with higher `priority` wins. If priorities are equal, the more specifically requested skill wins (explicit > pack > mode default > builtin). Ties are errors and halt resolution with a diagnostic message.

#### 7.2.3 Precedence and composition

When multiple skills are active, their content is composed into the final control context in priority order (lowest first, highest last). This means higher-priority skills can override guidance from lower-priority ones. The composed result is a single context block sent to the model provider, with clear `<!-- BEGIN SKILL: {skill_id} -->` / `<!-- END SKILL: {skill_id} -->` delimiters for traceability.

### 7.3 Skill packs

A skill pack is a TOML file that defines a named, versioned composition of skills with optional overrides.

```toml
[pack]
pack_id = "caw.packs.deep_research"
version = "1.0.0"
name = "Deep Research"
description = "Full research pipeline with adversarial review."

[[pack.skills]]
skill_id = "caw.builtin.research_operator"
version = ">=1.0.0"                    # SemVer range

[[pack.skills]]
skill_id = "caw.builtin.critique_agent"
version = ">=1.0.0"
priority_override = 150               # Override default priority

[[pack.skills]]
skill_id = "caw.builtin.synthesis_agent"
version = ">=1.0.0"

[pack.config_overrides]
providers.default = "anthropic"        # Pack-level config overrides
routing.strategy = "capability"
```

### 7.4 Skill validation

The validator checks skill documents at load time:

- Frontmatter parses against the schema (§7.1.1).
- `skill_id` is unique within the resolved set.
- `version` is valid SemVer.
- `requires_tools` references tools that exist in the tool registry.
- `requires_permissions` references valid permission levels.
- `conflicts_with` references valid skill IDs.
- Markdown body is non-empty and well-formed.

Validation failures are logged with specific error messages and prevent the skill from loading. They do not crash the system.

---

## 8. Storage Layer

### 8.1 Database schema

The database uses SQLite with WAL mode. All tables use UUIDv7 primary keys for time-ordered uniqueness. Timestamps are ISO 8601 UTC strings.

```sql
-- Schema version tracking
CREATE TABLE schema_version (
    version     TEXT PRIMARY KEY,          -- SemVer
    applied_at  TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);

-- Sessions
CREATE TABLE sessions (
    id              TEXT PRIMARY KEY,       -- UUIDv7
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    state           TEXT NOT NULL,          -- created|active|paused|checkpointed|completed|failed
    mode            TEXT NOT NULL,          -- chat|research|deliberation|workspace|arena
    parent_id       TEXT REFERENCES sessions(id),
    config_json     TEXT,                   -- JSON: per-session config overrides
    active_skills   TEXT,                   -- JSON: list of resolved skill IDs
    active_pack     TEXT,                   -- Skill pack ID if applicable
    metadata_json   TEXT                    -- JSON: extensible metadata
);
CREATE INDEX idx_sessions_state ON sessions(state);
CREATE INDEX idx_sessions_mode ON sessions(mode);
CREATE INDEX idx_sessions_updated ON sessions(updated_at);

-- Messages
CREATE TABLE messages (
    id              TEXT PRIMARY KEY,       -- UUIDv7
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    sequence_num    INTEGER NOT NULL,       -- Order within session
    role            TEXT NOT NULL,          -- user|assistant|system|tool
    content         TEXT NOT NULL,          -- Message content
    model           TEXT,                   -- Model used for assistant messages
    provider        TEXT,                   -- Provider key used
    token_count_in  INTEGER,               -- Input tokens consumed
    token_count_out INTEGER,               -- Output tokens generated
    created_at      TEXT NOT NULL,
    metadata_json   TEXT                    -- JSON: tool calls, citations, etc.
);
CREATE INDEX idx_messages_session ON messages(session_id, sequence_num);

-- Artifacts
CREATE TABLE artifacts (
    id              TEXT PRIMARY KEY,       -- UUIDv7
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    type            TEXT NOT NULL,          -- report|patch|file|export|evaluation_result
    name            TEXT NOT NULL,
    path            TEXT,                   -- Filesystem path if persisted
    content         TEXT,                   -- Inline content if small
    content_hash    TEXT,                   -- SHA-256 of content/file
    created_at      TEXT NOT NULL,
    metadata_json   TEXT
);
CREATE INDEX idx_artifacts_session ON artifacts(session_id);
CREATE INDEX idx_artifacts_type ON artifacts(type);

-- Trace events (high-volume, append-only)
CREATE TABLE trace_events (
    id              TEXT PRIMARY KEY,       -- UUIDv7
    trace_id        TEXT NOT NULL,          -- Groups events for one run
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    timestamp       TEXT NOT NULL,
    event_type      TEXT NOT NULL,          -- See §11 for event types
    data_json       TEXT NOT NULL,          -- JSON: event-specific payload
    parent_event_id TEXT REFERENCES trace_events(id)
);
CREATE INDEX idx_trace_session ON trace_events(session_id);
CREATE INDEX idx_trace_trace_id ON trace_events(trace_id);
CREATE INDEX idx_trace_type ON trace_events(event_type);
CREATE INDEX idx_trace_timestamp ON trace_events(timestamp);

-- Sources (for research pillar)
CREATE TABLE sources (
    id              TEXT PRIMARY KEY,       -- UUIDv7
    session_id      TEXT REFERENCES sessions(id),
    type            TEXT NOT NULL,          -- file|url|text|api
    uri             TEXT,                   -- Original location
    title           TEXT,
    content         TEXT,                   -- Extracted text content
    content_hash    TEXT,                   -- SHA-256
    embedding       BLOB,                   -- Vector embedding (optional)
    created_at      TEXT NOT NULL,
    metadata_json   TEXT
);
CREATE INDEX idx_sources_session ON sources(session_id);
CREATE INDEX idx_sources_hash ON sources(content_hash);

-- Citations (links claims to sources)
CREATE TABLE citations (
    id              TEXT PRIMARY KEY,       -- UUIDv7
    message_id      TEXT NOT NULL REFERENCES messages(id),
    source_id       TEXT NOT NULL REFERENCES sources(id),
    claim           TEXT NOT NULL,          -- The claim being cited
    excerpt         TEXT,                   -- Source excerpt supporting the claim
    confidence      REAL,                   -- 0.0-1.0 confidence score
    location        TEXT,                   -- Page, paragraph, or offset in source
    created_at      TEXT NOT NULL
);
CREATE INDEX idx_citations_message ON citations(message_id);
CREATE INDEX idx_citations_source ON citations(source_id);

-- Evaluation runs
CREATE TABLE eval_runs (
    id              TEXT PRIMARY KEY,       -- UUIDv7
    task_id         TEXT NOT NULL,
    provider        TEXT NOT NULL,
    model           TEXT NOT NULL,
    skill_pack      TEXT,
    started_at      TEXT NOT NULL,
    completed_at    TEXT,
    status          TEXT NOT NULL,          -- running|completed|failed
    scores_json     TEXT,                   -- JSON: scoring results
    trace_id        TEXT,                   -- Links to trace store
    metadata_json   TEXT
);
CREATE INDEX idx_eval_task ON eval_runs(task_id);
CREATE INDEX idx_eval_provider ON eval_runs(provider, model);

-- Checkpoints
CREATE TABLE checkpoints (
    id              TEXT PRIMARY KEY,       -- UUIDv7
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    created_at      TEXT NOT NULL,
    state_json      TEXT NOT NULL,          -- Serialized session state
    message_index   INTEGER NOT NULL,       -- Message count at checkpoint
    description     TEXT
);
CREATE INDEX idx_checkpoints_session ON checkpoints(session_id);
```

### 8.2 Migration strategy

Schema migrations are Python scripts in `src/caw/storage/migrations/`, named with a version prefix: `001_initial_schema.py`, `002_add_citations_table.py`, etc. Each migration has an `up()` and `down()` function. The `schema_version` table tracks applied migrations. Migrations run automatically on startup if needed, with a backup taken before any destructive migration.

### 8.3 Data access patterns

All database access goes through repository classes, never raw SQL in business logic.

```python
class SessionRepository:
    """Data access for sessions.

    All methods are async. All writes are wrapped in
    transactions. All reads use parameterized queries.
    """

    async def create(self, session: Session) -> Session: ...
    async def get(self, session_id: str) -> Session | None: ...
    async def update(self, session: Session) -> Session: ...
    async def list_by_state(self, state: SessionState, limit: int = 50) -> list[Session]: ...
    async def list_by_mode(self, mode: SessionMode, limit: int = 50) -> list[Session]: ...
    async def get_with_messages(self, session_id: str) -> tuple[Session, list[Message]]: ...
```

### 8.4 Decision: SQLAlchemy vs raw SQL vs dataclasses+aiosqlite

**Choice:** Dataclasses for models + `aiosqlite` for async access + raw parameterized SQL in repository methods.

**Rationale:** SQLAlchemy's ORM adds substantial complexity for a single-user SQLite workload. The schema is well-defined and stable enough that raw SQL in repository methods is clearer and more debuggable. Dataclasses provide type safety without ORM magic. `aiosqlite` provides async access needed for the async orchestration engine.

**Tradeoff:** If the project migrates to PostgreSQL, the repository layer must be rewritten. This is acceptable because the repository boundary isolates the change.

---

## 9. Capability Layer

The capability layer implements the four product pillars from Design Document §12.

### 9.1 Research capability

#### 9.1.1 Ingestion pipeline

```python
class IngestPipeline:
    """Processes raw sources into indexed, retrievable content.

    Supported source types:
    - Files: .txt, .md, .pdf, .docx, .html, .csv, .json, .xml
    - URLs: fetched and converted to text
    - Raw text: pasted or piped input

    Pipeline stages:
    1. Detection: identify source type and encoding.
    2. Extraction: convert to plain text with structure markers.
    3. Chunking: split into retrieval-sized segments with overlap.
    4. Embedding: generate vector embeddings for each chunk (optional).
    5. Storage: persist source record, chunks, and embeddings.
    6. Indexing: update retrieval index.

    Each stage emits trace events.
    """

    async def ingest(self, source: SourceInput) -> Source: ...
    async def ingest_batch(self, sources: list[SourceInput]) -> list[Source]: ...
```

#### 9.1.2 Retrieval

```python
class Retriever:
    """Retrieves relevant content from ingested sources.

    Retrieval strategies:
    - keyword: BM25/TF-IDF text search via SQLite FTS5.
    - semantic: vector similarity search against embeddings.
    - hybrid: weighted combination of keyword and semantic scores.

    All retrieval results include source provenance (source ID,
    chunk location, relevance score) for downstream citation.
    """

    async def retrieve(
        self,
        query: str,
        session_id: str,
        strategy: str = "hybrid",
        top_k: int = 10,
        min_score: float = 0.0
    ) -> list[RetrievalResult]: ...
```

#### 9.1.3 Synthesis

```python
class Synthesizer:
    """Produces citation-aware synthesis from retrieved content.

    Synthesis follows the fidelity-over-fluency principle
    (Design Document §5.2). Every claim in the synthesis
    output is linked to one or more source citations.

    Output structure:
    - claims: list of synthesized claims, each with citation IDs
    - uncertainty_markers: explicit flags where sources conflict or coverage is thin
    - source_map: mapping from citation IDs to source excerpts
    """

    async def synthesize(
        self,
        query: str,
        retrieval_results: list[RetrievalResult],
        output_format: str = "structured",  # structured | narrative | brief
        active_skills: list[ResolvedSkill] | None = None
    ) -> SynthesisResult: ...
```

#### 9.1.4 Export

Produces deliverable artifacts from synthesis results:

- **Markdown report**: structured document with inline citations.
- **JSON structured output**: machine-readable claims, citations, and evidence map.
- **DOCX report**: formatted document via the docx skill.
- **Evidence map**: JSON graph of claims → sources → excerpts.

### 9.2 Deliberation capability

#### 9.2.1 Deliberation architecture

Deliberation implements Design Document §12.2 and §13.3. It is not "multi-agent theater" — it is structured multi-perspective reasoning where each perspective is a role with a defined skill, and the output is a disagreement surface, not a consensus illusion.

```python
class DeliberationEngine:
    """Orchestrates structured multi-perspective reasoning.

    A deliberation consists of:
    1. Frame definition: what perspectives will be represented.
    2. Initial generation: each frame produces its position.
    3. Critique rounds: frames respond to each other.
    4. Rhetoric analysis: identify sophistic devices, biases,
       inconsistencies across all positions.
    5. Disagreement surface: explicit map of agreements,
       disagreements, and open questions.
    6. Synthesis: optional final integration.

    Each frame is driven by a skill document that defines
    the perspective's constraints, priorities, and style.
    Frames may use the same or different model providers.
    """

    async def deliberate(
        self,
        question: str,
        frames: list[FrameConfig],
        rounds: int = 2,
        include_rhetoric_analysis: bool = True,
        include_synthesis: bool = True
    ) -> DeliberationResult: ...
```

#### 9.2.2 Frame configuration

```python
@dataclass
class FrameConfig:
    frame_id: str                    # Unique within this deliberation
    skill_id: str                    # Skill document defining this perspective
    label: str                       # Human-readable label (e.g., "Devil's Advocate")
    provider: str | None = None      # Optional provider override
    model: str | None = None         # Optional model override
    initial_context: str | None = None  # Additional framing context
```

#### 9.2.3 Deliberation result

```python
@dataclass
class DeliberationResult:
    question: str
    frames: list[FrameOutput]        # Each frame's position and critique responses
    rhetoric_analysis: RhetoricAnalysis | None
    disagreement_surface: DisagreementSurface
    synthesis: str | None
    trace_id: str

@dataclass
class DisagreementSurface:
    agreements: list[AgreementPoint]     # Claims all frames accept
    disagreements: list[DisagreementPoint]  # Claims where frames diverge
    open_questions: list[str]            # Unresolved issues
    confidence_map: dict[str, float]     # Per-claim confidence aggregation
```

#### 9.2.4 Rhetoric analysis

```python
@dataclass
class RhetoricAnalysis:
    """Analysis of rhetorical and sophistic devices across all frame outputs.

    Implements Design Document §4 bullet items:
    finding/identifying biases, rhetorical/sophistic devices/figures,
    inconsistencies and contradictions.
    """

    devices: list[RhetoricalDevice]      # Identified devices with locations
    biases: list[IdentifiedBias]         # Cognitive or framing biases detected
    inconsistencies: list[Inconsistency] # Internal contradictions within frames
    cross_frame_contradictions: list[Contradiction]  # Contradictions between frames

@dataclass
class RhetoricalDevice:
    device_type: str                 # e.g., "appeal_to_authority", "false_dichotomy"
    frame_id: str                    # Which frame used it
    excerpt: str                     # The text exhibiting the device
    explanation: str                 # Why this qualifies
    severity: str                    # informational | cautionary | deceptive
```

### 9.3 Workspace capability

#### 9.3.1 File operations

```python
class WorkspaceOperator:
    """Manages file and workspace operations with safety constraints.

    All operations respect the permission model (§6.5).
    All mutations require approval when configured.
    All operations emit trace events.
    """

    # Read operations (permission level: read)
    async def list_files(self, path: str, recursive: bool = False) -> list[FileInfo]: ...
    async def read_file(self, path: str) -> FileContent: ...
    async def search_files(self, pattern: str, path: str) -> list[FileInfo]: ...
    async def diff_files(self, path_a: str, path_b: str) -> DiffResult: ...

    # Write operations (permission level: write, gated)
    async def write_file(self, path: str, content: str) -> WriteResult: ...
    async def apply_patch(self, patch: PatchProposal) -> PatchResult: ...
    async def move_file(self, src: str, dst: str) -> MoveResult: ...
    async def copy_file(self, src: str, dst: str) -> CopyResult: ...

    # Delete operations (permission level: delete, always gated)
    async def delete_file(self, path: str) -> DeleteResult: ...

    # Execute operations (permission level: execute, gated)
    async def execute_command(
        self,
        command: str,
        working_dir: str | None = None,
        timeout_seconds: int = 30,
        env: dict[str, str] | None = None
    ) -> ExecutionResult: ...
```

#### 9.3.2 Patch proposals

Before applying changes, the workspace generates a patch proposal that the user can review.

```python
@dataclass
class PatchProposal:
    id: str
    target_path: str
    original_content_hash: str       # SHA-256 of current content (detect conflicts)
    hunks: list[PatchHunk]           # Individual change hunks
    description: str                 # Human-readable summary
    reversible: bool                 # Whether a reverse patch was generated
    reverse_patch: PatchProposal | None  # For rollback

@dataclass
class PatchHunk:
    start_line: int
    end_line: int
    original_lines: list[str]
    replacement_lines: list[str]
    context_before: list[str]        # 3 lines of context
    context_after: list[str]
```

#### 9.3.3 Remote workspace operations

Remote workspace support uses SSH for command execution and SFTP for file operations. Connection configuration is stored per-workspace in the config.

```python
@dataclass
class RemoteWorkspace:
    id: str
    name: str
    host: str
    port: int = 22
    user: str = ""
    key_path: str | None = None      # SSH key path
    base_path: str = "~"             # Remote base directory
```

Remote operations use the same `WorkspaceOperator` interface. The implementation dispatches to local or remote based on the workspace context.

### 9.4 Chat capability

Chat is the fast entry point (Design Document §13.1). It is the simplest capability: take a user message, resolve skills, call a provider, return the response, log everything.

```python
class ChatHandler:
    """Handles conversational interactions.

    Chat is intentionally thin. It does not implement
    research, deliberation, or workspace logic directly.
    Instead, it can invoke those capabilities through
    the orchestration engine when the user requests them
    or when a skill's guidance triggers them.
    """

    async def handle_message(
        self,
        session_id: str,
        message: str,
        attachments: list[Attachment] | None = None
    ) -> AsyncIterator[StreamChunk]:
        """Process a user message and stream the response.

        Yields StreamChunk objects containing:
        - text: incremental text content
        - tool_call: tool invocation events
        - tool_result: tool results
        - citation: citation events
        - done: completion signal with final metadata
        """
        ...
```

---

## 10. Protocol Layer

The protocol layer abstracts external model providers and tool servers behind stable interfaces (Design Document §5.7, §11.4).

### 10.1 Provider abstraction

```python
class ModelProvider(Protocol):
    """Interface that all model providers must implement.

    This is the contract that makes the system provider-agnostic.
    New providers are added by implementing this protocol and
    registering them in the provider registry.
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider (e.g., 'anthropic', 'openai')."""
        ...

    async def complete(
        self,
        messages: list[ProviderMessage],
        model: str,
        tools: list[ToolDefinition] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        stream: bool = False
    ) -> ProviderResponse | AsyncIterator[ProviderStreamChunk]:
        """Send a completion request to the provider."""
        ...

    async def health_check(self) -> ProviderHealth:
        """Check provider availability and latency."""
        ...

    def supports_tool_use(self) -> bool: ...
    def supports_streaming(self) -> bool: ...
    def max_context_window(self, model: str) -> int: ...
```

#### 10.1.1 Provider implementations

Three provider implementations ship with the platform:

- **AnthropicProvider**: Anthropic API (Claude models). Uses the `anthropic` Python SDK.
- **OpenAIProvider**: OpenAI API (GPT models). Uses the `openai` Python SDK.
- **OpenAICompatibleProvider**: Any OpenAI-compatible API (Ollama, vLLM, LM Studio, etc.). Uses the `openai` SDK with a custom `base_url`.

Additional providers can be added by implementing the `ModelProvider` protocol and registering in the provider config.

#### 10.1.2 Provider message normalization

Each provider has its own message format. The protocol layer normalizes between the internal `ProviderMessage` format and provider-specific formats. This normalization is the provider implementation's responsibility.

```python
@dataclass
class ProviderMessage:
    role: str                        # user | assistant | system | tool
    content: str | list[ContentBlock]
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None  # For tool result messages
    name: str | None = None          # For tool messages

@dataclass
class ContentBlock:
    type: str                        # text | image | document
    text: str | None = None
    media_type: str | None = None
    data: str | None = None          # Base64 for images/documents
    source_uri: str | None = None
```

### 10.2 Tool server abstraction

```python
class ToolServer(Protocol):
    """Interface for tool servers.

    Tools can be local functions, MCP servers, or remote APIs.
    All tool invocations are logged as trace events.
    """

    async def list_tools(self) -> list[ToolDefinition]: ...
    async def invoke(self, tool_name: str, arguments: dict) -> ToolResult: ...
    async def health_check(self) -> bool: ...

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict                 # JSON Schema for parameters
    permission_level: str            # read | write | execute | delete
    server_id: str                   # Which server provides this tool

@dataclass
class ToolResult:
    tool_name: str
    success: bool
    output: str | dict | list
    error: str | None = None
    duration_ms: int = 0
```

### 10.3 MCP integration

MCP (Model Context Protocol) is supported as a first-class tool server type.

```python
class MCPClient:
    """Client for MCP-compatible tool servers.

    Handles:
    - Server discovery and connection.
    - Tool listing and schema retrieval.
    - Tool invocation with proper framing.
    - Connection lifecycle (connect, reconnect, close).
    """

    async def connect(self, server_url: str) -> None: ...
    async def list_tools(self) -> list[ToolDefinition]: ...
    async def invoke(self, tool_name: str, arguments: dict) -> ToolResult: ...
    async def close(self) -> None: ...
```

---

## 11. Trace System

The trace system implements Design Document §5.4 ("Trace everything that matters") and §8.1.E.

### 11.1 Trace event types

Every significant action in the system emits a typed trace event. Events are append-only, immutable, and linked by `trace_id` (per-run) and `session_id` (per-session).

| Event Type | Payload | Emitted By |
|------------|---------|------------|
| `session:created` | session config, mode, skills | Engine |
| `session:state_changed` | old state, new state | Engine |
| `session:branched` | parent_id, branch_point | Engine |
| `skill:resolved` | resolved skill IDs, precedence chain | Resolver |
| `skill:conflict` | conflicting skill IDs, resolution | Resolver |
| `routing:decision` | strategy, candidates, selection, rationale | Router |
| `provider:request` | provider, model, message count, token estimate | Provider |
| `provider:response` | provider, model, tokens used, latency_ms | Provider |
| `provider:error` | provider, model, error type, message | Provider |
| `provider:fallback` | from_provider, to_provider, reason | Router |
| `tool:invocation` | tool_name, arguments, server_id | ToolServer |
| `tool:result` | tool_name, success, duration_ms | ToolServer |
| `retrieval:query` | query, strategy, top_k | Retriever |
| `retrieval:results` | result_count, scores, source_ids | Retriever |
| `synthesis:started` | query, source_count, format | Synthesizer |
| `synthesis:completed` | claim_count, citation_count, uncertainty_count | Synthesizer |
| `deliberation:started` | question, frame_count, rounds | DeliberationEngine |
| `deliberation:frame_output` | frame_id, position summary | DeliberationEngine |
| `deliberation:critique` | from_frame, to_frame, critique summary | DeliberationEngine |
| `deliberation:completed` | agreement_count, disagreement_count | DeliberationEngine |
| `workspace:read` | path, size | WorkspaceOperator |
| `workspace:write` | path, size, hash | WorkspaceOperator |
| `workspace:execute` | command, exit_code, duration_ms | WorkspaceOperator |
| `workspace:delete` | path | WorkspaceOperator |
| `gate:approval_required` | action, permission_level, resources | Engine |
| `gate:approved` | request_id, modifier | Engine |
| `gate:denied` | request_id | Engine |
| `checkpoint:saved` | checkpoint_id, message_index | CheckpointManager |
| `checkpoint:restored` | checkpoint_id | CheckpointManager |
| `eval:run_started` | task_id, provider, model, skill_pack | EvalRunner |
| `eval:run_completed` | scores, duration_ms | EvalRunner |
| `error:unhandled` | exception type, message, traceback | Any |

### 11.2 Trace event schema

```python
@dataclass
class TraceEvent:
    id: str                          # UUIDv7
    trace_id: str                    # Groups events for one logical run
    session_id: str
    timestamp: datetime              # UTC
    event_type: str                  # From the type table above
    data: dict                       # Event-specific payload
    parent_event_id: str | None = None  # For nested/causal events
```

### 11.3 Trace collector

```python
class TraceCollector:
    """Collects and persists trace events.

    Events are buffered in memory and flushed to the
    database in batches (default: every 100 events or
    every 5 seconds, whichever comes first).

    The collector is thread-safe and async-safe.
    It is injected as a dependency into every component
    that needs to emit events.
    """

    async def emit(self, event: TraceEvent) -> None: ...
    async def flush(self) -> None: ...
    async def get_trace(self, trace_id: str) -> list[TraceEvent]: ...
    async def get_session_events(
        self,
        session_id: str,
        event_types: list[str] | None = None,
        since: datetime | None = None
    ) -> list[TraceEvent]: ...
```

### 11.4 Replay

The replay engine reconstructs a run from its trace events, allowing inspection of what happened, in what order, with what inputs and outputs.

```python
class ReplayEngine:
    """Reconstructs and replays traced runs.

    Replay modes:
    - timeline: chronological event listing with filtering.
    - summary: condensed view of key decisions and outputs.
    - diff: compare two runs of the same task.
    """

    async def timeline(
        self,
        trace_id: str,
        event_types: list[str] | None = None
    ) -> list[TraceEvent]: ...

    async def summary(self, trace_id: str) -> RunSummary: ...

    async def diff(
        self,
        trace_id_a: str,
        trace_id_b: str
    ) -> RunDiff: ...
```

---

## 12. Evaluation Layer

The evaluation layer implements Design Document §5.9, §8.1.F, §12.5, and §18.

### 12.1 Task definition

Evaluation tasks are defined in TOML files in the `tasks/` directory.

```toml
[task]
task_id = "research.summarize_complex_source"
version = "1.0.0"
name = "Summarize Complex Source"
description = "Given a complex multi-source corpus, produce a citation-aware synthesis."
category = "research"               # research | deliberation | workspace | chat
difficulty = "medium"               # easy | medium | hard

[task.input]
type = "corpus"                     # corpus | question | file | command
sources = [
    "tasks/fixtures/research/complex_corpus_01.md",
    "tasks/fixtures/research/complex_corpus_02.md",
    "tasks/fixtures/research/complex_corpus_03.md"
]
query = "Synthesize the key findings across these sources, noting areas of agreement and conflict."

[task.expected]
type = "structured"                 # structured | freeform | exact
min_claims = 5
min_citations = 3
must_include_uncertainty = true
must_cite_all_sources = true

[task.scoring]
scorers = ["citation_accuracy", "source_coverage", "claim_fidelity", "uncertainty_marking"]
weights = { citation_accuracy = 0.3, source_coverage = 0.2, claim_fidelity = 0.35, uncertainty_marking = 0.15 }
```

### 12.2 Scoring framework

```python
class Scorer(Protocol):
    """Interface for evaluation scorers.

    Each scorer evaluates one quality dimension.
    Scorers are composable — the composite scorer
    aggregates individual scores with configurable weights.
    """

    @property
    def scorer_id(self) -> str: ...

    async def score(
        self,
        task: EvalTask,
        result: ExecutionResult,
        trace: list[TraceEvent]
    ) -> Score: ...

@dataclass
class Score:
    scorer_id: str
    value: float                     # 0.0 - 1.0
    explanation: str                 # Why this score
    details: dict | None = None      # Scorer-specific details
```

#### 12.2.1 Built-in scorers

| Scorer ID | Evaluates | Method |
|-----------|-----------|--------|
| `citation_accuracy` | Whether citations actually support their claims | LLM-as-judge against source excerpts |
| `source_coverage` | Whether all relevant sources were used | Set intersection of cited vs. available sources |
| `claim_fidelity` | Whether claims accurately represent sources | LLM-as-judge for semantic fidelity |
| `uncertainty_marking` | Whether conflicting/weak evidence is flagged | Presence and accuracy of uncertainty markers |
| `deliberation_depth` | Whether critique rounds produce substantive challenges | LLM-as-judge on critique quality |
| `rhetoric_detection` | Whether rhetorical devices are correctly identified | Precision/recall against annotated examples |
| `action_safety` | Whether workspace operations respected constraints | Audit trace for permission violations |
| `latency` | End-to-end execution time | Wall clock from trace timestamps |
| `token_efficiency` | Tokens consumed relative to output quality | Tokens / composite score |

### 12.3 Comparator

```python
class Comparator:
    """Side-by-side comparison of evaluation runs.

    Supports comparison across:
    - Models (same task, different providers/models)
    - Skill packs (same task and model, different skills)
    - Workflows (same task, different execution strategies)
    - Versions (same task and config, different platform versions)
    """

    async def compare(
        self,
        run_ids: list[str],
        dimensions: list[str] | None = None  # Specific scorers to compare
    ) -> ComparisonResult: ...
```

### 12.4 Regression detection

```python
class RegressionDetector:
    """Detects performance regressions over time.

    Monitors score distributions across eval runs
    for a given task+provider+skill_pack combination.
    Alerts when scores drop below historical baselines.

    Uses median and IQR (not mean and stddev) for
    robustness to outliers, consistent with Dan's
    preference for medians over averages.
    """

    async def check_regression(
        self,
        task_id: str,
        latest_run_id: str,
        baseline_window: int = 10    # Number of prior runs to compare against
    ) -> RegressionReport: ...
```

---

## 13. API Surface

### 13.1 API framework: FastAPI

**Rationale:** Async-native, automatic OpenAPI schema generation, Pydantic integration for request/response validation, WebSocket support for streaming.

### 13.2 Route structure

```
POST   /api/v1/sessions                     # Create session
GET    /api/v1/sessions                     # List sessions
GET    /api/v1/sessions/{id}                # Get session
PATCH  /api/v1/sessions/{id}                # Update session (pause, resume, config)
POST   /api/v1/sessions/{id}/branch         # Branch session
DELETE /api/v1/sessions/{id}                # Delete session

POST   /api/v1/sessions/{id}/messages       # Send message (chat mode)
GET    /api/v1/sessions/{id}/messages       # Get message history
WS     /api/v1/sessions/{id}/stream         # WebSocket for streaming responses

POST   /api/v1/research/ingest              # Ingest sources
POST   /api/v1/research/retrieve            # Run retrieval query
POST   /api/v1/research/synthesize          # Run synthesis
POST   /api/v1/research/export              # Export artifact

POST   /api/v1/deliberation/run             # Start deliberation
GET    /api/v1/deliberation/{id}            # Get deliberation result
GET    /api/v1/deliberation/{id}/surface    # Get disagreement surface

POST   /api/v1/workspace/list               # List files
POST   /api/v1/workspace/read               # Read file
POST   /api/v1/workspace/write              # Write file (gated)
POST   /api/v1/workspace/patch              # Propose patch
POST   /api/v1/workspace/patch/{id}/apply   # Apply approved patch
POST   /api/v1/workspace/execute            # Execute command (gated)

GET    /api/v1/traces/{trace_id}            # Get trace events
GET    /api/v1/traces/{trace_id}/summary    # Get run summary
POST   /api/v1/traces/diff                  # Compare two runs

GET    /api/v1/approvals/pending            # List pending approval gates
POST   /api/v1/approvals/{id}               # Approve or deny

POST   /api/v1/eval/run                     # Start eval run
GET    /api/v1/eval/runs                    # List eval runs
GET    /api/v1/eval/runs/{id}               # Get eval run result
POST   /api/v1/eval/compare                 # Compare eval runs
POST   /api/v1/eval/regression              # Check for regression

GET    /api/v1/skills                       # List available skills
GET    /api/v1/skills/{id}                  # Get skill details
GET    /api/v1/skills/packs                 # List skill packs
GET    /api/v1/skills/packs/{id}            # Get skill pack details

GET    /api/v1/providers                    # List configured providers
GET    /api/v1/providers/{id}/health        # Provider health check

GET    /api/v1/config                       # Get current config (redacted secrets)
```

### 13.3 API versioning

The API is versioned at the path level (`/api/v1/`). Breaking changes to request/response schemas require a major version bump. The version in the URL path increments independently of the platform SemVer version, following its own SemVer semantics documented in the API changelog.

### 13.4 Request/response conventions

- All request and response bodies are JSON.
- All responses include a top-level `status` field: `"ok"` or `"error"`.
- Error responses include `status: "error"`, `error_code` (machine-readable), and `message` (human-readable).
- List endpoints support `limit` (default 50, max 200) and `cursor` (opaque pagination token) parameters.
- All timestamps are ISO 8601 UTC.
- All IDs are UUIDv7 strings.

```python
# Standard response envelope
class APIResponse(BaseModel, Generic[T]):
    status: str = "ok"
    data: T | None = None
    error_code: str | None = None
    message: str | None = None
    pagination: PaginationInfo | None = None

class PaginationInfo(BaseModel):
    cursor: str | None = None
    has_more: bool = False
    total: int | None = None         # Omitted for expensive counts
```

### 13.5 WebSocket protocol

The streaming WebSocket at `/api/v1/sessions/{id}/stream` uses a JSON-lines protocol. Each line is a JSON object with a `type` field:

```json
{"type": "text", "content": "partial response text"}
{"type": "tool_call", "tool": "retrieval", "arguments": {"query": "..."}}
{"type": "tool_result", "tool": "retrieval", "result": {"..."}}
{"type": "citation", "claim": "...", "source_id": "...", "excerpt": "..."}
{"type": "approval_required", "request": {"id": "...", "action": "...", "..."}}
{"type": "error", "error_code": "...", "message": "..."}
{"type": "done", "message_id": "...", "tokens_in": 1234, "tokens_out": 567}
```

---

## 14. Engineering Standards

### 14.1 Code style

- **Formatter:** `ruff format` (Black-compatible).
- **Linter:** `ruff check` with a curated rule set (see `pyproject.toml`).
- **Type checking:** `mypy` in strict mode. All public interfaces have complete type annotations.
- **Docstrings:** Google style. Required on all public classes, methods, and functions.
- **Line length:** 100 characters.

### 14.2 Commenting discipline

Per Dan's preference for verbose commenting: every module has a module-level docstring explaining its purpose and architectural role. Every class has a class-level docstring. Every non-trivial function has inline comments explaining the why, not the what. Comments are mandatory at decision points, boundary crossings, and error handling paths.

### 14.3 Import discipline

Enforced by `ruff` import linting rules:

- No circular imports.
- No upward dependency violations (Capability importing from Orchestration, etc.).
- No wildcard imports.
- Standard library, then third-party, then internal, with blank line separators.
- Internal imports use absolute paths from `caw` package root.

### 14.4 Error handling

Per Dan's preference for comprehensive error handling:

- All exceptions inherit from a base `CAWError` class.
- External API errors are caught at the protocol layer and wrapped in `ProviderError`.
- File system errors are caught at the workspace layer and wrapped in `WorkspaceError`.
- Validation errors use `ValidationError` with specific field-level detail.
- Unhandled exceptions are caught at the engine level, logged with full traceback, emitted as `error:unhandled` trace events, and surfaced to the user as structured error responses.
- No bare `except:` clauses. Every `except` names specific exception types.
- `finally` blocks ensure cleanup (connections, file handles, locks).

```python
class CAWError(Exception):
    """Base exception for all CAW errors."""
    def __init__(self, message: str, code: str, details: dict | None = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ProviderError(CAWError): ...
class WorkspaceError(CAWError): ...
class SkillError(CAWError): ...
class ValidationError(CAWError): ...
class PermissionError(CAWError): ...
class CheckpointError(CAWError): ...
class EvaluationError(CAWError): ...
```

### 14.5 Logging

- **Library:** Python stdlib `logging` module with structured JSON output in production, human-readable in development.
- **Log levels:** Follow config `log_level`. Default `INFO` for production, `DEBUG` for development.
- **Sensitive data:** API keys, tokens, and user content are never logged at any level. Provider responses are logged at `DEBUG` with content truncated to 200 characters.
- **Correlation:** Every log entry includes `session_id` and `trace_id` where applicable.

### 14.6 Testing

- **Unit tests:** `pytest` with `pytest-asyncio` for async code. Target: all public interfaces, all error paths, all validation logic.
- **Integration tests:** Test cross-layer interactions (engine → capability → protocol → mock provider). Use `pytest` fixtures for database setup/teardown.
- **Fixtures:** Stored in `tests/fixtures/`. Include sample skill documents, config files, source corpora, and expected outputs.
- **Coverage:** Measured but not gated on a specific percentage. Coverage reports guide where to add tests, not whether to merge.
- **Mocking:** Provider calls are mocked in unit and integration tests. A `MockProvider` implementing the `ModelProvider` protocol returns configurable canned responses.

### 14.7 File path handling

Per Dan's explicit preference: all file path operations use `pathlib.Path`. Paths with spaces and special characters are handled correctly throughout. String concatenation for paths is prohibited. All path operations that cross trust boundaries (user input → file system) are validated and sanitized.

```python
# Always
path = Path(user_input).resolve()
if not path.is_relative_to(allowed_base):
    raise WorkspaceError("Path outside allowed workspace", "path_violation")

# Never
path = base_dir + "/" + user_input  # PROHIBITED
```

---

## 15. State Flows

### 15.1 Session lifecycle

```
                    ┌──────────┐
                    │ CREATED  │
                    └────┬─────┘
                         │ first message or mode activation
                         ▼
                    ┌──────────┐
         ┌──────── │  ACTIVE   │ ────────┐
         │         └──┬──┬──┬──┘         │
         │            │  │  │            │
     user pause   branch │ complete   fatal error
         │            │  │  │            │
         ▼            │  │  ▼            ▼
    ┌──────────┐      │  │ ┌──────────┐ ┌──────────┐
    │  PAUSED  │      │  │ │COMPLETED │ │  FAILED  │
    └────┬─────┘      │  │ └──────────┘ └──────────┘
         │            │  │
     user resume      │  └─── checkpoint save
         │            │            │
         └────────────┘       ┌────▼───────┐
                              │CHECKPOINTED│
                              └────┬───────┘
                                   │ restore
                                   ▼
                              ┌──────────┐
                              │  ACTIVE   │
                              └──────────┘
```

### 15.2 Request execution flow

```
User Request
     │
     ▼
┌─────────────────┐
│  Validate Input  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Resolve Skills   │──── emit: skill:resolved
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Route Provider  │──── emit: routing:decision
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Check Permissions │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Gated?  │
    └────┬────┘
     yes │    no
         ▼     │
┌──────────────┐│
│Request Approval││  emit: gate:approval_required
└───────┬──────┘│
        │       │
   ┌────┴────┐  │
   │Approved?│  │
   └────┬────┘  │
   yes  │  no   │
        │  │    │
        │  ▼    │
        │ DENY  │
        │       │
        ▼       ▼
┌─────────────────┐
│Execute Capability│──── emit: provider:request, tool:invocation, etc.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Store Results   │──── emit: provider:response
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Checkpoint (if    │──── emit: checkpoint:saved (conditional)
│ workflow step)   │
└────────┬────────┘
         │
         ▼
    Return Result
```

### 15.3 Deliberation flow

```
Question + Frame Configs
         │
         ▼
┌────────────────────┐
│ Resolve frame skills│   One skill per frame
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Generate initial    │   Each frame produces position
│ positions (parallel)│   May use different providers
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Critique round N    │   Each frame critiques others
│ (sequential or      │   emit: deliberation:critique
│  parallel per config)│
└────────┬───────────┘
         │
    ┌────┴────┐
    │More     │
    │rounds?  │
    └────┬────┘
    yes  │  no
    ▲    │   │
    │    │   ▼
    └────┘ ┌────────────────────┐
           │ Rhetoric analysis   │   Optional
           │ (bias, sophistry,   │   emit: deliberation:rhetoric
           │  inconsistency)     │
           └────────┬───────────┘
                    │
                    ▼
           ┌────────────────────┐
           │ Build disagreement  │
           │ surface             │
           └────────┬───────────┘
                    │
                    ▼
           ┌────────────────────┐
           │ Synthesis (optional)│
           └────────┬───────────┘
                    │
                    ▼
           Return DeliberationResult
```

---

## 16. Dependency Inventory

### 16.1 Core dependencies

| Package | Purpose | Version Constraint |
|---------|---------|-------------------|
| `fastapi` | API framework | `>=0.115` |
| `uvicorn` | ASGI server | `>=0.30` |
| `pydantic` | Validation and schemas | `>=2.0` |
| `aiosqlite` | Async SQLite access | `>=0.20` |
| `httpx` | Async HTTP client (provider calls) | `>=0.27` |
| `anthropic` | Anthropic API SDK | `>=0.40` |
| `openai` | OpenAI API SDK | `>=1.50` |
| `click` | CLI framework | `>=8.0` |
| `rich` | Terminal formatting and progress | `>=13.0` |
| `websockets` | WebSocket support | `>=12.0` |

### 16.2 Research dependencies

| Package | Purpose | Version Constraint |
|---------|---------|-------------------|
| `pypdf` | PDF text extraction | `>=4.0` |
| `python-docx` | DOCX reading | `>=1.0` |
| `beautifulsoup4` | HTML parsing | `>=4.12` |
| `markdownify` | HTML to Markdown conversion | `>=0.12` |
| `tiktoken` | Token counting (OpenAI models) | `>=0.7` |
| `anthropic-tokenizer` | Token counting (Claude models) | latest |

### 16.3 Optional dependencies

| Package | Purpose | Condition |
|---------|---------|-----------|
| `sentence-transformers` | Local embedding generation | If not using API embeddings |
| `numpy` | Vector operations for retrieval | If using local embeddings |
| `paramiko` | SSH/SFTP for remote workspaces | If remote workspace enabled |

### 16.4 Development dependencies

| Package | Purpose |
|---------|---------|
| `pytest` | Test framework |
| `pytest-asyncio` | Async test support |
| `pytest-cov` | Coverage reporting |
| `ruff` | Linting and formatting |
| `mypy` | Static type checking |
| `pre-commit` | Git hook management |

---

## 17. Security Considerations

### 17.1 API key management

API keys are never stored in configuration files, database, or source control. They are read from environment variables at runtime. The config file stores only the environment variable name (`api_key_env`), never the value.

### 17.2 Input sanitization

- All user-provided file paths are resolved and validated against allowed workspace boundaries.
- All user-provided shell commands are logged before execution and require explicit approval.
- SQL injection is prevented by exclusive use of parameterized queries (no string formatting in SQL).
- The API validates all input against Pydantic schemas before processing.

### 17.3 Workspace sandboxing

In `strict` mode, file operations are restricted to paths listed in `workspace.allowed_paths`. In `permissive` mode, all paths are accessible but mutations still require approval. In `none` mode, no restrictions apply (development only, not recommended).

### 17.4 Network exposure

The API server binds to `127.0.0.1` by default (localhost only). Binding to `0.0.0.0` for network access requires explicit configuration and is logged as a warning on startup.

---

## 18. Performance Considerations

### 18.1 Streaming

All provider responses that support streaming use streaming by default. The orchestration engine passes stream chunks through to the interaction layer without buffering the full response. This ensures the user sees output incrementally.

### 18.2 Trace buffering

Trace events are buffered and batch-written to avoid per-event database overhead. The buffer flushes every 100 events or every 5 seconds. A `flush()` is called on session completion and graceful shutdown.

### 18.3 Embedding computation

Embedding generation is the most compute-intensive local operation. It is performed asynchronously, does not block ingestion acknowledgment, and can be deferred or skipped if a lighter retrieval strategy (keyword-only) is configured.

### 18.4 SQLite optimization

- WAL mode enabled on connection.
- `PRAGMA journal_mode=WAL;`
- `PRAGMA synchronous=NORMAL;` (adequate for local single-user; not used for shared deployment).
- `PRAGMA cache_size=-64000;` (64MB cache).
- Indexes on all foreign keys and query-frequent columns (defined in §8.1).

---

## 19. Deployment

### 19.1 Local deployment (primary)

```bash
# Install
uv sync

# Configure
cp config/example.toml ~/.config/caw/config.toml
# Edit config with provider API keys, workspace paths, etc.

# Initialize database
caw db init

# Start
caw serve
# → API available at http://127.0.0.1:8420
```

### 19.2 CLI interface

```bash
caw serve                            # Start API server
caw chat                             # Interactive chat in terminal
caw research ingest <path>           # Ingest sources
caw research query "<question>"      # Run retrieval + synthesis
caw deliberate "<question>"          # Run deliberation
caw eval run <task_id>               # Run evaluation task
caw eval compare <run_id> <run_id>   # Compare eval runs
caw db init                          # Initialize database
caw db migrate                       # Run pending migrations
caw db backup                        # Backup database
caw skills list                      # List available skills
caw skills validate <path>           # Validate a skill document
caw config show                      # Show current config (secrets redacted)
caw version                          # Show version
```

### 19.3 Docker deployment (optional)

A `Dockerfile` and `docker-compose.yml` are provided for containerized deployment. The database and configuration are mounted as volumes for persistence.

---

## 20. Extension Points

The architecture supports extension at defined boundaries without requiring changes to core code:

| Extension Point | Mechanism | Example |
|----------------|-----------|---------|
| New model provider | Implement `ModelProvider` protocol, add config entry | Add Google Vertex AI |
| New tool server | Implement `ToolServer` protocol or connect MCP server | Add filesystem watcher |
| New skill | Add Markdown file to `skills/user/` | Custom analysis perspective |
| New skill pack | Add TOML file to `skills/packs/` | Domain-specific bundle |
| New evaluation scorer | Implement `Scorer` protocol, register | Custom quality metric |
| New evaluation task | Add TOML file to `tasks/` | New benchmark scenario |
| New export format | Add exporter to `capabilities/research/export.py` | LaTeX output |
| New retrieval strategy | Add strategy to `capabilities/research/retrieve.py` | Graph-based retrieval |

---

## 21. What This Specification Does Not Cover

The following are explicitly deferred to the Atomic Roadmap or future specification revisions:

- **Frontend implementation details** — component hierarchy, state management, design system. Deferred until the API stabilizes.
- **Multi-user support** — authentication, authorization, multi-tenancy. Deferred per Design Document §20.4.
- **App-store or marketplace mechanics** — skill distribution, versioning across users. Deferred per Design Document §8.2.
- **Specific model fine-tuning or training** — the platform uses models as-is via APIs.
- **Hardware integration** — GPU management, edge deployment. Deferred per Design Document §8.2.
- **Mobile interfaces** — out of scope for initial waves.

---

## 22. Specification Versioning

This document follows SemVer. The current version is `1.0.0`.

Changes to this specification are tracked in the project `CHANGELOG.md`. Any change to a module interface, data model, or protocol surface described here requires a version bump to this specification and a corresponding entry in the changelog.

| Version | Date | Change Summary |
|---------|------|----------------|
| 1.0.0 | 2026-03-08 | Initial specification |
