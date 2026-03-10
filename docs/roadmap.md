# Atomic Roadmap

## Canonical Agent Workbench

**Version:** 1.0.0
**Status:** Draft
**Companion to:** Design Document v1.0, Technical Specification v1.0.0
**Date:** 2026-03-08

---

## 0. How to Read This Document

This roadmap is the execution spine for the Canonical Agent Workbench. It is designed so that an implementation agent of moderate capability (Gemini Flash, Haiku, DeepSeek, or equivalent) can pick up any work package and produce exactly the specified output without needing to infer intent.

### 0.1 Structure

The roadmap is organized into **milestones**. Each milestone contains **work packages** (WPs). Work packages are the atomic unit of implementation — each one produces a specific, testable deliverable.

### 0.2 Work package format

Every work package specifies:

- **ID**: `M{milestone}-WP{number}` — globally unique, stable reference.
- **Title**: What this work package produces.
- **Dependencies**: Which other WPs must be complete before this one can start. `none` means it can start immediately within its milestone.
- **Files**: Exact file paths to create or modify. Every file listed must exist after the WP is complete.
- **Specification**: Precisely what the code must do. Includes function signatures, class interfaces, data structures, and behavioral requirements.
- **Acceptance criteria**: A numbered list of testable conditions. The WP is complete if and only if all criteria pass.
- **Tests**: Exact test file paths and what each test must verify.
- **Complexity**: `S` (< 100 lines), `M` (100–400 lines), `L` (400+ lines).

### 0.3 Dependency rules

- Work packages within a milestone may depend on earlier WPs in the same milestone or on WPs from earlier milestones.
- Work packages never depend on WPs in later milestones.
- If a WP has no dependencies listed, it depends only on the milestone's prerequisites (the prior milestone being complete).
- The dependency graph is a DAG. There are no cycles.

### 0.4 Ordering rationale

The milestone order follows the dependency graph from the Technical Specification §4.1:

1. **M0 (Bootstrap)**: Repository scaffold, tooling. Everything else depends on this.
2. **M1 (Foundation)**: Configuration, storage, core data models. Every layer reads config and writes to storage.
3. **M2 (Protocol)**: Provider abstraction. Capabilities need to call models.
4. **M3 (Skills)**: Skill loading and resolution. Orchestration needs skills before it can run.
5. **M4 (Traces)**: Trace collection. Everything emits traces; this must exist before the first real execution.
6. **M5 (Orchestration)**: Engine, sessions, routing, permissions. Ties the lower layers together.
7. **M6 (Chat)**: First vertical slice. Proves the entire stack works end-to-end.
8. **M7 (API)**: HTTP/WebSocket surface. Makes the system externally usable.
9. **M8 (Research)**: Ingestion, retrieval, synthesis, export. First major capability pillar.
10. **M9 (Deliberation)**: Multi-frame reasoning, rhetoric analysis. Second capability pillar.
11. **M10 (Workspace)**: File operations, patching, command execution. Third capability pillar.
12. **M11 (Evaluation)**: Task runner, scorers, comparison, regression. The hidden pillar.
13. **M12 (Integration)**: Cross-cutting integration, CLI completion, hardening.

### 0.5 Implementation conventions

These apply to every work package unless explicitly overridden:

- **Language**: Python 3.11+.
- **Formatting**: `ruff format` (Black-compatible), 100 char line length.
- **Type annotations**: All public interfaces. `mypy --strict` must pass.
- **Docstrings**: Google style on all public classes, methods, and functions.
- **Commenting**: Verbose. Explain the why at decision points, boundary crossings, and error paths.
- **Error handling**: Specific exception types inheriting from `CAWError`. No bare `except:`. Always name exception types.
- **File paths**: Always `pathlib.Path`. Never string concatenation for paths.
- **Imports**: Absolute from `caw` package root. No wildcards. No circular imports.
- **Tests**: `pytest` + `pytest-asyncio`. Test file mirrors source file path: `src/caw/core/engine.py` → `tests/unit/core/test_engine.py`.
- **Logging**: Use `logging.getLogger(__name__)` per module. Include `session_id` and `trace_id` in structured context where applicable.

---

## Milestone 0: Project Bootstrap

**Goal:** A working repository with tooling, dependency management, and project scaffold. After this milestone, `uv sync` succeeds, `ruff check` passes on all files, `mypy` passes, and `pytest` runs (with zero tests).

**Prerequisites:** None. This is the starting point.

---

### M0-WP01: Repository initialization

**Dependencies:** none
**Complexity:** S

**Files to create:**

```
canonical-agent-workbench/
├── .gitignore
├── .python-version
├── LICENSE
├── README.md
├── pyproject.toml
└── .pre-commit-config.yaml
```

**Specification:**

`.gitignore`: Standard Python gitignore. Additionally ignore: `*.db`, `*.db-wal`, `*.db-shm`, `skills/user/`, `config/local.toml`, `.env`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `*.egg-info/`.

`.python-version`: Contains `3.11`.

`LICENSE`: MIT license with current year and "Canonical Agent Workbench Contributors" as copyright holder.

`README.md`: Project name, one-line description from Technical Specification §1, "under construction" notice, link to `docs/` for design document and technical specification. No installation instructions yet (those come in M12).

`pyproject.toml`:
```toml
[project]
name = "canonical-agent-workbench"
version = "0.1.0"
description = "A human-directed platform for high-fidelity compression, analysis, deliberation, and action across information and real workspaces."
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "ruff>=0.8",
    "mypy>=1.13",
    "pre-commit>=4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/caw"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "RUF",    # ruff-specific
]

[tool.ruff.lint.isort]
known-first-party = ["caw"]

[tool.mypy]
strict = true
python_version = "3.11"
mypy_path = "src"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: []
        args: [--strict]
```

**Acceptance criteria:**

1. `uv sync --all-extras` completes without error.
2. `ruff check .` exits 0.
3. `ruff format --check .` exits 0.
4. `pyproject.toml` parses without error and `project.version` is `"0.1.0"`.
5. `.gitignore` includes all specified patterns.

**Tests:** None (no code to test yet).

---

### M0-WP02: Directory scaffold

**Dependencies:** M0-WP01
**Complexity:** S

**Files to create:**

```
src/
└── caw/
    ├── __init__.py
    ├── __version__.py
    ├── core/__init__.py
    ├── skills/__init__.py
    ├── storage/__init__.py
    ├── capabilities/__init__.py
    ├── capabilities/research/__init__.py
    ├── capabilities/deliberation/__init__.py
    ├── capabilities/workspace/__init__.py
    ├── capabilities/chat/__init__.py
    ├── protocols/__init__.py
    ├── traces/__init__.py
    ├── evaluation/__init__.py
    ├── api/__init__.py
    └── cli/__init__.py

skills/
├── builtin/.gitkeep
├── packs/.gitkeep
└── user/.gitkeep

tasks/
├── benchmarks/.gitkeep
└── regression/.gitkeep

tests/
├── __init__.py
├── unit/__init__.py
├── integration/__init__.py
├── fixtures/.gitkeep
└── conftest.py

config/
├── default.toml
└── example.toml

docs/
├── design_document.md
├── technical_specification.md
└── roadmap.md

scripts/
└── .gitkeep
```

**Specification:**

`src/caw/__init__.py`: Empty except for a docstring: `"""Canonical Agent Workbench."""`

`src/caw/__version__.py`:
```python
"""Single source of truth for the CAW version string."""

__version__ = "0.1.0"
```

All other `__init__.py` files: Empty except for a module docstring naming the package (e.g., `"""Orchestration layer for CAW."""`).

`tests/conftest.py`: Empty initially. Will accumulate shared fixtures as tests are added.

`config/default.toml`: The full default configuration from Technical Specification §5.1.2.

`config/example.toml`: Same as `default.toml` but with inline TOML comments explaining every field.

`docs/`: Copy the design document, technical specification, and this roadmap into the `docs/` directory.

**Acceptance criteria:**

1. `python -c "import caw; print(caw.__version__.__version__)"` prints `0.1.0`.
2. `python -c "from caw.core import __doc__"` does not raise.
3. `python -c "from caw.capabilities.research import __doc__"` does not raise.
4. All `__init__.py` files have docstrings.
5. `config/default.toml` parses as valid TOML.
6. `pytest` runs and reports 0 tests collected (no failures).
7. `ruff check src/ tests/` exits 0.
8. `mypy src/` exits 0.

**Tests:** None yet.

---

### M0-WP03: CHANGELOG initialization

**Dependencies:** M0-WP01
**Complexity:** S

**Files to create:**

```
CHANGELOG.md
```

**Specification:**

Follow Keep a Changelog format (https://keepachangelog.com/). Initialize with:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project scaffold with directory structure, tooling configuration, and dependency management.
- Design document, technical specification, and atomic roadmap in `docs/`.
- Default and example configuration files.
```

**Acceptance criteria:**

1. `CHANGELOG.md` exists at repository root.
2. File contains `[Unreleased]` section.
3. File references SemVer and Keep a Changelog.

**Tests:** None.

---

## Milestone 1: Foundation

**Goal:** The configuration system loads and validates config from the full precedence hierarchy. The storage layer initializes the database, runs migrations, and provides async repository access to all core data models. After this milestone, the system can read its own configuration and persist structured data.

**Prerequisites:** Milestone 0 complete.

---

### M1-WP01: Error base classes

**Dependencies:** none
**Complexity:** S

**Files to create:**

```
src/caw/errors.py
tests/unit/test_errors.py
```

**Specification:**

Define the base exception hierarchy from Technical Specification §14.4:

```python
"""Base exception hierarchy for CAW.

All CAW-specific exceptions inherit from CAWError.
Each layer has its own exception subclass.
"""


class CAWError(Exception):
    """Base exception for all CAW errors.

    Attributes:
        message: Human-readable error description.
        code: Machine-readable error code string (e.g., "provider_timeout").
        details: Optional dictionary with additional context.
    """

    def __init__(
        self,
        message: str,
        code: str,
        details: dict[str, object] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"


class ConfigError(CAWError):
    """Configuration loading or validation error."""
    ...

class StorageError(CAWError):
    """Database or file storage error."""
    ...

class ProviderError(CAWError):
    """Model provider communication error."""
    ...

class SkillError(CAWError):
    """Skill loading, validation, or resolution error."""
    ...

class WorkspaceError(CAWError):
    """File or workspace operation error."""
    ...

class PermissionError_(CAWError):
    """Permission check or approval gate error.

    Named with trailing underscore to avoid shadowing
    the builtin PermissionError.
    """
    ...

class ValidationError_(CAWError):
    """Input validation error.

    Named with trailing underscore to avoid shadowing
    the pydantic ValidationError.
    """
    ...

class CheckpointError(CAWError):
    """Checkpoint save or restore error."""
    ...

class EvaluationError(CAWError):
    """Evaluation task or scoring error."""
    ...

class TraceError(CAWError):
    """Trace collection or retrieval error."""
    ...
```

**Acceptance criteria:**

1. All exception classes are importable from `caw.errors`.
2. `CAWError("msg", "code")` stores `.message`, `.code`, `.details` correctly.
3. `CAWError("msg", "code", {"key": "val"}).details == {"key": "val"}`.
4. All subclasses are instances of both `CAWError` and `Exception`.
5. `repr()` produces the specified format.
6. `ruff check` and `mypy` pass.

**Tests (`tests/unit/test_errors.py`):**

- Test `CAWError` construction with and without details.
- Test `repr` output format.
- Test that each subclass is an instance of `CAWError`.
- Test that each subclass is an instance of `Exception`.
- Test that `details` defaults to empty dict when not provided.

---

### M1-WP02: Configuration system

**Dependencies:** M1-WP01
**Complexity:** L

**Files to create:**

```
src/caw/core/config.py
tests/unit/core/test_config.py
tests/fixtures/config/
tests/fixtures/config/valid_minimal.toml
tests/fixtures/config/valid_full.toml
tests/fixtures/config/invalid_sandbox_mode.toml
tests/fixtures/config/invalid_missing_provider.toml
```

**Specification:**

Implement the configuration system from Technical Specification §5.1.

The module must:

1. Define Pydantic v2 `BaseModel` subclasses for every configuration section: `GeneralConfig`, `StorageConfig`, `ProviderConfig`, `RoutingConfig`, `SkillsConfig`, `WorkspaceConfig`, `EvaluationConfig`, `APIConfig`, and the top-level `CAWConfig`.

2. Implement the five-level precedence hierarchy (Technical Specification §5.1.1):
   - Runtime overrides (passed as a `dict`)
   - Environment variables (prefixed `CAW_`, nested with `__`)
   - User config file (`~/.config/caw/config.toml`)
   - Project config file (`./caw.toml`)
   - Default config file (shipped with package)

3. Implement a `load_config()` function:

```python
def load_config(
    overrides: dict[str, object] | None = None,
    user_config_path: Path | None = None,
    project_config_path: Path | None = None,
    default_config_path: Path | None = None,
) -> CAWConfig:
    """Load and validate configuration from the full precedence hierarchy.

    Process:
    1. Load default config from default_config_path (or bundled default).
    2. If project_config_path exists, deep-merge its values on top.
    3. If user_config_path exists, deep-merge its values on top.
    4. Read CAW_-prefixed environment variables and deep-merge.
    5. If overrides dict is provided, deep-merge on top.
    6. Expand path variables (${data_dir}, ~).
    7. Validate the merged result against CAWConfig.
    8. Return the validated config.

    Raises:
        ConfigError: If the merged config fails validation,
            with a message listing every validation failure.
    """
    ...
```

4. Implement path variable expansion: `${data_dir}` in path fields is replaced with the resolved value of `general.data_dir`. Tilde (`~`) is expanded via `Path.expanduser()`.

5. Implement deep merge: nested dicts are merged recursively. Lists are replaced, not appended. Scalar values are overwritten.

**Pydantic model details:**

```python
class GeneralConfig(BaseModel):
    version: str = "1.0.0"
    log_level: str = "INFO"
    data_dir: str = "~/.local/share/caw"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}, got '{v}'")
        return v.upper()

class StorageConfig(BaseModel):
    db_path: str = "${data_dir}/caw.db"
    trace_dir: str = "${data_dir}/traces"
    artifact_dir: str = "${data_dir}/artifacts"

class ProviderConfig(BaseModel):
    type: str                          # anthropic | openai | openai_compatible
    api_key_env: str = ""
    default_model: str
    max_tokens: int = 4096
    timeout_seconds: int = 120
    base_url: str | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"anthropic", "openai", "openai_compatible"}
        if v not in allowed:
            raise ValueError(f"provider type must be one of {allowed}, got '{v}'")
        return v

class RoutingConfig(BaseModel):
    strategy: str = "config"
    fallback_chain: list[str] = []

    @field_validator("strategy")
    @classmethod
    def validate_strategy(cls, v: str) -> str:
        allowed = {"config", "cost", "capability", "latency"}
        if v not in allowed:
            raise ValueError(f"routing strategy must be one of {allowed}, got '{v}'")
        return v

class SkillsConfig(BaseModel):
    builtin_dir: str = "skills/builtin"
    user_dir: str = "skills/user"
    packs_dir: str = "skills/packs"

class WorkspaceConfig(BaseModel):
    sandbox_mode: str = "permissive"
    allowed_paths: list[str] = ["~", "/tmp"]
    confirm_writes: bool = True
    confirm_deletes: bool = True
    confirm_executions: bool = True

    @field_validator("sandbox_mode")
    @classmethod
    def validate_sandbox_mode(cls, v: str) -> str:
        allowed = {"strict", "permissive", "none"}
        if v not in allowed:
            raise ValueError(f"sandbox_mode must be one of {allowed}, got '{v}'")
        return v

class EvaluationConfig(BaseModel):
    tasks_dir: str = "tasks"
    results_dir: str = "${data_dir}/eval_results"
    default_scorer: str = "composite"

class APIConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8420
    cors_origins: list[str] = ["http://localhost:3000"]

class CAWConfig(BaseModel):
    general: GeneralConfig = GeneralConfig()
    storage: StorageConfig = StorageConfig()
    providers: dict[str, ProviderConfig] = {}
    routing: RoutingConfig = RoutingConfig()
    skills: SkillsConfig = SkillsConfig()
    workspace: WorkspaceConfig = WorkspaceConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    api: APIConfig = APIConfig()
```

**Acceptance criteria:**

1. `load_config()` with no arguments returns a valid `CAWConfig` with all defaults.
2. `load_config()` with a valid TOML override file merges correctly.
3. Environment variables `CAW_GENERAL__LOG_LEVEL=DEBUG` override the config.
4. Path variables `${data_dir}` are expanded in all path fields.
5. Tilde `~` is expanded to the user's home directory.
6. Invalid `sandbox_mode` raises `ConfigError` with a message containing the invalid value.
7. Invalid `log_level` raises `ConfigError`.
8. Invalid `provider.type` raises `ConfigError`.
9. Deep merge replaces lists, merges dicts, overwrites scalars.
10. `ruff check` and `mypy` pass.

**Tests (`tests/unit/core/test_config.py`):**

- `test_load_defaults`: Load with no files, verify all default values.
- `test_load_from_file`: Load a valid TOML file, verify overridden values.
- `test_precedence_env_over_file`: Set env var and file, verify env wins.
- `test_precedence_override_over_env`: Set override dict, env, and file, verify override wins.
- `test_path_expansion_data_dir`: Verify `${data_dir}` is replaced.
- `test_path_expansion_tilde`: Verify `~` is expanded.
- `test_invalid_sandbox_mode`: Verify `ConfigError` raised with descriptive message.
- `test_invalid_log_level`: Verify `ConfigError` raised.
- `test_invalid_provider_type`: Verify `ConfigError` raised.
- `test_deep_merge_dicts`: Verify nested dict merge.
- `test_deep_merge_lists_replace`: Verify lists are replaced not appended.
- `test_unknown_keys_no_crash`: Verify unknown keys in TOML do not cause errors (logged as warnings).

**Fixture files:**

`tests/fixtures/config/valid_minimal.toml`:
```toml
[general]
log_level = "DEBUG"
```

`tests/fixtures/config/valid_full.toml`: Full config with all sections populated.

`tests/fixtures/config/invalid_sandbox_mode.toml`:
```toml
[workspace]
sandbox_mode = "invalid_value"
```

`tests/fixtures/config/invalid_missing_provider.toml`:
```toml
[providers.test]
# missing required field: type
default_model = "test-model"
```

---

### M1-WP03: Core data models

**Dependencies:** M1-WP01
**Complexity:** M

**Files to create:**

```
src/caw/models.py
tests/unit/test_models.py
```

**Specification:**

Define all core data models from Technical Specification §6.2, §8.1, and §9 as Python `dataclasses`. These are the shared vocabulary of the system — every layer uses them.

The module must define:

```python
"""Core data models for CAW.

These dataclasses define the shared vocabulary used across all layers.
They are pure data containers with no business logic. Serialization
to/from database rows and API schemas happens in the respective layers.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utcnow() -> datetime:
    """Return current UTC time. Extracted for testability."""
    return datetime.now(timezone.utc)


def _generate_id() -> str:
    """Generate a UUIDv7 string. Extracted for testability."""
    import uuid
    # UUIDv7 is available in Python 3.14+; for 3.11-3.13 use uuid6 package
    # or fall back to uuid4 with timestamp prefix for ordering.
    # Implementation note: use uuid6.uuid7() if available, else uuid4().
    try:
        import uuid6
        return str(uuid6.uuid7())
    except ImportError:
        return str(uuid.uuid4())


# --- Enums ---

class SessionState(str, enum.Enum):
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    CHECKPOINTED = "checkpointed"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionMode(str, enum.Enum):
    CHAT = "chat"
    RESEARCH = "research"
    DELIBERATION = "deliberation"
    WORKSPACE = "workspace"
    ARENA = "arena"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ArtifactType(str, enum.Enum):
    REPORT = "report"
    PATCH = "patch"
    FILE = "file"
    EXPORT = "export"
    EVALUATION_RESULT = "evaluation_result"


class PermissionLevel(str, enum.Enum):
    READ = "read"
    SUGGEST = "suggest"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


# --- Core Models ---

@dataclass
class Session:
    id: str = field(default_factory=_generate_id)
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    state: SessionState = SessionState.CREATED
    mode: SessionMode = SessionMode.CHAT
    parent_id: str | None = None
    config_overrides: dict[str, object] = field(default_factory=dict)
    active_skills: list[str] = field(default_factory=list)
    active_skill_pack: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class Message:
    id: str = field(default_factory=_generate_id)
    session_id: str = ""
    sequence_num: int = 0
    role: MessageRole = MessageRole.USER
    content: str = ""
    model: str | None = None
    provider: str | None = None
    token_count_in: int | None = None
    token_count_out: int | None = None
    created_at: datetime = field(default_factory=_utcnow)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class Artifact:
    id: str = field(default_factory=_generate_id)
    session_id: str = ""
    type: ArtifactType = ArtifactType.FILE
    name: str = ""
    path: str | None = None
    content: str | None = None
    content_hash: str | None = None
    created_at: datetime = field(default_factory=_utcnow)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class Source:
    id: str = field(default_factory=_generate_id)
    session_id: str | None = None
    type: str = ""                     # file | url | text | api
    uri: str | None = None
    title: str | None = None
    content: str | None = None
    content_hash: str | None = None
    created_at: datetime = field(default_factory=_utcnow)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class Citation:
    id: str = field(default_factory=_generate_id)
    message_id: str = ""
    source_id: str = ""
    claim: str = ""
    excerpt: str | None = None
    confidence: float | None = None
    location: str | None = None
    created_at: datetime = field(default_factory=_utcnow)


@dataclass
class TraceEvent:
    id: str = field(default_factory=_generate_id)
    trace_id: str = ""
    session_id: str = ""
    timestamp: datetime = field(default_factory=_utcnow)
    event_type: str = ""
    data: dict[str, object] = field(default_factory=dict)
    parent_event_id: str | None = None


@dataclass
class ApprovalRequest:
    id: str = field(default_factory=_generate_id)
    session_id: str = ""
    action: str = ""
    permission_level: PermissionLevel = PermissionLevel.WRITE
    resources: list[str] = field(default_factory=list)
    reversible: bool = False
    preview: str | None = None
    timeout_seconds: int = 300


@dataclass
class ApprovalResponse:
    request_id: str = ""
    approved: bool = False
    modifier: str | None = None
    timestamp: datetime = field(default_factory=_utcnow)


@dataclass
class CheckpointRef:
    id: str = field(default_factory=_generate_id)
    session_id: str = ""
    created_at: datetime = field(default_factory=_utcnow)
    message_index: int = 0
    description: str | None = None


@dataclass
class EvalRun:
    id: str = field(default_factory=_generate_id)
    task_id: str = ""
    provider: str = ""
    model: str = ""
    skill_pack: str | None = None
    started_at: datetime = field(default_factory=_utcnow)
    completed_at: datetime | None = None
    status: str = "running"            # running | completed | failed
    scores: dict[str, float] = field(default_factory=dict)
    trace_id: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)
```

**Acceptance criteria:**

1. All model classes are importable from `caw.models`.
2. All enum values match the strings defined in the Technical Specification §8.1.
3. Default factory functions produce valid IDs and timestamps.
4. All dataclasses can be constructed with defaults only (no required positional args).
5. `SessionState("active") == SessionState.ACTIVE`.
6. `ruff check` and `mypy` pass.

**Tests (`tests/unit/test_models.py`):**

- `test_session_defaults`: Construct `Session()`, verify all fields have valid defaults.
- `test_session_state_enum`: Verify all enum values roundtrip from string.
- `test_message_defaults`: Construct `Message()`, verify defaults.
- `test_generate_id_unique`: Call `_generate_id()` 100 times, verify all unique.
- `test_utcnow_is_utc`: Verify `_utcnow()` returns timezone-aware UTC datetime.
- `test_all_enums_are_str_enum`: Verify each enum value is also a string.

---

### M1-WP04: Database initialization and migration

**Dependencies:** M1-WP02, M1-WP03
**Complexity:** M

**Files to create:**

```
src/caw/storage/database.py
src/caw/storage/migrations/__init__.py
src/caw/storage/migrations/001_initial_schema.py
tests/unit/storage/test_database.py
```

**Add dependency to `pyproject.toml`:**
```toml
dependencies = [
    "aiosqlite>=0.20",
]
```

Also add `uuid6>=2024.1` to dependencies for UUIDv7 support.

**Specification:**

`src/caw/storage/database.py`:

```python
"""Database connection and migration management.

Handles SQLite connection lifecycle, WAL mode configuration,
pragma tuning, and migration execution.
"""

import aiosqlite
from pathlib import Path
from caw.core.config import StorageConfig
from caw.errors import StorageError


class Database:
    """Manages the SQLite database connection and lifecycle.

    Usage:
        db = Database(storage_config)
        await db.connect()
        async with db.connection() as conn:
            await conn.execute("SELECT 1")
        await db.close()
    """

    def __init__(self, config: StorageConfig) -> None:
        """Initialize database manager.

        Args:
            config: Storage configuration with db_path.
        """
        ...

    async def connect(self) -> None:
        """Open database connection and apply pragmas.

        Pragmas applied:
        - journal_mode=WAL
        - synchronous=NORMAL
        - cache_size=-64000 (64MB)
        - foreign_keys=ON

        Creates the database file and parent directories
        if they do not exist.

        Raises:
            StorageError: If connection fails.
        """
        ...

    async def close(self) -> None:
        """Close the database connection gracefully.

        Ensures WAL checkpoint before closing.
        """
        ...

    def connection(self) -> aiosqlite.Connection:
        """Return the active connection.

        Raises:
            StorageError: If not connected.
        """
        ...

    async def run_migrations(self) -> list[str]:
        """Run all pending migrations in order.

        Process:
        1. Ensure schema_version table exists.
        2. List applied migrations from schema_version.
        3. Discover migration modules in migrations/ directory.
        4. Run each unapplied migration's up() function in order.
        5. Record each successful migration in schema_version.
        6. Return list of applied migration names.

        Raises:
            StorageError: If any migration fails (rolls back that migration).
        """
        ...
```

`src/caw/storage/migrations/001_initial_schema.py`:

```python
"""Initial database schema.

Creates all tables defined in Technical Specification §8.1.
"""

VERSION = "0.1.0"
DESCRIPTION = "Initial schema: sessions, messages, artifacts, trace_events, sources, citations, eval_runs, checkpoints"


async def up(conn: aiosqlite.Connection) -> None:
    """Apply migration: create all initial tables and indexes."""
    # Execute the full SQL from Technical Specification §8.1
    # Every CREATE TABLE and CREATE INDEX statement.
    ...


async def down(conn: aiosqlite.Connection) -> None:
    """Reverse migration: drop all tables."""
    # DROP TABLE in reverse dependency order
    ...
```

**Acceptance criteria:**

1. `Database(config)` creates parent directories for `db_path` if missing.
2. `await db.connect()` creates the database file.
3. After `connect()`, `PRAGMA journal_mode` returns `wal`.
4. After `connect()`, `PRAGMA foreign_keys` returns `1`.
5. `await db.run_migrations()` creates all tables from Technical Specification §8.1.
6. Running `run_migrations()` twice is idempotent (second run applies nothing).
7. All tables and indexes from §8.1 exist after migration.
8. `await db.close()` does not raise.
9. `ruff check` and `mypy` pass.

**Tests (`tests/unit/storage/test_database.py`):**

- `test_connect_creates_file`: Connect to a path in a temp dir, verify file exists.
- `test_connect_creates_parent_dirs`: Use a nested path, verify dirs created.
- `test_pragmas_applied`: After connect, verify WAL, foreign_keys, cache_size.
- `test_run_migrations_initial`: Run migrations, verify all tables exist (query sqlite_master).
- `test_run_migrations_idempotent`: Run twice, verify no error and same table set.
- `test_close_no_error`: Connect then close, verify no exception.
- `test_connection_before_connect_raises`: Access connection without connecting, verify StorageError.

---

### M1-WP05: Repository layer

**Dependencies:** M1-WP04
**Complexity:** L

**Files to create:**

```
src/caw/storage/repository.py
tests/unit/storage/test_repository.py
```

**Specification:**

Implement repository classes from Technical Specification §8.3 for each core model. Each repository handles serialization between dataclass models and database rows, including JSON serialization for dict/list fields.

```python
"""Data access repositories for all core models.

Each repository encapsulates SQL queries for one model type.
All methods are async. All writes use parameterized queries.
Dict/list fields are serialized as JSON text columns.
"""

import json
from datetime import datetime
from caw.models import (
    Session, SessionState, SessionMode, Message, MessageRole,
    Artifact, ArtifactType, Source, Citation, TraceEvent,
    CheckpointRef, EvalRun,
)
from caw.storage.database import Database
from caw.errors import StorageError


class SessionRepository:
    def __init__(self, db: Database) -> None: ...

    async def create(self, session: Session) -> Session: ...
    async def get(self, session_id: str) -> Session | None: ...
    async def update(self, session: Session) -> Session: ...
    async def delete(self, session_id: str) -> None: ...
    async def list_by_state(
        self, state: SessionState, limit: int = 50, cursor: str | None = None
    ) -> list[Session]: ...
    async def list_by_mode(
        self, mode: SessionMode, limit: int = 50, cursor: str | None = None
    ) -> list[Session]: ...
    async def list_recent(
        self, limit: int = 50, cursor: str | None = None
    ) -> list[Session]: ...


class MessageRepository:
    def __init__(self, db: Database) -> None: ...

    async def create(self, message: Message) -> Message: ...
    async def get(self, message_id: str) -> Message | None: ...
    async def list_by_session(
        self, session_id: str, limit: int | None = None
    ) -> list[Message]: ...
    async def count_by_session(self, session_id: str) -> int: ...
    async def get_last_n(self, session_id: str, n: int) -> list[Message]: ...


class ArtifactRepository:
    def __init__(self, db: Database) -> None: ...

    async def create(self, artifact: Artifact) -> Artifact: ...
    async def get(self, artifact_id: str) -> Artifact | None: ...
    async def list_by_session(self, session_id: str) -> list[Artifact]: ...
    async def list_by_type(
        self, artifact_type: ArtifactType, limit: int = 50
    ) -> list[Artifact]: ...


class TraceEventRepository:
    def __init__(self, db: Database) -> None: ...

    async def create(self, event: TraceEvent) -> TraceEvent: ...
    async def create_batch(self, events: list[TraceEvent]) -> None: ...
    async def get_by_trace_id(
        self, trace_id: str, event_types: list[str] | None = None
    ) -> list[TraceEvent]: ...
    async def get_by_session(
        self, session_id: str, event_types: list[str] | None = None,
        since: datetime | None = None
    ) -> list[TraceEvent]: ...


class SourceRepository:
    def __init__(self, db: Database) -> None: ...

    async def create(self, source: Source) -> Source: ...
    async def get(self, source_id: str) -> Source | None: ...
    async def list_by_session(self, session_id: str) -> list[Source]: ...
    async def find_by_hash(self, content_hash: str) -> Source | None: ...


class CitationRepository:
    def __init__(self, db: Database) -> None: ...

    async def create(self, citation: Citation) -> Citation: ...
    async def list_by_message(self, message_id: str) -> list[Citation]: ...
    async def list_by_source(self, source_id: str) -> list[Citation]: ...


class CheckpointRepository:
    def __init__(self, db: Database) -> None: ...

    async def create(self, checkpoint: CheckpointRef, state_json: str) -> CheckpointRef: ...
    async def get_latest(self, session_id: str) -> tuple[CheckpointRef, str] | None: ...
    async def list_by_session(self, session_id: str) -> list[CheckpointRef]: ...


class EvalRunRepository:
    def __init__(self, db: Database) -> None: ...

    async def create(self, run: EvalRun) -> EvalRun: ...
    async def get(self, run_id: str) -> EvalRun | None: ...
    async def update(self, run: EvalRun) -> EvalRun: ...
    async def list_by_task(
        self, task_id: str, limit: int = 50
    ) -> list[EvalRun]: ...
    async def list_by_provider(
        self, provider: str, model: str, limit: int = 50
    ) -> list[EvalRun]: ...
```

**Serialization rules:**

- `dict` and `list` fields map to `TEXT` columns as `json.dumps()` / `json.loads()`.
- `datetime` fields map to `TEXT` columns as ISO 8601 UTC strings.
- `Enum` fields map to `TEXT` columns as their `.value` string.
- `None` maps to SQL `NULL`.
- All queries use `?` parameter substitution. No f-strings or `.format()` in SQL.

**Acceptance criteria:**

1. `SessionRepository.create()` inserts a row and returns the session with ID.
2. `SessionRepository.get()` retrieves a session and deserializes all fields including JSON dicts.
3. `SessionRepository.update()` modifies `updated_at` and persists changes.
4. `SessionRepository.list_by_state()` returns only sessions matching the given state.
5. `MessageRepository.list_by_session()` returns messages ordered by `sequence_num`.
6. `TraceEventRepository.create_batch()` inserts multiple events in one transaction.
7. `TraceEventRepository.get_by_trace_id()` filters by `event_types` when provided.
8. `SourceRepository.find_by_hash()` returns a source or `None`.
9. Roundtrip test: create any model, retrieve it, verify all fields match.
10. `ruff check` and `mypy` pass.

**Tests (`tests/unit/storage/test_repository.py`):**

Use a shared `conftest.py` fixture that creates an in-memory SQLite database (`":memory:"`), runs migrations, and provides a `Database` instance.

- `test_session_create_and_get`: Create, get, verify fields.
- `test_session_update`: Create, modify, update, get, verify changes.
- `test_session_list_by_state`: Create sessions with different states, filter.
- `test_session_list_by_mode`: Create sessions with different modes, filter.
- `test_message_ordering`: Create messages with sequence numbers, verify list order.
- `test_message_count`: Create N messages, verify count.
- `test_artifact_create_and_list`: Create artifacts, list by session.
- `test_trace_event_batch_create`: Create batch of events, retrieve by trace_id.
- `test_trace_event_filter_by_type`: Filter events by event_type.
- `test_source_find_by_hash`: Create source, find by hash.
- `test_source_find_by_hash_not_found`: Query nonexistent hash, verify None.
- `test_citation_roundtrip`: Create citation, list by message and by source.
- `test_json_field_roundtrip`: Create a session with complex config_overrides dict, retrieve, verify.
- `test_datetime_serialization`: Create model, retrieve, verify datetime fields are correct.
- `test_enum_serialization`: Create session with each state, retrieve, verify enum type.

---

## Milestone 2: Protocol Layer

**Goal:** The system can send completion requests to model providers and receive responses through a stable, provider-agnostic interface. After this milestone, a mock provider works end-to-end and at least one real provider (Anthropic) is wired up.

**Prerequisites:** Milestone 1 complete.

---

### M2-WP01: Provider protocol and base types

**Dependencies:** none
**Complexity:** M

**Files to create:**

```
src/caw/protocols/types.py
src/caw/protocols/provider.py
tests/unit/protocols/test_types.py
```

**Specification:**

`src/caw/protocols/types.py`: Define all provider-layer data types from Technical Specification §10.1.2:

- `ContentBlock` (text, image, document)
- `ProviderMessage` (role, content, tool_calls)
- `ToolCall` and `ToolResult`
- `ToolDefinition`
- `ProviderResponse` (content, model, tokens, latency)
- `ProviderStreamChunk` (delta text, tool call events, done signal)
- `ProviderHealth` (available, latency_ms, error)

`src/caw/protocols/provider.py`: Define the `ModelProvider` protocol from Technical Specification §10.1:

```python
from typing import Protocol, AsyncIterator, runtime_checkable

@runtime_checkable
class ModelProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    async def complete(
        self,
        messages: list[ProviderMessage],
        model: str,
        tools: list[ToolDefinition] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        stream: bool = False,
    ) -> ProviderResponse | AsyncIterator[ProviderStreamChunk]: ...

    async def health_check(self) -> ProviderHealth: ...
    def supports_tool_use(self) -> bool: ...
    def supports_streaming(self) -> bool: ...
    def max_context_window(self, model: str) -> int: ...
```

**Acceptance criteria:**

1. All types are importable from `caw.protocols.types`.
2. `ModelProvider` is a `runtime_checkable` Protocol.
3. `isinstance(mock_that_implements_all_methods, ModelProvider)` returns `True`.
4. All dataclasses have defaults for optional fields.
5. `ruff check` and `mypy` pass.

**Tests (`tests/unit/protocols/test_types.py`):**

- `test_content_block_text`: Create text content block, verify fields.
- `test_provider_message_construction`: Create message with mixed content blocks.
- `test_provider_response_fields`: Verify all response fields.
- `test_provider_protocol_check`: Create a class implementing all methods, verify isinstance.

---

### M2-WP02: Mock provider

**Dependencies:** M2-WP01
**Complexity:** M

**Files to create:**

```
src/caw/protocols/mock.py
tests/unit/protocols/test_mock.py
```

**Specification:**

A `MockProvider` implementing `ModelProvider` for testing and development. It returns configurable canned responses and can simulate streaming, errors, and latency.

```python
class MockProvider:
    """Mock model provider for testing.

    Configurable behaviors:
    - Fixed response text (default: "Mock response.")
    - Simulated token counts
    - Simulated latency (default: 0)
    - Configurable failure mode (raise ProviderError)
    - Streaming simulation (yields response word by word)
    """

    def __init__(
        self,
        provider_id: str = "mock",
        response_text: str = "Mock response.",
        latency_ms: int = 0,
        fail: bool = False,
        fail_message: str = "Simulated provider failure",
        token_count_in: int = 10,
        token_count_out: int = 20,
    ) -> None: ...
```

**Acceptance criteria:**

1. `MockProvider()` implements `ModelProvider` (isinstance check passes).
2. `await mock.complete(messages, model="test")` returns a `ProviderResponse` with the configured text.
3. `await mock.complete(..., stream=True)` yields `ProviderStreamChunk` objects.
4. `MockProvider(fail=True)` raises `ProviderError` on `complete()`.
5. `await mock.health_check()` returns `ProviderHealth(available=True)` (or `False` if `fail=True`).
6. `ruff check` and `mypy` pass.

**Tests (`tests/unit/protocols/test_mock.py`):**

- `test_mock_complete_default`: Verify default response text.
- `test_mock_complete_custom`: Verify custom response text.
- `test_mock_streaming`: Collect all stream chunks, verify full text.
- `test_mock_failure`: Verify ProviderError raised.
- `test_mock_health_check`: Verify health response.
- `test_mock_isinstance_protocol`: Verify isinstance(MockProvider(), ModelProvider).

---

### M2-WP03: Anthropic provider

**Dependencies:** M2-WP01, M1-WP02
**Complexity:** M

**Files to create:**

```
src/caw/protocols/anthropic_provider.py
tests/unit/protocols/test_anthropic_provider.py
```

**Add dependency to `pyproject.toml`:**
```toml
"anthropic>=0.40",
"httpx>=0.27",
```

**Specification:**

Implement `ModelProvider` for the Anthropic API using the `anthropic` Python SDK. Reads configuration from `ProviderConfig`.

Key implementation details:
- Normalize `ProviderMessage` to Anthropic's message format (system messages extracted as `system` parameter).
- Map `ToolDefinition` to Anthropic's tool format.
- Handle streaming via Anthropic's `stream()` method, yielding `ProviderStreamChunk`.
- Map Anthropic API errors to `ProviderError` with specific codes: `provider_auth` (401), `provider_rate_limit` (429), `provider_timeout`, `provider_server_error` (500+).
- Context window lookup: maintain a dict of known model context windows (claude-sonnet-4-20250514: 200k, etc.).

**Acceptance criteria:**

1. Class implements `ModelProvider` protocol.
2. `provider_id` returns `"anthropic"`.
3. System messages are correctly extracted from the messages list and passed as the `system` parameter.
4. `supports_tool_use()` returns `True`.
5. `supports_streaming()` returns `True`.
6. API errors are caught and wrapped as `ProviderError` with appropriate codes.
7. Missing API key (env var not set) raises `ProviderError(code="provider_auth")` on first call.
8. `ruff check` and `mypy` pass.

**Tests (`tests/unit/protocols/test_anthropic_provider.py`):**

Tests mock the `anthropic` SDK client to avoid real API calls.

- `test_provider_id`: Verify returns "anthropic".
- `test_system_message_extraction`: Verify system messages are separated.
- `test_complete_maps_response`: Mock SDK response, verify ProviderResponse fields.
- `test_streaming_yields_chunks`: Mock SDK stream, verify chunk sequence.
- `test_auth_error_mapping`: Mock 401, verify ProviderError code.
- `test_rate_limit_error_mapping`: Mock 429, verify ProviderError code.
- `test_timeout_error_mapping`: Mock timeout, verify ProviderError code.
- `test_missing_api_key`: No env var set, verify ProviderError.

---

### M2-WP04: OpenAI-compatible provider

**Dependencies:** M2-WP01, M1-WP02
**Complexity:** M

**Files to create:**

```
src/caw/protocols/openai_provider.py
tests/unit/protocols/test_openai_provider.py
```

**Add dependency to `pyproject.toml`:**
```toml
"openai>=1.50",
```

**Specification:**

Implement `ModelProvider` for OpenAI and OpenAI-compatible APIs (Ollama, vLLM, LM Studio). Uses the `openai` Python SDK with a configurable `base_url`.

When `ProviderConfig.type` is `"openai"`, use the default OpenAI base URL.
When `ProviderConfig.type` is `"openai_compatible"`, use `ProviderConfig.base_url`.

Key differences from Anthropic:
- System messages are included inline in the messages array (OpenAI format).
- Tool format maps to OpenAI's function calling schema.
- Streaming uses OpenAI's `stream=True` parameter.

**Acceptance criteria:**

1. Class implements `ModelProvider` protocol.
2. Works with both `"openai"` and `"openai_compatible"` config types.
3. `base_url` is set from config when type is `"openai_compatible"`.
4. Tool definitions map correctly to OpenAI function format.
5. Streaming yields proper `ProviderStreamChunk` objects.
6. API errors map to `ProviderError` with appropriate codes.
7. `ruff check` and `mypy` pass.

**Tests (`tests/unit/protocols/test_openai_provider.py`):**

- `test_provider_id_openai`: Verify returns "openai".
- `test_provider_id_compatible`: Verify returns configured ID.
- `test_custom_base_url`: Verify base_url is set from config.
- `test_complete_maps_response`: Mock SDK response, verify fields.
- `test_tool_format_mapping`: Verify ToolDefinition maps to OpenAI format.
- `test_streaming`: Mock stream, verify chunks.
- `test_error_mapping`: Verify error type mapping.

---

### M2-WP05: Provider registry

**Dependencies:** M2-WP02, M2-WP03, M2-WP04, M1-WP02
**Complexity:** S

**Files to create:**

```
src/caw/protocols/registry.py
tests/unit/protocols/test_registry.py
```

**Specification:**

```python
class ProviderRegistry:
    """Registry of available model providers.

    Instantiates and manages provider instances based on configuration.
    Provides lookup by provider key (the key in config.providers dict).
    """

    def __init__(self, config: CAWConfig) -> None:
        """Initialize registry from config.

        For each entry in config.providers, instantiate the
        appropriate provider class based on the 'type' field:
        - "anthropic" → AnthropicProvider
        - "openai" → OpenAIProvider
        - "openai_compatible" → OpenAIProvider (with base_url)

        Does NOT call health_check at init time. Providers are
        lazily validated on first use.
        """
        ...

    def get(self, provider_key: str) -> ModelProvider:
        """Get a provider by its config key.

        Raises:
            ProviderError: If key not found in registry.
        """
        ...

    def list_providers(self) -> list[str]:
        """Return all registered provider keys."""
        ...

    async def health_check_all(self) -> dict[str, ProviderHealth]:
        """Run health checks on all registered providers."""
        ...
```

**Acceptance criteria:**

1. Registry initializes providers from config without calling health_check.
2. `get("anthropic")` returns an `AnthropicProvider` instance.
3. `get("nonexistent")` raises `ProviderError`.
4. `list_providers()` returns all config keys.
5. `ruff check` and `mypy` pass.

**Tests (`tests/unit/protocols/test_registry.py`):**

- `test_registry_creates_providers`: Config with mock entries, verify providers created.
- `test_registry_get_valid`: Get known key, verify type.
- `test_registry_get_invalid`: Get unknown key, verify ProviderError.
- `test_registry_list`: Verify list matches config keys.

---

## Milestone 3: Skill System

**Goal:** Skills can be loaded from disk, validated, resolved with precedence, and composed into a final context. Skill packs can be parsed and applied. After this milestone, the system has its primary internal control surface.

**Prerequisites:** Milestone 1 complete (needs config and storage). Milestone 2 not required.

---

### M3-WP01: Skill document parser and validator

**Dependencies:** none
**Complexity:** M

**Files to create:**

```
src/caw/skills/loader.py
src/caw/skills/validator.py
tests/unit/skills/test_loader.py
tests/unit/skills/test_validator.py
tests/fixtures/skills/valid_basic.md
tests/fixtures/skills/valid_full.md
tests/fixtures/skills/invalid_missing_id.md
tests/fixtures/skills/invalid_bad_version.md
tests/fixtures/skills/invalid_empty_body.md
```

**Specification:**

`src/caw/skills/loader.py`:

```python
"""Skill document loader.

Loads skill documents from disk, parses YAML frontmatter
and Markdown body, and returns structured SkillDocument objects.
"""

from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class SkillDocument:
    """Parsed skill document.

    Attributes:
        skill_id: Dot-namespaced unique identifier.
        version: SemVer version string.
        name: Human-readable name.
        description: Purpose summary.
        author: Creator identifier.
        tags: Searchable tags.
        requires_tools: Tool names this skill needs.
        requires_permissions: Minimum permission levels.
        conflicts_with: Skill IDs that cannot coexist.
        priority: Resolution precedence (higher = loaded later).
        provider_preference: Preferred model provider key.
        min_context_window: Minimum context window in tokens.
        body: Markdown body content (everything after frontmatter).
        source_path: File path the skill was loaded from.
    """
    skill_id: str
    version: str
    name: str
    description: str
    author: str
    tags: list[str] = field(default_factory=list)
    requires_tools: list[str] = field(default_factory=list)
    requires_permissions: list[str] = field(default_factory=list)
    conflicts_with: list[str] = field(default_factory=list)
    priority: int = 100
    provider_preference: str | None = None
    min_context_window: int | None = None
    body: str = ""
    source_path: Path | None = None


def load_skill(path: Path) -> SkillDocument:
    """Load a single skill document from a Markdown file.

    Parses YAML frontmatter (between --- delimiters) and
    extracts the Markdown body (everything after the closing ---).

    Args:
        path: Path to the .md skill document.

    Returns:
        Parsed SkillDocument.

    Raises:
        SkillError: If file cannot be read or frontmatter cannot be parsed.
    """
    ...


def discover_skills(directory: Path) -> list[Path]:
    """Discover all .md files in a directory (non-recursive).

    Returns:
        Sorted list of .md file paths.
    """
    ...


def load_all_skills(directory: Path) -> list[SkillDocument]:
    """Load all skill documents from a directory.

    Loads each .md file, skipping files that fail validation
    (logged as warnings, not fatal).

    Returns:
        List of successfully loaded SkillDocuments.
    """
    ...
```

`src/caw/skills/validator.py`:

```python
"""Skill document validation.

Validates SkillDocument objects against the schema
defined in Technical Specification §7.1.1.
"""

import re

@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]    # List of specific error messages
    warnings: list[str]  # Non-fatal issues


def validate_skill(skill: SkillDocument) -> ValidationResult:
    """Validate a loaded skill document.

    Checks:
    1. skill_id is non-empty and matches pattern: lowercase alphanumeric + dots.
    2. version is valid SemVer (MAJOR.MINOR.PATCH, optional pre-release).
    3. name is non-empty.
    4. description is non-empty.
    5. author is non-empty.
    6. priority is a positive integer.
    7. requires_permissions values are valid PermissionLevel enum values.
    8. body is non-empty (at least 10 characters of non-whitespace content).
    9. version pre-release identifiers, if present, match SemVer spec.

    Returns:
        ValidationResult with errors and warnings.
    """
    ...
```

**Fixture files:**

`tests/fixtures/skills/valid_basic.md`:
```markdown
---
skill_id: "test.basic"
version: "1.0.0"
name: "Basic Test Skill"
description: "A minimal valid skill for testing."
author: "test"
---

# Basic Test Skill

This skill does basic things for testing purposes.
```

`tests/fixtures/skills/valid_full.md`: All frontmatter fields populated.

`tests/fixtures/skills/invalid_missing_id.md`: Valid YAML frontmatter but no `skill_id` field.

`tests/fixtures/skills/invalid_bad_version.md`: `version: "not-semver"`.

`tests/fixtures/skills/invalid_empty_body.md`: Valid frontmatter, empty body.

**Acceptance criteria:**

1. `load_skill()` parses valid skill files and returns complete `SkillDocument`.
2. `load_skill()` raises `SkillError` for files that don't exist.
3. `load_skill()` raises `SkillError` for files without YAML frontmatter.
4. `validate_skill()` returns `valid=True` for valid skills.
5. `validate_skill()` returns `valid=False` with specific error messages for each invalid case.
6. `discover_skills()` finds all `.md` files in a directory.
7. `load_all_skills()` skips invalid files without crashing.
8. `ruff check` and `mypy` pass.

**Tests:**

- `test_load_valid_basic`: Load basic fixture, verify all fields.
- `test_load_valid_full`: Load full fixture, verify all fields including optional ones.
- `test_load_nonexistent_file`: Verify SkillError raised.
- `test_load_no_frontmatter`: File without `---` delimiters, verify SkillError.
- `test_validate_valid`: Validate basic fixture, verify `valid=True`.
- `test_validate_missing_id`: Verify error message about missing skill_id.
- `test_validate_bad_version`: Verify error message about invalid SemVer.
- `test_validate_empty_body`: Verify error message about empty body.
- `test_discover_finds_md_files`: Create temp dir with .md and .txt files, verify only .md found.
- `test_load_all_skips_invalid`: Dir with one valid and one invalid, verify one loaded.

---

### M3-WP02: Skill resolver

**Dependencies:** M3-WP01
**Complexity:** M

**Files to create:**

```
src/caw/skills/resolver.py
tests/unit/skills/test_resolver.py
```

**Specification:**

Implement the skill resolution logic from Technical Specification §7.2.

```python
"""Skill resolution and composition.

Determines which skills are active for a given session or request,
resolves conflicts, and composes the final skill context.
"""

@dataclass
class ResolvedSkillSet:
    """The result of skill resolution.

    Attributes:
        skills: Ordered list of resolved skills (lowest priority first).
        composed_context: The final composed context string with
            skill delimiters for traceability.
        conflicts_resolved: List of conflict resolutions made.
        warnings: Non-fatal issues encountered during resolution.
    """
    skills: list[SkillDocument]
    composed_context: str
    conflicts_resolved: list[str]
    warnings: list[str]


class SkillResolver:
    """Resolves which skills are active and composes them.

    Resolution order (Technical Specification §7.2.1):
    1. Explicit request — skills specified by the user.
    2. Skill pack — if a pack is active, all skills in the pack.
    3. Mode default — each mode has a default set of skills.
    4. Builtin base — core skills always load.

    Conflict resolution (Technical Specification §7.2.2):
    If two skills declare conflicts_with each other,
    the higher-priority skill wins. Equal priority with
    conflicting specificity levels (explicit > pack > mode > builtin)
    resolves in favor of the more specific request.
    Equal priority AND equal specificity is an error.

    Composition (Technical Specification §7.2.3):
    Skills are concatenated in priority order (lowest first)
    with <!-- BEGIN SKILL: {skill_id} --> / <!-- END SKILL: {skill_id} -->
    delimiters between them.
    """

    def __init__(self, available_skills: list[SkillDocument]) -> None:
        """Initialize with the full set of available skills."""
        ...

    def resolve(
        self,
        explicit_ids: list[str] | None = None,
        pack_ids: list[str] | None = None,
        mode_default_ids: list[str] | None = None,
        builtin_ids: list[str] | None = None,
    ) -> ResolvedSkillSet:
        """Resolve the active skill set.

        Args:
            explicit_ids: Skill IDs explicitly requested by the user.
            pack_ids: Skill IDs from the active skill pack.
            mode_default_ids: Skill IDs that are default for the current mode.
            builtin_ids: Skill IDs that always load.

        Returns:
            ResolvedSkillSet with ordered skills and composed context.

        Raises:
            SkillError: If conflicting skills have equal priority
                and equal specificity (unresolvable conflict).
        """
        ...
```

**Acceptance criteria:**

1. Skills are composed in priority order (lowest first).
2. Higher priority skills appear later in the composed context (can override earlier guidance).
3. Explicit skills override pack skills which override mode defaults which override builtins.
4. Conflicting skills are resolved by priority, then by specificity.
5. Unresolvable conflicts raise `SkillError` with a message naming both skills.
6. Composed context includes `<!-- BEGIN SKILL: ... -->` / `<!-- END SKILL: ... -->` delimiters.
7. Skills not found in `available_skills` produce a warning (not an error).
8. `ruff check` and `mypy` pass.

**Tests (`tests/unit/skills/test_resolver.py`):**

- `test_resolve_empty`: No skills requested, verify empty result.
- `test_resolve_single_explicit`: One explicit skill, verify it's in the set.
- `test_resolve_priority_order`: Multiple skills with different priorities, verify order.
- `test_resolve_conflict_by_priority`: Two conflicting skills, higher priority wins.
- `test_resolve_conflict_by_specificity`: Same priority, explicit beats pack.
- `test_resolve_unresolvable_conflict`: Same priority and specificity, verify SkillError.
- `test_composed_context_has_delimiters`: Verify delimiter format in output.
- `test_missing_skill_warning`: Request nonexistent skill ID, verify warning.
- `test_resolve_with_pack_and_explicit`: Both sources, verify merge.

---

### M3-WP03: Skill pack parser

**Dependencies:** M3-WP01
**Complexity:** S

**Files to create:**

```
src/caw/skills/pack.py
tests/unit/skills/test_pack.py
tests/fixtures/skills/packs/valid_pack.toml
tests/fixtures/skills/packs/invalid_pack.toml
```

**Specification:**

Parse skill pack TOML files from Technical Specification §7.3.

```python
@dataclass
class SkillPackEntry:
    skill_id: str
    version_constraint: str = ">=0.0.0"  # SemVer range
    priority_override: int | None = None

@dataclass
class SkillPack:
    pack_id: str
    version: str
    name: str
    description: str
    skills: list[SkillPackEntry]
    config_overrides: dict[str, object] = field(default_factory=dict)
    source_path: Path | None = None

def load_skill_pack(path: Path) -> SkillPack:
    """Load a skill pack from a TOML file."""
    ...

def load_all_packs(directory: Path) -> list[SkillPack]:
    """Load all skill packs from a directory."""
    ...
```

**Acceptance criteria:**

1. Valid TOML pack files parse correctly.
2. `priority_override` is applied when present.
3. `config_overrides` section is captured.
4. Invalid TOML files raise `SkillError`.
5. `ruff check` and `mypy` pass.

**Tests (`tests/unit/skills/test_pack.py`):**

- `test_load_valid_pack`: Load fixture, verify all fields.
- `test_load_pack_with_overrides`: Verify config_overrides captured.
- `test_load_invalid_pack`: Verify SkillError on malformed TOML.
- `test_load_all_packs`: Directory with two packs, verify both loaded.

---

### M3-WP04: Skill registry

**Dependencies:** M3-WP01, M3-WP02, M3-WP03, M1-WP02
**Complexity:** M

**Files to create:**

```
src/caw/skills/registry.py
tests/unit/skills/test_registry.py
```

**Specification:**

```python
class SkillRegistry:
    """Central registry for skills and skill packs.

    Loads skills from configured directories (builtin + user),
    loads packs from the packs directory, and provides the
    SkillResolver with the full set of available skills.

    Also defines mode-default skill mappings:
    - chat: [] (no default skills for chat)
    - research: ["caw.builtin.research_operator"]
    - deliberation: ["caw.builtin.deliberation_director"]
    - workspace: ["caw.builtin.workspace_operator"]
    - arena: []
    """

    def __init__(self, config: SkillsConfig) -> None: ...

    def load(self) -> None:
        """Load all skills and packs from configured directories."""
        ...

    def get_skill(self, skill_id: str) -> SkillDocument | None: ...
    def get_pack(self, pack_id: str) -> SkillPack | None: ...
    def list_skills(self) -> list[SkillDocument]: ...
    def list_packs(self) -> list[SkillPack]: ...
    def get_mode_defaults(self, mode: SessionMode) -> list[str]: ...

    def create_resolver(self) -> SkillResolver:
        """Create a SkillResolver with all loaded skills."""
        ...
```

**Acceptance criteria:**

1. Registry loads skills from both builtin and user directories.
2. Registry loads packs from packs directory.
3. `get_skill()` returns skill by ID or None.
4. `get_mode_defaults()` returns correct default skill IDs per mode.
5. `create_resolver()` returns a configured `SkillResolver`.
6. `ruff check` and `mypy` pass.

**Tests (`tests/unit/skills/test_registry.py`):**

- `test_load_from_directories`: Create temp dirs with skill files, verify loaded.
- `test_get_skill_by_id`: Load skills, retrieve by ID.
- `test_get_skill_not_found`: Query nonexistent ID, verify None.
- `test_mode_defaults`: Verify each mode returns expected defaults.
- `test_create_resolver`: Verify resolver has all skills.

---

## Milestone 4: Trace System

**Goal:** Every significant action can emit structured trace events that are buffered, persisted, and queryable. After this milestone, the trace collector and replay engine are functional.

**Prerequisites:** Milestone 1 complete (needs storage).

---

### M4-WP01: Trace collector

**Dependencies:** M1-WP05 (TraceEventRepository)
**Complexity:** M

**Files to create:**

```
src/caw/traces/collector.py
tests/unit/traces/test_collector.py
```

**Specification:**

Implement the `TraceCollector` from Technical Specification §11.3. The collector buffers events in memory and flushes to the database in batches.

```python
class TraceCollector:
    """Collects and persists trace events.

    Thread-safe and async-safe. Events are buffered
    and flushed every `flush_interval` seconds or every
    `flush_threshold` events, whichever comes first.

    The collector must be started (to run the periodic
    flush task) and stopped (to flush remaining events).
    """

    def __init__(
        self,
        repository: TraceEventRepository,
        flush_threshold: int = 100,
        flush_interval: float = 5.0,
    ) -> None: ...

    async def start(self) -> None:
        """Start the periodic flush background task."""
        ...

    async def stop(self) -> None:
        """Flush remaining events and stop the background task."""
        ...

    async def emit(self, event: TraceEvent) -> None:
        """Buffer a trace event for persistence.

        If the buffer reaches flush_threshold, triggers
        an immediate flush.
        """
        ...

    async def flush(self) -> None:
        """Write all buffered events to the database."""
        ...

    async def get_trace(self, trace_id: str) -> list[TraceEvent]:
        """Retrieve all events for a trace ID, ordered by timestamp."""
        ...

    async def get_session_events(
        self,
        session_id: str,
        event_types: list[str] | None = None,
        since: datetime | None = None,
    ) -> list[TraceEvent]:
        """Retrieve events for a session with optional filtering."""
        ...
```

**Acceptance criteria:**

1. `emit()` buffers events without immediate database write.
2. `flush()` writes all buffered events to the database via `create_batch()`.
3. Buffer auto-flushes when reaching `flush_threshold`.
4. `stop()` flushes remaining events.
5. `get_trace()` retrieves events ordered by timestamp.
6. `get_session_events()` filters by event type and timestamp.
7. `ruff check` and `mypy` pass.

**Tests (`tests/unit/traces/test_collector.py`):**

- `test_emit_buffers`: Emit events, verify not yet in database.
- `test_flush_persists`: Emit then flush, verify in database.
- `test_auto_flush_on_threshold`: Set threshold=5, emit 5 events, verify flushed.
- `test_stop_flushes_remaining`: Emit events, stop, verify all persisted.
- `test_get_trace`: Emit events with same trace_id, retrieve, verify order.
- `test_get_session_events_filter`: Emit mixed types, filter, verify subset.

---

### M4-WP02: Trace schemas and helpers

**Dependencies:** M4-WP01
**Complexity:** S

**Files to create:**

```
src/caw/traces/schemas.py
tests/unit/traces/test_schemas.py
```

**Specification:**

Define helper functions that create correctly-typed trace events for each event type from Technical Specification §11.1. These are convenience constructors that ensure event payloads match the expected schema.

```python
"""Trace event factory functions.

Each function creates a TraceEvent with the correct event_type
and a validated data payload. Use these instead of constructing
TraceEvent directly to ensure schema consistency.
"""

def session_created(
    trace_id: str, session_id: str, mode: str, skills: list[str]
) -> TraceEvent: ...

def routing_decision(
    trace_id: str, session_id: str, strategy: str,
    candidates: list[str], selected: str, rationale: str
) -> TraceEvent: ...

def provider_request(
    trace_id: str, session_id: str, provider: str,
    model: str, message_count: int, token_estimate: int
) -> TraceEvent: ...

def provider_response(
    trace_id: str, session_id: str, provider: str,
    model: str, tokens_in: int, tokens_out: int, latency_ms: int
) -> TraceEvent: ...

def provider_error(
    trace_id: str, session_id: str, provider: str,
    model: str, error_type: str, message: str
) -> TraceEvent: ...

def tool_invocation(
    trace_id: str, session_id: str, tool_name: str,
    arguments: dict[str, object], server_id: str
) -> TraceEvent: ...

def tool_result(
    trace_id: str, session_id: str, tool_name: str,
    success: bool, duration_ms: int
) -> TraceEvent: ...

def gate_approval_required(
    trace_id: str, session_id: str, action: str,
    permission_level: str, resources: list[str]
) -> TraceEvent: ...

def gate_approved(
    trace_id: str, session_id: str, request_id: str,
    modifier: str | None = None
) -> TraceEvent: ...

def gate_denied(
    trace_id: str, session_id: str, request_id: str
) -> TraceEvent: ...

# ... one function per event type from §11.1
```

**Acceptance criteria:**

1. Each factory function returns a `TraceEvent` with correct `event_type`.
2. Each factory function populates `data` dict with all specified parameters.
3. `trace_id` and `session_id` are set on every event.
4. Timestamp is auto-generated.
5. `ruff check` and `mypy` pass.

**Tests (`tests/unit/traces/test_schemas.py`):**

- One test per factory function verifying event_type and data fields.

---

### M4-WP03: Replay engine

**Dependencies:** M4-WP01
**Complexity:** M

**Files to create:**

```
src/caw/traces/replay.py
tests/unit/traces/test_replay.py
```

**Specification:**

Implement the `ReplayEngine` from Technical Specification §11.4.

```python
@dataclass
class RunSummary:
    trace_id: str
    session_id: str
    mode: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    event_count: int
    provider_calls: int
    tool_calls: int
    errors: int
    key_events: list[TraceEvent]   # Filtered to important events

@dataclass
class RunDiff:
    trace_id_a: str
    trace_id_b: str
    events_only_in_a: list[TraceEvent]
    events_only_in_b: list[TraceEvent]
    common_event_types: list[str]
    timing_comparison: dict[str, tuple[int, int]]  # event_type → (ms_a, ms_b)

class ReplayEngine:
    def __init__(self, collector: TraceCollector) -> None: ...

    async def timeline(
        self, trace_id: str, event_types: list[str] | None = None
    ) -> list[TraceEvent]: ...

    async def summary(self, trace_id: str) -> RunSummary: ...

    async def diff(self, trace_id_a: str, trace_id_b: str) -> RunDiff: ...
```

**Acceptance criteria:**

1. `timeline()` returns events in chronological order.
2. `timeline()` filters by event type when specified.
3. `summary()` correctly counts provider calls, tool calls, and errors.
4. `summary()` calculates duration from first to last event.
5. `diff()` identifies events unique to each trace.
6. `ruff check` and `mypy` pass.

**Tests:**

- `test_timeline_order`: Insert events out of order, verify returned in order.
- `test_timeline_filter`: Filter by type, verify subset.
- `test_summary_counts`: Insert known events, verify counts.
- `test_summary_duration`: Verify duration calculation.
- `test_diff_unique_events`: Two traces with overlapping and unique events.

---

## Milestone 5: Orchestration Engine

**Goal:** The engine manages sessions, resolves skills, routes to providers, enforces permissions, and emits traces. After this milestone, the central nervous system is operational.

**Prerequisites:** Milestones 1–4 complete.

---

### M5-WP01: Session manager

**Dependencies:** M1-WP05
**Complexity:** M

**Files to create:**

```
src/caw/core/session.py
tests/unit/core/test_session.py
```

**Specification:**

```python
class SessionManager:
    """Manages session lifecycle.

    Handles creation, state transitions, branching,
    and retrieval of sessions. Validates state transitions
    against the state machine in Technical Specification §15.1.
    """

    VALID_TRANSITIONS: dict[SessionState, set[SessionState]] = {
        SessionState.CREATED: {SessionState.ACTIVE, SessionState.FAILED},
        SessionState.ACTIVE: {
            SessionState.PAUSED, SessionState.COMPLETED,
            SessionState.FAILED, SessionState.CHECKPOINTED,
        },
        SessionState.PAUSED: {SessionState.ACTIVE},
        SessionState.CHECKPOINTED: {SessionState.ACTIVE},
        SessionState.COMPLETED: set(),   # Terminal
        SessionState.FAILED: set(),      # Terminal
    }

    def __init__(self, repo: SessionRepository) -> None: ...

    async def create(
        self, mode: SessionMode, config_overrides: dict | None = None,
        skills: list[str] | None = None, skill_pack: str | None = None,
    ) -> Session: ...

    async def get(self, session_id: str) -> Session: ...

    async def transition(self, session_id: str, new_state: SessionState) -> Session:
        """Transition a session to a new state.

        Raises:
            ValidationError_: If the transition is not valid.
        """
        ...

    async def branch(self, session_id: str, branch_point: int) -> Session: ...

    async def list_sessions(
        self, state: SessionState | None = None, mode: SessionMode | None = None,
        limit: int = 50,
    ) -> list[Session]: ...
```

**Acceptance criteria:**

1. `create()` returns a session in `CREATED` state with a valid ID.
2. `transition()` enforces the state machine — invalid transitions raise `ValidationError_`.
3. `branch()` creates a new session with `parent_id` set and message history copied.
4. All state transitions update `updated_at`.
5. Terminal states (COMPLETED, FAILED) reject further transitions.
6. `ruff check` and `mypy` pass.

**Tests (`tests/unit/core/test_session.py`):**

- `test_create_session`: Verify initial state and fields.
- `test_valid_transitions`: Test each valid transition path.
- `test_invalid_transition`: COMPLETED → ACTIVE, verify error.
- `test_branch_copies_parent_id`: Branch, verify parent_id.
- `test_transition_updates_timestamp`: Verify updated_at changes.

---

### M5-WP02: Router

**Dependencies:** M2-WP05 (ProviderRegistry), M1-WP02
**Complexity:** M

**Files to create:**

```
src/caw/core/router.py
tests/unit/core/test_router.py
```

**Specification:**

Implement the `Router` from Technical Specification §6.3.

```python
@dataclass
class ProviderSelection:
    provider_key: str
    model: str
    rationale: str
    fallback_chain: list[str]

class Router:
    def __init__(
        self, config: CAWConfig, registry: ProviderRegistry
    ) -> None: ...

    async def route(
        self,
        explicit_provider: str | None = None,
        explicit_model: str | None = None,
        skill_preference: str | None = None,
    ) -> ProviderSelection:
        """Select a provider based on the routing strategy.

        Priority order:
        1. Explicit provider/model in the request.
        2. Skill-level provider preference.
        3. Config routing strategy.
        4. Fallback chain.
        """
        ...
```

**Acceptance criteria:**

1. Explicit provider overrides all other selection.
2. Skill preference is used when no explicit provider.
3. Config default is used when no explicit or skill preference.
4. Fallback chain is populated from config.
5. Unknown provider keys raise `ProviderError`.
6. `ruff check` and `mypy` pass.

**Tests:**

- `test_route_explicit`: Explicit provider, verify selected.
- `test_route_skill_preference`: Skill preference, verify selected.
- `test_route_config_default`: No preferences, verify config default.
- `test_route_fallback_chain`: Verify fallback chain populated.
- `test_route_unknown_provider`: Unknown key, verify error.

---

### M5-WP03: Permission gate

**Dependencies:** M1-WP03 (models), M4-WP02 (trace schemas)
**Complexity:** M

**Files to create:**

```
src/caw/core/permissions.py
tests/unit/core/test_permissions.py
```

**Specification:**

Implement the permission model from Technical Specification §6.5.

```python
class PermissionGate:
    """Checks permissions and manages approval gates.

    Uses the workspace config to determine which
    operations require confirmation. Emits trace events
    for all gate decisions.
    """

    def __init__(
        self, config: WorkspaceConfig, collector: TraceCollector
    ) -> None: ...

    async def check(
        self,
        level: PermissionLevel,
        action: str,
        resources: list[str],
        trace_id: str,
        session_id: str,
    ) -> ApprovalRequest | None:
        """Check if an action requires approval.

        Returns:
            None if the action is permitted without approval.
            ApprovalRequest if approval is needed.
        """
        ...

    def requires_approval(self, level: PermissionLevel) -> bool:
        """Check if a permission level requires approval based on config."""
        ...
```

**Acceptance criteria:**

1. `READ` and `SUGGEST` never require approval.
2. `DELETE` and `ADMIN` always require approval.
3. `WRITE` and `EXECUTE` respect config settings.
4. `check()` emits `gate:approval_required` trace event when approval needed.
5. `check()` returns None when no approval needed.
6. `ruff check` and `mypy` pass.

**Tests:**

- `test_read_no_approval`: READ level, verify None returned.
- `test_delete_always_approval`: DELETE level, verify ApprovalRequest returned.
- `test_write_configurable`: Test with confirm_writes=True and False.
- `test_execute_configurable`: Test with confirm_executions=True and False.
- `test_trace_event_emitted`: Verify gate event emitted on approval required.

---

### M5-WP04: Engine

**Dependencies:** M5-WP01, M5-WP02, M5-WP03, M3-WP04, M4-WP01
**Complexity:** L

**Files to create:**

```
src/caw/core/engine.py
tests/unit/core/test_engine.py
tests/integration/test_engine_integration.py
```

**Specification:**

Implement the `Engine` from Technical Specification §6.1. This is the central orchestration point. For this WP, implement the core `execute()` method for chat mode only. Research, deliberation, and workspace modes are wired in during their respective milestones.

```python
@dataclass
class ExecutionRequest:
    session_id: str
    content: str
    mode: SessionMode = SessionMode.CHAT
    provider: str | None = None
    model: str | None = None
    tools: list[ToolDefinition] | None = None
    attachments: list[object] | None = None

@dataclass
class ExecutionResult:
    session_id: str
    message_id: str
    content: str
    model: str
    provider: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    trace_id: str
    artifacts: list[Artifact] = field(default_factory=list)

class Engine:
    def __init__(
        self,
        config: CAWConfig,
        session_manager: SessionManager,
        router: Router,
        permission_gate: PermissionGate,
        skill_registry: SkillRegistry,
        trace_collector: TraceCollector,
        provider_registry: ProviderRegistry,
        message_repo: MessageRepository,
    ) -> None: ...

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a single request through the full pipeline.

        Steps:
        1. Get or validate the session.
        2. Resolve skills for the session mode.
        3. Route to a provider.
        4. Build the message list (history + skills context + new message).
        5. Call the provider.
        6. Store the user message and assistant response.
        7. Emit trace events for every step.
        8. Return the result.
        """
        ...
```

**Acceptance criteria:**

1. `execute()` with a chat request returns a complete `ExecutionResult`.
2. User message and assistant response are both stored in the database.
3. Session state transitions to ACTIVE on first message if CREATED.
4. Skills are resolved and composed into the provider context.
5. Routing decision is traced.
6. Provider request and response are traced.
7. Token counts are captured from the provider response.
8. The MockProvider can be used for fully offline execution.
9. `ruff check` and `mypy` pass.

**Tests (`tests/unit/core/test_engine.py`):** Use MockProvider.

- `test_execute_chat_basic`: Send message, verify response returned.
- `test_execute_stores_messages`: Verify both user and assistant messages in DB.
- `test_execute_activates_session`: CREATED session becomes ACTIVE.
- `test_execute_resolves_skills`: Verify skill resolution traced.
- `test_execute_routes_provider`: Verify routing decision traced.
- `test_execute_records_tokens`: Verify token counts in result.

**Tests (`tests/integration/test_engine_integration.py`):**

- `test_full_chat_roundtrip`: Create session, send message, verify response, verify traces, verify message history.

---

## Milestone 6: Chat Capability

**Goal:** End-to-end chat works through the engine with streaming support. This is the first vertical slice proving the entire stack.

**Prerequisites:** Milestone 5 complete.

---

### M6-WP01: Chat handler with streaming

**Dependencies:** M5-WP04
**Complexity:** M

**Files to create:**

```
src/caw/capabilities/chat/handler.py
src/caw/capabilities/chat/history.py
tests/unit/capabilities/chat/test_handler.py
```

**Specification:**

Implement `ChatHandler` from Technical Specification §9.4.

```python
@dataclass
class StreamChunk:
    type: str              # text | tool_call | tool_result | citation | error | done
    content: str | None = None
    data: dict[str, object] | None = None

class ChatHandler:
    def __init__(self, engine: Engine) -> None: ...

    async def handle_message(
        self, session_id: str, message: str,
        attachments: list[object] | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Process a message and yield stream chunks."""
        ...

class ConversationHistory:
    """Manages conversation history for context building."""

    def __init__(self, message_repo: MessageRepository) -> None: ...

    async def build_context(
        self, session_id: str, max_messages: int | None = None
    ) -> list[ProviderMessage]:
        """Build provider message list from session history."""
        ...
```

**Acceptance criteria:**

1. `handle_message()` yields `StreamChunk` objects.
2. Final chunk has `type="done"` with message metadata.
3. Non-streaming mode collects all chunks into a complete response.
4. Conversation history is correctly built from stored messages.
5. `ruff check` and `mypy` pass.

**Tests:**

- `test_handle_message_yields_chunks`: Verify stream produces text and done chunks.
- `test_done_chunk_has_metadata`: Verify done chunk has message_id, tokens.
- `test_history_builds_context`: Store messages, build context, verify order and roles.

---

## Milestone 7: API Surface

**Goal:** The HTTP API and WebSocket streaming endpoint are operational. After this milestone, external clients can interact with the system.

**Prerequisites:** Milestone 6 complete.

---

### M7-WP01: FastAPI application scaffold

**Dependencies:** none
**Complexity:** M

**Files to create:**

```
src/caw/api/app.py
src/caw/api/deps.py
src/caw/api/schemas.py
tests/unit/api/test_app.py
```

**Add dependency to `pyproject.toml`:**
```toml
"fastapi>=0.115",
"uvicorn[standard]>=0.30",
```

**Specification:**

`src/caw/api/app.py`: FastAPI application factory.

```python
def create_app(config: CAWConfig | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Sets up:
    - Lifespan handler for startup/shutdown (database, trace collector).
    - CORS middleware from config.
    - Exception handlers mapping CAWError subclasses to HTTP responses.
    - Route inclusion from route modules.
    """
    ...
```

`src/caw/api/deps.py`: Dependency injection functions for FastAPI.

```python
async def get_engine() -> Engine: ...
async def get_session_manager() -> SessionManager: ...
async def get_trace_collector() -> TraceCollector: ...
# etc.
```

`src/caw/api/schemas.py`: Pydantic request/response models from Technical Specification §13.4.

```python
class APIResponse(BaseModel, Generic[T]):
    status: str = "ok"
    data: T | None = None
    error_code: str | None = None
    message: str | None = None

class CreateSessionRequest(BaseModel):
    mode: str = "chat"
    config_overrides: dict[str, object] | None = None
    skills: list[str] | None = None
    skill_pack: str | None = None

class SendMessageRequest(BaseModel):
    content: str
    provider: str | None = None
    model: str | None = None

class SessionResponse(BaseModel):
    id: str
    state: str
    mode: str
    created_at: str
    updated_at: str
    # ...
```

**Acceptance criteria:**

1. `create_app()` returns a FastAPI instance.
2. Health endpoint `GET /api/v1/health` returns 200.
3. CAWError subclasses map to appropriate HTTP status codes.
4. CORS middleware is configured from config.
5. `ruff check` and `mypy` pass.

**Tests (`tests/unit/api/test_app.py`):** Use `TestClient` from FastAPI.

- `test_health_endpoint`: GET /api/v1/health returns 200.
- `test_unknown_route_404`: GET /nonexistent returns 404.
- `test_cors_headers`: Verify CORS headers present.

---

### M7-WP02: Session and chat routes

**Dependencies:** M7-WP01
**Complexity:** M

**Files to create:**

```
src/caw/api/routes/__init__.py
src/caw/api/routes/sessions.py
src/caw/api/routes/chat.py
tests/unit/api/test_sessions.py
tests/unit/api/test_chat.py
```

**Specification:**

Implement routes from Technical Specification §13.2 for sessions and chat:

```
POST   /api/v1/sessions              → Create session
GET    /api/v1/sessions              → List sessions
GET    /api/v1/sessions/{id}         → Get session
PATCH  /api/v1/sessions/{id}         → Update session
POST   /api/v1/sessions/{id}/branch  → Branch session
DELETE /api/v1/sessions/{id}         → Delete session
POST   /api/v1/sessions/{id}/messages → Send message
GET    /api/v1/sessions/{id}/messages → Get history
```

**Acceptance criteria:**

1. POST /sessions creates a session and returns 201.
2. GET /sessions lists sessions with pagination.
3. GET /sessions/{id} returns session or 404.
4. POST /sessions/{id}/messages sends a message through the engine.
5. GET /sessions/{id}/messages returns message history ordered by sequence.
6. `ruff check` and `mypy` pass.

**Tests:** Use TestClient with MockProvider.

- `test_create_session`: POST, verify 201 and response body.
- `test_get_session`: Create then GET, verify fields.
- `test_get_session_not_found`: GET nonexistent, verify 404.
- `test_list_sessions`: Create several, list, verify count.
- `test_send_message`: POST message, verify response.
- `test_get_message_history`: Send messages, GET history, verify order.

---

### M7-WP03: WebSocket streaming

**Dependencies:** M7-WP01, M6-WP01
**Complexity:** M

**Files to create:**

```
src/caw/api/websocket.py
tests/unit/api/test_websocket.py
```

**Specification:**

Implement WebSocket endpoint from Technical Specification §13.5:

```
WS /api/v1/sessions/{id}/stream
```

Protocol: JSON-lines. Each line is a JSON object with `type` field. Client sends messages, server streams responses.

**Acceptance criteria:**

1. WebSocket connection succeeds for existing sessions.
2. Client sends `{"type": "message", "content": "..."}`, server streams chunks.
3. Each chunk is a valid JSON object with a `type` field.
4. Stream ends with `{"type": "done", ...}`.
5. Invalid session ID returns close with error code.
6. `ruff check` and `mypy` pass.

**Tests:**

- `test_websocket_connect`: Connect, verify connection established.
- `test_websocket_message_stream`: Send message, collect chunks, verify types.
- `test_websocket_done_signal`: Verify done chunk received.
- `test_websocket_invalid_session`: Connect with bad ID, verify close.

---

### M7-WP04: Trace and skill routes

**Dependencies:** M7-WP01
**Complexity:** M

**Files to create:**

```
src/caw/api/routes/traces.py
src/caw/api/routes/skills.py
tests/unit/api/test_traces.py
tests/unit/api/test_skills.py
```

**Specification:**

Implement remaining read-only routes:

```
GET  /api/v1/traces/{trace_id}         → Get trace events
GET  /api/v1/traces/{trace_id}/summary → Get run summary
GET  /api/v1/skills                    → List skills
GET  /api/v1/skills/{id}              → Get skill details
GET  /api/v1/skills/packs             → List packs
GET  /api/v1/providers                → List providers
GET  /api/v1/providers/{id}/health    → Provider health
```

**Acceptance criteria:**

1. Trace endpoints return trace events and summaries.
2. Skill endpoints list available skills and packs.
3. Provider endpoints list configured providers and run health checks.
4. All endpoints return proper APIResponse envelopes.
5. `ruff check` and `mypy` pass.

**Tests:**

- One test per endpoint verifying response structure and status code.

---

### M7-WP05: CLI entry point

**Dependencies:** M7-WP01
**Complexity:** M

**Files to create:**

```
src/caw/cli/main.py
tests/unit/cli/test_main.py
```

**Add dependency to `pyproject.toml`:**
```toml
"click>=8.0",
"rich>=13.0",
```

Also add to `pyproject.toml`:
```toml
[project.scripts]
caw = "caw.cli.main:cli"
```

**Specification:**

Implement the CLI from Technical Specification §19.2. Initially just:

```
caw serve       — Start API server
caw chat        — Interactive chat in terminal
caw db init     — Initialize database
caw db migrate  — Run migrations
caw config show — Show config (secrets redacted)
caw version     — Show version
```

Other commands (`caw research`, `caw deliberate`, `caw eval`) are added in their respective milestones.

**Acceptance criteria:**

1. `caw version` prints the version string.
2. `caw config show` prints the current config with API keys redacted.
3. `caw db init` creates the database and runs migrations.
4. `caw serve` starts uvicorn on the configured host/port.
5. `caw chat` starts an interactive loop (exits on Ctrl+C or "exit").
6. `ruff check` and `mypy` pass.

**Tests:**

- `test_version_command`: Invoke, verify version output.
- `test_config_show_redacted`: Verify API keys show as `***`.
- `test_db_init`: Invoke in temp dir, verify database created.

---

## Milestone 8: Research Capability

**Goal:** The system can ingest sources, retrieve relevant content, produce citation-aware synthesis, and export reports. After this milestone, the research-to-report journey (Design Document §14.1) is functional.

**Prerequisites:** Milestone 7 complete.

---

### M8-WP01: Ingestion pipeline

**Dependencies:** M1-WP05 (SourceRepository)
**Complexity:** L

**Files to create:**

```
src/caw/capabilities/research/ingest.py
tests/unit/capabilities/research/test_ingest.py
tests/fixtures/research/sample.txt
tests/fixtures/research/sample.md
tests/fixtures/research/sample.pdf
```

**Add dependencies:**
```toml
"pypdf>=4.0",
"beautifulsoup4>=4.12",
"markdownify>=0.12",
```

**Specification:** Implement `IngestPipeline` from Technical Specification §9.1.1. Supports .txt, .md, .pdf, .html, .csv, .json. Each source is chunked (default 1000 tokens, 200 token overlap), stored in the sources table, and emits trace events.

**Acceptance criteria:**

1. Text files ingest and produce Source records.
2. PDF files are text-extracted and ingested.
3. HTML files are converted to text and ingested.
4. Content is chunked with configurable size and overlap.
5. Content hash (SHA-256) is computed and stored.
6. Duplicate sources (same hash) are detected and skipped.
7. Trace events emitted for each ingestion.
8. `ruff check` and `mypy` pass.

**Tests:**

- `test_ingest_text_file`: Ingest .txt, verify source record.
- `test_ingest_markdown`: Ingest .md, verify content preserved.
- `test_ingest_pdf`: Ingest .pdf fixture, verify text extracted.
- `test_chunking`: Ingest large text, verify chunk count and overlap.
- `test_duplicate_detection`: Ingest same file twice, verify skipped.
- `test_content_hash`: Verify SHA-256 hash computed.

---

### M8-WP02: Retrieval

**Dependencies:** M8-WP01
**Complexity:** M

**Files to create:**

```
src/caw/capabilities/research/retrieve.py
tests/unit/capabilities/research/test_retrieve.py
```

**Specification:** Implement `Retriever` from Technical Specification §9.1.2. Keyword retrieval uses SQLite FTS5. Semantic retrieval is deferred to a later WP (requires embedding infrastructure). Hybrid retrieval falls back to keyword-only when embeddings are not available.

**Acceptance criteria:**

1. Keyword search returns ranked results from ingested sources.
2. Results include source ID, chunk content, and relevance score.
3. `top_k` parameter limits result count.
4. Empty query returns empty results.
5. Trace events emitted for each retrieval.
6. `ruff check` and `mypy` pass.

**Tests:**

- `test_retrieve_keyword_match`: Ingest text with known terms, retrieve, verify found.
- `test_retrieve_no_match`: Query with no matching terms, verify empty.
- `test_retrieve_top_k`: Verify result count limited by top_k.
- `test_retrieve_provenance`: Verify source_id present on all results.

---

### M8-WP03: Synthesis

**Dependencies:** M8-WP02, M5-WP04 (Engine)
**Complexity:** L

**Files to create:**

```
src/caw/capabilities/research/synthesize.py
tests/unit/capabilities/research/test_synthesize.py
```

**Specification:** Implement `Synthesizer` from Technical Specification §9.1.3. Calls the model provider with retrieved content and a synthesis skill to produce citation-aware output.

```python
@dataclass
class SynthesisResult:
    query: str
    claims: list[SynthesizedClaim]
    uncertainty_markers: list[str]
    source_map: dict[str, str]       # citation_id → source excerpt
    raw_output: str                  # Full model output
    trace_id: str

@dataclass
class SynthesizedClaim:
    text: str
    citation_ids: list[str]
    confidence: float | None = None
```

**Acceptance criteria:**

1. Synthesis produces structured output with claims and citations.
2. Each claim links to at least one source citation.
3. Uncertainty markers are generated when sources conflict.
4. Source map connects citation IDs to source excerpts.
5. Trace events emitted.
6. `ruff check` and `mypy` pass.

**Tests:** Use MockProvider with structured responses.

- `test_synthesize_basic`: Provide retrieval results, verify claims produced.
- `test_synthesize_citations_linked`: Verify citation_ids reference valid sources.
- `test_synthesize_uncertainty`: Provide conflicting sources, verify uncertainty markers.

---

### M8-WP04: Export

**Dependencies:** M8-WP03
**Complexity:** M

**Files to create:**

```
src/caw/capabilities/research/export.py
tests/unit/capabilities/research/test_export.py
```

**Specification:** Implement export from Technical Specification §9.1.4. Supports Markdown and JSON initially. DOCX support added later.

**Acceptance criteria:**

1. Markdown export produces a structured report with inline citations.
2. JSON export produces machine-readable claims, citations, and evidence map.
3. Exported artifacts are stored in the artifacts table.
4. Exported files are written to the configured artifact directory.
5. `ruff check` and `mypy` pass.

**Tests:**

- `test_export_markdown`: Export synthesis result, verify Markdown structure.
- `test_export_json`: Export, verify JSON schema.
- `test_export_creates_artifact`: Verify artifact record in database.

---

### M8-WP05: Research API routes and CLI

**Dependencies:** M8-WP01 through M8-WP04, M7-WP01
**Complexity:** M

**Files to create:**

```
src/caw/api/routes/research.py
tests/unit/api/test_research.py
```

**Specification:** Add research routes from Technical Specification §13.2:

```
POST /api/v1/research/ingest
POST /api/v1/research/retrieve
POST /api/v1/research/synthesize
POST /api/v1/research/export
```

Add CLI commands: `caw research ingest <path>`, `caw research query "<question>"`.

**Acceptance criteria:**

1. All four research endpoints functional.
2. CLI ingest command ingests files.
3. CLI query command runs retrieval + synthesis and prints result.
4. `ruff check` and `mypy` pass.

**Tests:**

- One test per endpoint verifying request/response flow.

---

## Milestone 9: Deliberation Capability

**Goal:** The system supports structured multi-frame deliberation with rhetoric analysis and disagreement surfaces. After this milestone, the question-to-deliberation journey (Design Document §14.2) is functional.

**Prerequisites:** Milestone 7 complete (API), Milestone 5 complete (Engine).

---

### M9-WP01: Frame management

**Dependencies:** M3-WP04 (SkillRegistry)
**Complexity:** M

**Files to create:**

```
src/caw/capabilities/deliberation/frames.py
tests/unit/capabilities/deliberation/test_frames.py
```

**Specification:** Implement `FrameConfig` and frame management from Technical Specification §9.2.2. Each frame resolves a skill and optionally targets a specific provider.

**Acceptance criteria:**

1. Frame configs can be created with skill ID and label.
2. Frames resolve their skills via the SkillRegistry.
3. Invalid skill IDs produce clear error messages.
4. `ruff check` and `mypy` pass.

**Tests:**

- `test_frame_config_creation`: Create frame, verify fields.
- `test_frame_skill_resolution`: Resolve skill from registry, verify body.
- `test_frame_invalid_skill`: Nonexistent skill, verify error.

---

### M9-WP02: Deliberation engine

**Dependencies:** M9-WP01, M5-WP04
**Complexity:** L

**Files to create:**

```
src/caw/capabilities/deliberation/engine.py
tests/unit/capabilities/deliberation/test_engine.py
```

**Specification:** Implement `DeliberationEngine` from Technical Specification §9.2.1. Orchestrates the full deliberation flow: initial positions → critique rounds → disagreement surface → optional synthesis.

**Acceptance criteria:**

1. Deliberation produces positions from each frame.
2. Critique rounds produce responses between frames.
3. Disagreement surface identifies agreements and disagreements.
4. Number of rounds is configurable.
5. Each step is traced.
6. `ruff check` and `mypy` pass.

**Tests:** Use MockProvider with frame-specific responses.

- `test_deliberate_two_frames`: Two frames, verify both produce positions.
- `test_deliberate_critique_round`: Verify critique responses generated.
- `test_deliberate_disagreement_surface`: Verify surface populated.
- `test_deliberate_zero_rounds`: No critique rounds, just positions + surface.

---

### M9-WP03: Rhetoric analysis

**Dependencies:** M9-WP02
**Complexity:** M

**Files to create:**

```
src/caw/capabilities/deliberation/rhetoric.py
tests/unit/capabilities/deliberation/test_rhetoric.py
```

**Specification:** Implement `RhetoricAnalysis` from Technical Specification §9.2.4. Uses a model call to analyze all frame outputs for rhetorical devices, biases, inconsistencies, and cross-frame contradictions.

**Acceptance criteria:**

1. Analysis identifies rhetorical devices with type, frame, excerpt, and severity.
2. Analysis identifies cognitive/framing biases.
3. Analysis detects internal inconsistencies within frames.
4. Analysis detects contradictions between frames.
5. `ruff check` and `mypy` pass.

**Tests:** Use MockProvider with structured analysis responses.

- `test_rhetoric_devices_detected`: Provide text with known device, verify detected.
- `test_rhetoric_biases_detected`: Verify bias detection.
- `test_rhetoric_cross_frame_contradictions`: Two contradicting frames, verify detected.

---

### M9-WP04: Deliberation API routes and CLI

**Dependencies:** M9-WP02, M9-WP03, M7-WP01
**Complexity:** M

**Files to create:**

```
src/caw/api/routes/deliberation.py
tests/unit/api/test_deliberation.py
```

**Specification:** Add deliberation routes:

```
POST /api/v1/deliberation/run
GET  /api/v1/deliberation/{id}
GET  /api/v1/deliberation/{id}/surface
```

Add CLI command: `caw deliberate "<question>"`.

**Acceptance criteria:**

1. POST starts deliberation and returns result.
2. GET retrieves completed deliberation.
3. Surface endpoint returns disagreement surface.
4. CLI command runs deliberation and prints result.
5. `ruff check` and `mypy` pass.

**Tests:**

- One test per endpoint.

---

## Milestone 10: Workspace Capability

**Goal:** The system can perform file operations, propose patches, and execute commands with safety constraints. After this milestone, the task-to-action journey (Design Document §14.3) is functional.

**Prerequisites:** Milestone 5 complete (Engine with permissions).

---

### M10-WP01: Local file operations

**Dependencies:** M5-WP03 (PermissionGate)
**Complexity:** M

**Files to create:**

```
src/caw/capabilities/workspace/local.py
tests/unit/capabilities/workspace/test_local.py
```

**Specification:** Implement local file operations from Technical Specification §9.3.1 (read operations). All operations validate paths against workspace config and emit trace events.

**Acceptance criteria:**

1. `list_files()` lists directory contents.
2. `read_file()` reads file content.
3. `search_files()` finds files matching a glob pattern.
4. Path validation prevents access outside allowed paths in strict mode.
5. Trace events emitted.
6. `ruff check` and `mypy` pass.

**Tests:**

- `test_list_files`: Create temp dir with files, verify listing.
- `test_read_file`: Write then read, verify content.
- `test_search_files`: Create files matching pattern, verify found.
- `test_path_validation_strict`: Strict mode, path outside allowed, verify error.
- `test_path_validation_permissive`: Permissive mode, verify access allowed.

---

### M10-WP02: Patch proposal and application

**Dependencies:** M10-WP01
**Complexity:** M

**Files to create:**

```
src/caw/capabilities/workspace/patch.py
tests/unit/capabilities/workspace/test_patch.py
```

**Specification:** Implement `PatchProposal` from Technical Specification §9.3.2. Patches include conflict detection (via content hash), context lines, and reverse patches for rollback.

**Acceptance criteria:**

1. Patch proposals include hunks with context lines.
2. Content hash is checked before application (conflict detection).
3. Reverse patches are generated for rollback.
4. Application requires approval (gate check).
5. `ruff check` and `mypy` pass.

**Tests:**

- `test_create_patch`: Generate patch for a known change, verify hunks.
- `test_apply_patch`: Apply patch, verify file modified.
- `test_patch_conflict`: Modify file, attempt apply, verify conflict detected.
- `test_reverse_patch`: Apply then reverse, verify original restored.

---

### M10-WP03: Command execution

**Dependencies:** M5-WP03
**Complexity:** M

**Files to create:**

```
src/caw/capabilities/workspace/executor.py
tests/unit/capabilities/workspace/test_executor.py
```

**Specification:** Implement constrained command execution from Technical Specification §9.3.1. Commands run with timeout, configurable working directory, and are always traced.

**Acceptance criteria:**

1. Commands execute and return stdout, stderr, exit code.
2. Timeout kills the process after configured seconds.
3. Working directory is configurable.
4. Execution requires approval (gate check).
5. All executions are traced (command, exit code, duration).
6. `ruff check` and `mypy` pass.

**Tests:**

- `test_execute_simple`: Run `echo hello`, verify output.
- `test_execute_timeout`: Run `sleep 60` with 1s timeout, verify killed.
- `test_execute_working_dir`: Run `pwd` in temp dir, verify path.
- `test_execute_failure`: Run `false`, verify exit code 1.
- `test_execute_traced`: Verify trace event emitted.

---

### M10-WP04: Write and delete operations

**Dependencies:** M10-WP01, M5-WP03
**Complexity:** M

**Files to create:**

```
src/caw/capabilities/workspace/writes.py
tests/unit/capabilities/workspace/test_writes.py
```

**Specification:** Implement write, move, copy, and delete operations. All gated by permissions.

**Acceptance criteria:**

1. Write creates or overwrites files.
2. Move relocates files.
3. Copy duplicates files.
4. Delete removes files.
5. All mutations require approval gate checks.
6. All mutations are traced.
7. `ruff check` and `mypy` pass.

**Tests:**

- One test per operation verifying the file system change.
- Test that mutations emit trace events.

---

### M10-WP05: Workspace API routes and CLI

**Dependencies:** M10-WP01 through M10-WP04, M7-WP01
**Complexity:** M

**Files to create:**

```
src/caw/api/routes/workspace.py
tests/unit/api/test_workspace.py
```

**Specification:** Add workspace routes from Technical Specification §13.2.

**Acceptance criteria:**

1. All workspace endpoints functional.
2. Write/execute/delete endpoints enforce approval gates.
3. `ruff check` and `mypy` pass.

**Tests:**

- One test per endpoint.

---

## Milestone 11: Evaluation Layer

**Goal:** The system can define, run, and score evaluation tasks, compare results, and detect regressions. After this milestone, the evaluation journey (Design Document §14.4) is functional.

**Prerequisites:** Milestones 8 and 9 complete (capabilities to evaluate).

---

### M11-WP01: Task definition loader

**Dependencies:** none
**Complexity:** M

**Files to create:**

```
src/caw/evaluation/tasks.py
tests/unit/evaluation/test_tasks.py
tests/fixtures/tasks/sample_task.toml
```

**Specification:** Parse task TOML files from Technical Specification §12.1.

**Acceptance criteria:**

1. Valid task files parse into `EvalTask` dataclasses.
2. Invalid tasks produce clear error messages.
3. Tasks can reference fixture files for inputs.
4. `ruff check` and `mypy` pass.

**Tests:**

- `test_load_valid_task`: Parse fixture, verify all fields.
- `test_load_invalid_task`: Missing required field, verify error.

---

### M11-WP02: Scoring framework

**Dependencies:** M11-WP01
**Complexity:** M

**Files to create:**

```
src/caw/evaluation/scorer.py
tests/unit/evaluation/test_scorer.py
```

**Specification:** Implement the `Scorer` protocol and `CompositeScorer` from Technical Specification §12.2. Implement at least `latency` and `token_efficiency` scorers (these don't require LLM calls). LLM-as-judge scorers (citation_accuracy, claim_fidelity) are implemented as separate scorers that call the engine.

**Acceptance criteria:**

1. Scorer protocol is defined and runtime-checkable.
2. CompositeScorer aggregates individual scores with configurable weights.
3. LatencyScorer scores based on trace duration.
4. TokenEfficiencyScorer scores based on tokens/quality ratio.
5. `ruff check` and `mypy` pass.

**Tests:**

- `test_latency_scorer`: Provide trace with known duration, verify score.
- `test_token_efficiency_scorer`: Provide known counts, verify score.
- `test_composite_scorer`: Combine two scorers with weights, verify aggregation.

---

### M11-WP03: Evaluation runner

**Dependencies:** M11-WP01, M11-WP02, M5-WP04
**Complexity:** L

**Files to create:**

```
src/caw/evaluation/runner.py
tests/unit/evaluation/test_runner.py
```

**Specification:** Implement `EvalRunner` from Technical Specification §12. Runs a task against a provider/model/skill-pack combination, captures the full trace, and scores the result.

**Acceptance criteria:**

1. Runner executes task and captures trace.
2. Runner scores result using configured scorers.
3. Results are stored in eval_runs table.
4. `ruff check` and `mypy` pass.

**Tests:**

- `test_run_task`: Run sample task with MockProvider, verify EvalRun record.
- `test_run_captures_trace`: Verify trace_id links to trace events.
- `test_run_scores_result`: Verify scores populated.

---

### M11-WP04: Comparator and regression detector

**Dependencies:** M11-WP03
**Complexity:** M

**Files to create:**

```
src/caw/evaluation/comparator.py
src/caw/evaluation/regression.py
tests/unit/evaluation/test_comparator.py
tests/unit/evaluation/test_regression.py
```

**Specification:** Implement `Comparator` and `RegressionDetector` from Technical Specification §12.3 and §12.4. Regression detection uses median and IQR.

**Acceptance criteria:**

1. Comparator produces side-by-side score comparison.
2. Regression detector uses median and IQR (not mean and stddev).
3. Regression alert triggers when score drops below median - 1.5*IQR of baseline.
4. `ruff check` and `mypy` pass.

**Tests:**

- `test_compare_two_runs`: Compare, verify dimension breakdown.
- `test_regression_detected`: Insert declining scores, verify alert.
- `test_no_regression`: Stable scores, verify no alert.
- `test_median_not_mean`: Verify median used, not mean.

---

### M11-WP05: Evaluation API routes and CLI

**Dependencies:** M11-WP03, M11-WP04, M7-WP01
**Complexity:** M

**Files to create:**

```
src/caw/api/routes/evaluation.py
tests/unit/api/test_evaluation.py
```

**Specification:** Add evaluation routes:

```
POST /api/v1/eval/run
GET  /api/v1/eval/runs
GET  /api/v1/eval/runs/{id}
POST /api/v1/eval/compare
POST /api/v1/eval/regression
```

Add CLI commands: `caw eval run <task_id>`, `caw eval compare <id> <id>`.

**Acceptance criteria:**

1. All evaluation endpoints functional.
2. CLI commands work.
3. `ruff check` and `mypy` pass.

**Tests:**

- One test per endpoint.

---

## Milestone 12: Integration and Hardening

**Goal:** All components are wired together, cross-cutting concerns are complete, documentation is final, and the system passes a full integration test suite. The project is usable as a coherent tool.

**Prerequisites:** All prior milestones complete.

---

### M12-WP01: Approval gate flow

**Dependencies:** M7-WP02
**Complexity:** M

**Files to create:**

```
src/caw/api/routes/approvals.py
tests/integration/test_approval_flow.py
```

**Specification:** Implement the approval API routes:

```
GET  /api/v1/approvals/pending
POST /api/v1/approvals/{id}
```

Wire the full approval flow: workspace operation → gate check → approval request stored → API exposes pending → user approves → operation proceeds.

**Acceptance criteria:**

1. Pending approvals are listed via API.
2. Approve/deny via API resumes/cancels the operation.
3. Timeout auto-denies after configured seconds.
4. Full flow traced end-to-end.

**Tests:**

- `test_full_approval_flow`: Write operation → gate → approve → verify file written.
- `test_deny_cancels_operation`: Write → gate → deny → verify file not written.
- `test_approval_timeout`: Write → gate → wait → verify auto-denied.

---

### M12-WP02: Builtin skill documents

**Dependencies:** M3-WP01
**Complexity:** M

**Files to create:**

```
skills/builtin/research_operator.md
skills/builtin/deliberation_director.md
skills/builtin/workspace_operator.md
skills/builtin/critique_agent.md
skills/builtin/synthesis_agent.md
skills/builtin/rhetoric_analyst.md
```

**Specification:** Write the actual skill documents that ship with the platform. Each follows the Claude Skills standard format with YAML frontmatter. Content is derived from the Design Document's design principles and the Technical Specification's capability descriptions.

Each skill must:
- Have valid frontmatter (passes validation).
- Have substantive body content (not placeholder).
- Define the perspective, constraints, tool usage guidance, and output format for its role.
- Be usable by a real model to produce the described behavior.

**Acceptance criteria:**

1. All six skill files pass `validate_skill()`.
2. Each skill body is at least 200 words of substantive guidance.
3. Each skill has correct `requires_tools` and `requires_permissions`.
4. Skills can be loaded by the SkillRegistry.

**Tests:**

- `test_builtin_skills_valid`: Load all builtin skills, validate each.

---

### M12-WP03: Default skill packs

**Dependencies:** M12-WP02, M3-WP03
**Complexity:** S

**Files to create:**

```
skills/packs/deep_research.toml
skills/packs/adversarial_review.toml
skills/packs/workspace_ops.toml
```

**Specification:** Create the default skill packs from Technical Specification §7.3.

**Acceptance criteria:**

1. All pack files parse as valid SkillPacks.
2. All referenced skill IDs exist in the builtin set.
3. Packs are loadable by the SkillRegistry.

**Tests:**

- `test_default_packs_valid`: Load all packs, verify no errors.

---

### M12-WP04: End-to-end integration tests

**Dependencies:** All prior milestones
**Complexity:** L

**Files to create:**

```
tests/integration/test_research_journey.py
tests/integration/test_deliberation_journey.py
tests/integration/test_workspace_journey.py
tests/integration/test_evaluation_journey.py
```

**Specification:** Implement the four key user journeys from Design Document §14 as integration tests. Each test exercises the full stack from API request through engine, capability, protocol (MockProvider), storage, and traces.

**`test_research_journey.py`:**

1. Create research session via API.
2. Ingest source files.
3. Run retrieval query.
4. Run synthesis.
5. Export report.
6. Verify: source records, citations, artifact, trace events.

**`test_deliberation_journey.py`:**

1. Create deliberation session.
2. Run deliberation with two frames.
3. Verify: positions, critiques, rhetoric analysis, disagreement surface.
4. Verify: all trace events.

**`test_workspace_journey.py`:**

1. Create workspace session.
2. List files.
3. Read file.
4. Propose patch.
5. Approve patch.
6. Verify: file modified, trace events, approval flow.

**`test_evaluation_journey.py`:**

1. Run eval task.
2. Run same task again.
3. Compare runs.
4. Check regression.
5. Verify: eval_run records, scores, comparison result.

**Acceptance criteria:**

1. All four journey tests pass with MockProvider.
2. Each test verifies database state, trace events, and API responses.
3. Tests are independent (each creates its own database).

---

### M12-WP05: README and documentation finalization

**Dependencies:** All prior WPs
**Complexity:** M

**Files to create/update:**

```
README.md (update)
docs/quickstart.md (create)
```

**Specification:**

Update `README.md` with:
- Project description.
- Installation instructions (uv sync).
- Quick start (configure, init db, serve).
- Architecture overview (link to docs).
- Development setup (pre-commit, testing).

Create `docs/quickstart.md` with step-by-step first-run guide.

**Acceptance criteria:**

1. README has installation, quickstart, and architecture sections.
2. Quickstart guide is followable by a new user.
3. No placeholder text remains.

---

### M12-WP06: Version bump to 0.1.0 release

**Dependencies:** M12-WP04, M12-WP05
**Complexity:** S

**Specification:**

1. Update `CHANGELOG.md` with all changes in the `[0.1.0]` release section.
2. Verify `__version__.py` reads `"0.1.0"`.
3. Verify `pyproject.toml` version is `"0.1.0"`.
4. Tag the release `v0.1.0` in git.
5. All tests pass.
6. `ruff check`, `ruff format --check`, and `mypy` all pass.

**Acceptance criteria:**

1. Version is consistent across `__version__.py`, `pyproject.toml`, and git tag.
2. CHANGELOG has complete `[0.1.0]` section.
3. Full test suite passes.
4. All linting passes.

---

## Appendix A: Dependency Graph

```
M0-WP01 → M0-WP02
M0-WP01 → M0-WP03

M1-WP01 (no deps)
M1-WP02 → M1-WP01
M1-WP03 → M1-WP01
M1-WP04 → M1-WP02, M1-WP03
M1-WP05 → M1-WP04

M2-WP01 (no deps within M2)
M2-WP02 → M2-WP01
M2-WP03 → M2-WP01, M1-WP02
M2-WP04 → M2-WP01, M1-WP02
M2-WP05 → M2-WP02, M2-WP03, M2-WP04, M1-WP02

M3-WP01 (no deps within M3)
M3-WP02 → M3-WP01
M3-WP03 → M3-WP01
M3-WP04 → M3-WP01, M3-WP02, M3-WP03, M1-WP02

M4-WP01 → M1-WP05
M4-WP02 → M4-WP01
M4-WP03 → M4-WP01

M5-WP01 → M1-WP05
M5-WP02 → M2-WP05, M1-WP02
M5-WP03 → M1-WP03, M4-WP02
M5-WP04 → M5-WP01, M5-WP02, M5-WP03, M3-WP04, M4-WP01

M6-WP01 → M5-WP04

M7-WP01 (no deps within M7)
M7-WP02 → M7-WP01
M7-WP03 → M7-WP01, M6-WP01
M7-WP04 → M7-WP01
M7-WP05 → M7-WP01

M8-WP01 → M1-WP05
M8-WP02 → M8-WP01
M8-WP03 → M8-WP02, M5-WP04
M8-WP04 → M8-WP03
M8-WP05 → M8-WP01..WP04, M7-WP01

M9-WP01 → M3-WP04
M9-WP02 → M9-WP01, M5-WP04
M9-WP03 → M9-WP02
M9-WP04 → M9-WP02, M9-WP03, M7-WP01

M10-WP01 → M5-WP03
M10-WP02 → M10-WP01
M10-WP03 → M5-WP03
M10-WP04 → M10-WP01, M5-WP03
M10-WP05 → M10-WP01..WP04, M7-WP01

M11-WP01 (no deps within M11)
M11-WP02 → M11-WP01
M11-WP03 → M11-WP01, M11-WP02, M5-WP04
M11-WP04 → M11-WP03
M11-WP05 → M11-WP03, M11-WP04, M7-WP01

M12-WP01 → M7-WP02
M12-WP02 → M3-WP01
M12-WP03 → M12-WP02, M3-WP03
M12-WP04 → all prior milestones
M12-WP05 → all prior milestones
M12-WP06 → M12-WP04, M12-WP05
```

## Appendix B: Work Package Summary

| Milestone | WPs | Focus |
|-----------|-----|-------|
| M0: Bootstrap | 3 | Repo, scaffold, changelog |
| M1: Foundation | 5 | Config, models, storage, migrations, repositories |
| M2: Protocol | 5 | Provider abstraction, mock, Anthropic, OpenAI, registry |
| M3: Skills | 4 | Loader, validator, resolver, packs, registry |
| M4: Traces | 3 | Collector, schemas, replay |
| M5: Orchestration | 4 | Sessions, router, permissions, engine |
| M6: Chat | 1 | Chat handler with streaming |
| M7: API | 5 | FastAPI app, routes, WebSocket, CLI |
| M8: Research | 5 | Ingest, retrieve, synthesize, export, routes |
| M9: Deliberation | 4 | Frames, engine, rhetoric, routes |
| M10: Workspace | 5 | Files, patches, execution, writes, routes |
| M11: Evaluation | 5 | Tasks, scorers, runner, comparator, routes |
| M12: Integration | 6 | Approvals, skills, packs, E2E tests, docs, release |
| **Total** | **55** | |

## Appendix C: Parallelism Opportunities

The following milestones can proceed in parallel once their prerequisites are met:

- **M2, M3, M4** can all proceed in parallel after M1 completes.
- **M8, M9, M10** can all proceed in parallel after M7 completes.
- Within M1: WP01 and WP03 can be parallel. WP02 depends on WP01.
- Within M2: WP03 and WP04 can be parallel (both depend only on WP01 and M1-WP02).
- Within M7: WP02, WP03, WP04, and WP05 can mostly be parallel after WP01.

This parallelism is optional. A single implementer can proceed sequentially through the milestones.
