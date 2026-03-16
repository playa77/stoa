# Security Hardening Roadmap

## Canonical Agent Workbench — API Gateway

**Version:** 1.0.0
**Status:** Ready for implementation
**Date:** 2026-03-16
**Companion to:** Technical Specification v1.0.0, Atomic Roadmap v1.0.0

---

## 0. Threat Summary

The CAW API server (FastAPI on port 8420) currently exposes every endpoint — including endpoints that proxy requests to paid LLM providers — with **zero authentication**. Any process or network peer that can reach the port can:

1. Send unlimited chat messages through `/api/v1/sessions/{id}/messages`, consuming Anthropic/OpenAI API credits with no constraint.
2. Execute workspace commands via `/api/v1/workspace/execute` (subject to approval gates, but the approval endpoint itself is unauthenticated).
3. Read all session history, traces, evaluation data, and configuration.
4. Approve pending permission gates via `/api/v1/approvals/{id}`, bypassing the human-in-the-loop safety model entirely.

The default `127.0.0.1` bind mitigates remote network attacks, but does **not** protect against:

- Malicious local processes (malware, browser extensions, compromised npm packages).
- SSRF from any locally running web application.
- Accidental `0.0.0.0` bind (the config allows it with only a log warning).
- Any scenario where the operator exposes the port via tunneling (ngrok, ssh -R, tailscale).

**Risk rating: Critical.** The approval gate bypass alone collapses the entire safety architecture. The credit-drain vector makes this a direct financial exposure.

---

## 1. Security Architecture Decisions

### SD-01: Bearer token authentication for all API endpoints

Every HTTP and WebSocket request must include a valid bearer token in the `Authorization` header. Requests without a valid token receive `401 Unauthorized`. No exceptions.

**Rationale:** Simplest scheme that blocks unauthorized access. No user database needed (single-operator system). Token is generated at first run and stored locally.

### SD-02: API key generated at first run, stored in local file

On first startup (or when no key file exists), the server generates a cryptographically random API key (32 bytes, hex-encoded = 64 characters), writes it to `~/.config/caw/api_key`, and prints it to stdout once. The file is created with `0600` permissions (owner-read/write only).

**Rationale:** Avoids forcing the operator to invent a password. Avoids storing the key in the main config file (which may be version-controlled). The key file location follows the same XDG convention as the config.

### SD-03: Rate limiting per-session and global

Requests are rate-limited to prevent runaway credit consumption even with a valid token. Default: 60 requests/minute global, 20 requests/minute per session. Configurable in `[api]` config section.

**Rationale:** Defense-in-depth. Even an authenticated client (or a compromised token) cannot drain credits instantly.

### SD-04: Bind-address safeguard

If `api.host` is set to anything other than `127.0.0.1` or `::1`, the server refuses to start unless `api.require_auth` is explicitly `true` in config (which it is by default, but this prevents a misconfiguration where auth is disabled AND the server is network-exposed).

**Rationale:** Prevents the single most dangerous misconfiguration.

### SD-05: Provider API keys stay server-side

The current design (env var names in config, values read from env at runtime, never sent to clients) is correct and must not change. The API gateway proxies provider requests; clients never see provider keys.

**Rationale:** Already implemented correctly per Technical Specification §17.1. Confirmed as the right architecture — a passthrough design would expose raw keys to any frontend.

---

## 2. Work Packages

### Milestone ordering rationale

These work packages are ordered by dependency and risk reduction:

1. **S-WP01–02** establish the key and middleware (blocks all unauthorized access).
2. **S-WP03** protects the WebSocket surface (same auth, different transport).
3. **S-WP04** adds rate limiting (defense-in-depth against token compromise).
4. **S-WP05** adds the bind-address safeguard (prevents misconfiguration).
5. **S-WP06** adds key rotation (operational hygiene).
6. **S-WP07** integrates with the config system and documents everything.

No work package depends on a later one. Each is independently testable and deployable.

---

### S-WP01: API key generation and storage

**Dependencies:** M1-WP02 (configuration system must exist)
**Complexity:** S (< 100 lines)

**Files to create:**

```
src/caw/api/auth.py
tests/unit/api/test_auth.py
```

**Specification:**

Create `src/caw/api/auth.py` with the following:

```python
"""API authentication for CAW.

Handles generation, storage, and validation of the local API key
used to authenticate all requests to the CAW API server.
"""

import secrets
import logging
from pathlib import Path

from caw.errors import ConfigError

logger = logging.getLogger(__name__)

# Length of the generated API key in bytes.
# 32 bytes = 64 hex characters = 256 bits of entropy.
_KEY_LENGTH_BYTES: int = 32

# Default filename for the API key file, relative to config directory.
_KEY_FILENAME: str = "api_key"


def get_key_path(config_dir: Path) -> Path:
    """Return the full path to the API key file.

    Args:
        config_dir: The CAW configuration directory
            (typically ~/.config/caw/).

    Returns:
        Path to the api_key file within that directory.
    """
    return config_dir / _KEY_FILENAME


def generate_api_key() -> str:
    """Generate a cryptographically random API key.

    Returns:
        A 64-character hex string (32 bytes of entropy).
    """
    return secrets.token_hex(_KEY_LENGTH_BYTES)


def load_or_create_api_key(config_dir: Path) -> str:
    """Load the API key from disk, or generate and persist a new one.

    If the key file does not exist:
        1. Create the config directory if needed (mode 0o700).
        2. Generate a new key.
        3. Write it to the key file (mode 0o600).
        4. Log an INFO message that a new key was created.
        5. Return the key.

    If the key file exists:
        1. Read and strip whitespace.
        2. Validate that it is a non-empty hex string of exactly 64 characters.
        3. Return the key.

    Args:
        config_dir: The CAW configuration directory.

    Returns:
        The API key string.

    Raises:
        ConfigError: If the existing key file contains an invalid key.
    """
    key_path = get_key_path(config_dir)

    if key_path.exists():
        raw = key_path.read_text().strip()
        if len(raw) != _KEY_LENGTH_BYTES * 2 or not _is_hex(raw):
            raise ConfigError(
                message=f"API key file at {key_path} contains an invalid key. "
                        f"Expected a {_KEY_LENGTH_BYTES * 2}-character hex string.",
                code="invalid_api_key_file",
                details={"path": str(key_path), "key_length": len(raw)},
            )
        return raw

    # Generate new key.
    config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    key = generate_api_key()
    key_path.write_text(key + "\n")
    key_path.chmod(0o600)
    logger.info(
        "Generated new API key. Stored at: %s",
        key_path,
    )
    return key


def validate_bearer_token(provided: str, expected: str) -> bool:
    """Constant-time comparison of a provided token against the expected key.

    Uses secrets.compare_digest to prevent timing attacks.

    Args:
        provided: The token from the Authorization header.
        expected: The stored API key.

    Returns:
        True if the tokens match, False otherwise.
    """
    return secrets.compare_digest(provided, expected)


def _is_hex(s: str) -> bool:
    """Check whether a string is valid hexadecimal."""
    try:
        int(s, 16)
        return True
    except ValueError:
        return False
```

**Acceptance criteria:**

1. `generate_api_key()` returns a 64-character hex string.
2. `generate_api_key()` returns a different value on each call.
3. `load_or_create_api_key()` creates the key file with mode `0o600` when it does not exist.
4. `load_or_create_api_key()` creates the config directory with mode `0o700` if needed.
5. `load_or_create_api_key()` returns the same key on subsequent calls (reads from file).
6. `load_or_create_api_key()` raises `ConfigError` with code `"invalid_api_key_file"` for a key file containing non-hex content.
7. `load_or_create_api_key()` raises `ConfigError` for a key file containing a hex string of wrong length.
8. `validate_bearer_token()` returns `True` for matching tokens.
9. `validate_bearer_token()` returns `False` for non-matching tokens.
10. `ruff check` and `mypy --strict` pass on `src/caw/api/auth.py`.

**Tests (`tests/unit/api/test_auth.py`):**

- `test_generate_api_key_length`: Assert 64 characters.
- `test_generate_api_key_is_hex`: Assert all characters are valid hex.
- `test_generate_api_key_uniqueness`: Call twice, assert different.
- `test_load_creates_new_key`: Use `tmp_path`, assert file created, mode `0o600`.
- `test_load_reads_existing_key`: Write a valid key, assert it is returned unchanged.
- `test_load_rejects_invalid_hex`: Write "not-hex" to file, assert `ConfigError`.
- `test_load_rejects_wrong_length`: Write 32-char hex, assert `ConfigError`.
- `test_load_creates_config_dir`: Use non-existent subdir in `tmp_path`, assert dir created with mode `0o700`.
- `test_validate_matching`: Assert `True`.
- `test_validate_non_matching`: Assert `False`.
- `test_validate_empty_string`: Assert `False` when provided is empty.

---

### S-WP02: Authentication middleware for HTTP routes

**Dependencies:** S-WP01, M7 (API routes must exist; specifically `src/caw/api/app.py`)
**Complexity:** M (100–200 lines)

**Files to create or modify:**

```
src/caw/api/middleware.py       (create)
src/caw/api/app.py              (modify — add middleware)
src/caw/api/dependencies.py     (create)
tests/unit/api/test_middleware.py (create)
tests/integration/api/test_auth_integration.py (create)
```

**Specification:**

**`src/caw/api/dependencies.py`:**

```python
"""FastAPI dependencies for authentication and common request context."""

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from caw.api.auth import validate_bearer_token

logger = logging.getLogger(__name__)

# The HTTPBearer scheme extracts the token from the Authorization header.
# auto_error=True means FastAPI returns 401 automatically if the header is missing.
_bearer_scheme = HTTPBearer(auto_error=True)


def _get_api_key() -> str:
    """Return the loaded API key from the application state.

    This function is overridden at startup in app.py to return
    the actual loaded key. Defined here as a placeholder so the
    dependency injection chain is complete.

    Raises:
        RuntimeError: If called before app startup has completed.
    """
    raise RuntimeError("API key not initialized. Server startup incomplete.")


def set_api_key_provider(key: str) -> None:
    """Set the API key provider function.

    Called once during app startup to inject the loaded key.

    Args:
        key: The loaded API key string.
    """
    global _get_api_key

    def provider() -> str:
        return key

    _get_api_key = provider


async def require_auth(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Security(_bearer_scheme),
    ],
) -> str:
    """FastAPI dependency that enforces bearer token authentication.

    Extract the token from the Authorization header, compare it
    against the stored API key using constant-time comparison.

    Returns:
        The validated token string (useful for logging/tracing).

    Raises:
        HTTPException: 401 if the token is missing or invalid.
    """
    expected = _get_api_key()
    if not validate_bearer_token(credentials.credentials, expected):
        logger.warning("Rejected invalid API key attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "error_code": "invalid_api_key", "message": "Invalid API key."},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
```

**Modification to `src/caw/api/app.py`:**

Add the `require_auth` dependency to the FastAPI app-level dependencies so it applies to ALL routes:

```python
from caw.api.dependencies import require_auth, set_api_key_provider
from caw.api.auth import load_or_create_api_key

# In the app factory or startup:
app = FastAPI(
    title="CAW API",
    version=__version__,
    dependencies=[Depends(require_auth)],  # <-- ADD THIS
)

# In the startup event or lifespan:
config_dir = Path("~/.config/caw").expanduser()  # Or from loaded config
api_key = load_or_create_api_key(config_dir)
set_api_key_provider(api_key)

# Print the key on first run (when newly generated) so the operator can copy it.
# The load_or_create_api_key function logs when a new key is created.
```

Add **one** unauthenticated health check endpoint:

```python
from fastapi import APIRouter

health_router = APIRouter(tags=["health"])

@health_router.get("/health", dependencies=[])  # Empty dependencies = no auth
async def health_check() -> dict[str, str]:
    """Unauthenticated health check. Returns server status only."""
    return {"status": "ok"}

# Register this router WITHOUT the app-level auth dependency:
# app.include_router(health_router) — but note: app-level dependencies
# apply to all routes. To exempt /health, use a sub-application or
# override dependencies at the route level:
@app.get("/health", dependencies=[], include_in_schema=True)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

**Important implementation detail:** FastAPI's `dependencies` parameter on the `FastAPI()` constructor applies to all routes. To exempt specific routes, pass `dependencies=[]` as a route-level override, which replaces (not extends) the app-level dependencies for that route.

**Acceptance criteria:**

1. `GET /api/v1/sessions` without `Authorization` header returns `401`.
2. `GET /api/v1/sessions` with `Authorization: Bearer WRONG_KEY` returns `401`.
3. `GET /api/v1/sessions` with `Authorization: Bearer CORRECT_KEY` returns `200` (or appropriate response).
4. `POST /api/v1/sessions` with valid key works normally.
5. `GET /health` returns `200` without any `Authorization` header.
6. The `401` response body contains `{"status": "error", "error_code": "invalid_api_key", ...}`.
7. The `401` response includes `WWW-Authenticate: Bearer` header.
8. Every existing route in the application returns `401` without a valid key (no route was missed).
9. `ruff check` and `mypy --strict` pass.

**Tests (`tests/unit/api/test_middleware.py`):**

- `test_require_auth_valid_token`: Mock `_get_api_key`, pass valid credentials, assert no exception.
- `test_require_auth_invalid_token`: Pass wrong credentials, assert `HTTPException` with status 401.
- `test_set_api_key_provider`: Call `set_api_key_provider("abc")`, then call `_get_api_key()`, assert returns `"abc"`.

**Tests (`tests/integration/api/test_auth_integration.py`):**

Use `httpx.AsyncClient` with `app` (via FastAPI's `TestClient` or `httpx` ASGITransport):

- `test_unauthenticated_request_returns_401`: `GET /api/v1/sessions` with no header.
- `test_wrong_key_returns_401`: `GET /api/v1/sessions` with wrong bearer token.
- `test_valid_key_returns_success`: `GET /api/v1/sessions` with correct bearer token.
- `test_health_no_auth_required`: `GET /health` with no header returns 200.
- `test_all_api_v1_routes_require_auth`: Enumerate all registered routes starting with `/api/v1/`, call each without auth, assert all return 401. This is the critical regression test — it catches any future route added without auth.

---

### S-WP03: WebSocket authentication

**Dependencies:** S-WP01, S-WP02, M7 (WebSocket handler must exist)
**Complexity:** S (< 100 lines)

**Files to modify:**

```
src/caw/api/websocket.py         (modify)
tests/unit/api/test_websocket_auth.py (create)
```

**Specification:**

WebSocket connections do not use the `Authorization` header in the same way as HTTP requests. The authentication token must be passed as a query parameter.

Modify the WebSocket endpoint at `/api/v1/sessions/{id}/stream`:

```python
from fastapi import WebSocket, WebSocketDisconnect, Query, status
from caw.api.auth import validate_bearer_token
from caw.api.dependencies import _get_api_key

@app.websocket("/api/v1/sessions/{session_id}/stream")
async def session_stream(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(..., alias="token"),
) -> None:
    """WebSocket endpoint for streaming session responses.

    Authentication: The client must pass the API key as a query parameter:
        ws://localhost:8420/api/v1/sessions/{id}/stream?token=YOUR_KEY

    If the token is missing or invalid, the connection is rejected
    with WebSocket close code 4401 (custom code for unauthorized).
    """
    expected = _get_api_key()
    if not validate_bearer_token(token, expected):
        await websocket.close(code=4401, reason="Invalid API key.")
        return

    await websocket.accept()
    # ... existing WebSocket handler logic ...
```

**Acceptance criteria:**

1. WebSocket connection to `/api/v1/sessions/{id}/stream` without `?token=` parameter is rejected with close code 4401.
2. WebSocket connection with `?token=WRONG_KEY` is rejected with close code 4401.
3. WebSocket connection with `?token=CORRECT_KEY` is accepted and functions normally.
4. `ruff check` and `mypy --strict` pass.

**Tests (`tests/unit/api/test_websocket_auth.py`):**

- `test_websocket_no_token_rejected`: Connect without token, assert connection closed with 4401.
- `test_websocket_wrong_token_rejected`: Connect with wrong token, assert closed with 4401.
- `test_websocket_valid_token_accepted`: Connect with valid token, assert connection accepted.

---

### S-WP04: Request rate limiting

**Dependencies:** S-WP02 (auth middleware must exist — rate limiting runs after auth)
**Complexity:** M (100–250 lines)

**Files to create:**

```
src/caw/api/rate_limit.py
tests/unit/api/test_rate_limit.py
```

**Files to modify:**

```
src/caw/core/config.py           (add rate limit fields to APIConfig)
config/default.toml               (add rate limit defaults)
config/example.toml               (add rate limit defaults with comments)
```

**Specification:**

**`src/caw/api/rate_limit.py`:**

```python
"""Request rate limiting for the CAW API.

Implements a sliding-window rate limiter using in-memory storage.
Two limits are enforced:
    1. Global limit: total requests per minute across all sessions.
    2. Per-session limit: requests per minute to a single session.

Rate limiting runs AFTER authentication — unauthenticated requests
are rejected by the auth middleware before reaching the rate limiter.
"""

import time
import logging
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


@dataclass
class RateLimiter:
    """Sliding-window rate limiter.

    Attributes:
        global_limit: Maximum requests per minute across all sessions.
        session_limit: Maximum requests per minute per session.
        window_seconds: Sliding window duration in seconds.
    """

    global_limit: int = 60
    session_limit: int = 20
    window_seconds: int = 60

    # Internal state: maps key -> list of request timestamps.
    _windows: dict[str, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def check(self, session_id: str | None = None) -> None:
        """Check rate limits and raise if exceeded.

        Checks the global limit first, then the per-session limit
        if a session_id is provided.

        Args:
            session_id: The session ID from the request path, if applicable.

        Raises:
            HTTPException: 429 Too Many Requests if either limit is exceeded.
        """
        now = time.monotonic()
        cutoff = now - self.window_seconds

        # Check global limit.
        self._prune("__global__", cutoff)
        if len(self._windows["__global__"]) >= self.global_limit:
            logger.warning("Global rate limit exceeded: %d/%d", self.global_limit, self.window_seconds)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "status": "error",
                    "error_code": "rate_limit_exceeded",
                    "message": f"Global rate limit exceeded ({self.global_limit} requests/{self.window_seconds}s).",
                },
                headers={"Retry-After": str(self.window_seconds)},
            )
        self._windows["__global__"].append(now)

        # Check per-session limit.
        if session_id is not None:
            key = f"session:{session_id}"
            self._prune(key, cutoff)
            if len(self._windows[key]) >= self.session_limit:
                logger.warning(
                    "Per-session rate limit exceeded for session %s: %d/%d",
                    session_id, self.session_limit, self.window_seconds,
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "status": "error",
                        "error_code": "rate_limit_exceeded",
                        "message": f"Session rate limit exceeded ({self.session_limit} requests/{self.window_seconds}s).",
                    },
                    headers={"Retry-After": str(self.window_seconds)},
                )
            self._windows[key].append(now)

    def _prune(self, key: str, cutoff: float) -> None:
        """Remove timestamps older than the cutoff from the window."""
        self._windows[key] = [
            t for t in self._windows[key] if t > cutoff
        ]
```

**Configuration additions to `APIConfig` in `src/caw/core/config.py`:**

```python
class APIConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8420
    cors_origins: list[str] = ["http://localhost:3000"]
    require_auth: bool = True                  # NEW
    rate_limit_global: int = 60                # NEW: requests per minute
    rate_limit_per_session: int = 20           # NEW: requests per minute per session
```

**Configuration additions to `config/default.toml` and `config/example.toml`:**

```toml
[api]
host = "127.0.0.1"
port = 8420
cors_origins = ["http://localhost:3000"]
require_auth = true                            # Require bearer token authentication
rate_limit_global = 60                         # Max requests per minute (all sessions)
rate_limit_per_session = 20                    # Max requests per minute (single session)
```

**Integration into `src/caw/api/app.py`:**

Create the `RateLimiter` instance from config values during startup. Add a FastAPI middleware or dependency that calls `rate_limiter.check()` on every authenticated request. Extract `session_id` from the URL path when available (routes containing `/sessions/{id}/`).

```python
# In startup / lifespan:
rate_limiter = RateLimiter(
    global_limit=config.api.rate_limit_global,
    session_limit=config.api.rate_limit_per_session,
)

# As a dependency, added after require_auth:
async def apply_rate_limit(request: Request) -> None:
    """Extract session_id from path if present and check rate limits."""
    session_id = request.path_params.get("id") or request.path_params.get("session_id")
    rate_limiter.check(session_id=session_id)
```

**Acceptance criteria:**

1. Sending `global_limit + 1` requests within `window_seconds` returns `429` on the last request.
2. Sending `session_limit + 1` requests to the same session within `window_seconds` returns `429`.
3. Sending `session_limit` requests each to two different sessions does NOT trigger the per-session limit.
4. After waiting `window_seconds`, requests succeed again.
5. The `429` response includes `Retry-After` header.
6. The `429` response body follows the standard error envelope (`status`, `error_code`, `message`).
7. `GET /health` is NOT rate-limited.
8. `ruff check` and `mypy --strict` pass.

**Tests (`tests/unit/api/test_rate_limit.py`):**

- `test_under_global_limit`: Check `global_limit - 1` times, no exception.
- `test_global_limit_exceeded`: Check `global_limit + 1` times, assert `HTTPException` 429.
- `test_under_session_limit`: Check `session_limit - 1` times with same session_id, no exception.
- `test_session_limit_exceeded`: Check `session_limit + 1` times with same session_id, assert 429.
- `test_different_sessions_independent`: Check `session_limit` times each for two different session IDs, no exception.
- `test_window_expiry`: Monkeypatch `time.monotonic`, check limit, advance time past window, check again — should succeed.
- `test_no_session_id_skips_session_check`: Call `check(session_id=None)`, only global limit applies.

---

### S-WP05: Bind-address safeguard

**Dependencies:** S-WP02 (auth config field `require_auth` must exist)
**Complexity:** S (< 50 lines)

**Files to modify:**

```
src/caw/api/app.py               (modify — add startup check)
tests/unit/api/test_bind_safeguard.py (create)
```

**Specification:**

During server startup, **before** binding the socket, add the following check:

```python
def validate_bind_safety(host: str, require_auth: bool) -> None:
    """Prevent binding to a non-loopback address without authentication.

    If the configured host is not a loopback address (127.0.0.1, ::1,
    or localhost) AND require_auth is False, refuse to start.

    Args:
        host: The configured bind address.
        require_auth: Whether authentication is enabled.

    Raises:
        ConfigError: If the configuration is unsafe.
    """
    loopback = {"127.0.0.1", "::1", "localhost"}
    if host not in loopback and not require_auth:
        raise ConfigError(
            message=(
                f"Refusing to bind to non-loopback address '{host}' with authentication disabled. "
                f"Set api.require_auth = true in your configuration, or bind to 127.0.0.1."
            ),
            code="unsafe_bind_configuration",
            details={"host": host, "require_auth": require_auth},
        )

    if host not in loopback:
        logger.warning(
            "API server binding to non-loopback address '%s'. "
            "Ensure this is intentional and that the network is trusted.",
            host,
        )
```

Call `validate_bind_safety(config.api.host, config.api.require_auth)` during app startup, before `uvicorn.run()`.

**Acceptance criteria:**

1. `host="0.0.0.0"` + `require_auth=False` raises `ConfigError` with code `"unsafe_bind_configuration"`.
2. `host="0.0.0.0"` + `require_auth=True` succeeds (with a warning log).
3. `host="127.0.0.1"` + `require_auth=False` succeeds (loopback is acceptable without auth for local dev).
4. `host="127.0.0.1"` + `require_auth=True` succeeds.
5. `host="::1"` + `require_auth=False` succeeds (IPv6 loopback).
6. `ruff check` and `mypy --strict` pass.

**Tests (`tests/unit/api/test_bind_safeguard.py`):**

- `test_non_loopback_no_auth_raises`: `validate_bind_safety("0.0.0.0", False)` raises `ConfigError`.
- `test_non_loopback_with_auth_ok`: `validate_bind_safety("0.0.0.0", True)` does not raise.
- `test_loopback_no_auth_ok`: `validate_bind_safety("127.0.0.1", False)` does not raise.
- `test_loopback_ipv6_no_auth_ok`: `validate_bind_safety("::1", False)` does not raise.
- `test_localhost_no_auth_ok`: `validate_bind_safety("localhost", False)` does not raise.
- `test_arbitrary_ip_no_auth_raises`: `validate_bind_safety("192.168.1.100", False)` raises `ConfigError`.

---

### S-WP06: API key rotation

**Dependencies:** S-WP01
**Complexity:** S (< 80 lines)

**Files to modify:**

```
src/caw/api/auth.py               (add rotate function)
src/caw/cli/main.py               (add CLI command)
tests/unit/api/test_auth.py       (add rotation tests)
```

**Specification:**

Add to `src/caw/api/auth.py`:

```python
def rotate_api_key(config_dir: Path) -> str:
    """Generate a new API key and replace the existing one.

    Process:
    1. Generate a new key.
    2. Read the current key file (if it exists) as backup context.
    3. Write the new key to the key file (atomic write via temp file + rename).
    4. Log that rotation occurred.
    5. Return the new key.

    The server must be restarted after rotation for the new key to take effect.

    Args:
        config_dir: The CAW configuration directory.

    Returns:
        The newly generated API key string.
    """
    key_path = get_key_path(config_dir)
    new_key = generate_api_key()

    # Atomic write: write to temp file, then rename.
    # This prevents a partial write from corrupting the key file.
    tmp_path = key_path.with_suffix(".tmp")
    tmp_path.write_text(new_key + "\n")
    tmp_path.chmod(0o600)
    tmp_path.rename(key_path)

    logger.info("API key rotated. Stored at: %s", key_path)
    return new_key
```

Add a CLI command in `src/caw/cli/main.py`:

```python
@cli.command()
def rotate_key() -> None:
    """Generate a new API key and replace the existing one.

    The server must be restarted after rotation for the new key to take effect.
    Prints the new key to stdout.
    """
    config_dir = Path("~/.config/caw").expanduser()
    new_key = rotate_api_key(config_dir)
    click.echo(f"New API key: {new_key}")
    click.echo("Restart the server for the new key to take effect.")
```

**Acceptance criteria:**

1. `rotate_api_key()` returns a new 64-character hex key different from the old one.
2. The key file on disk contains the new key after rotation.
3. The old key is no longer present in the key file.
4. The write is atomic (uses temp file + rename).
5. `caw rotate-key` prints the new key and a restart reminder.
6. `ruff check` and `mypy --strict` pass.

**Tests (additions to `tests/unit/api/test_auth.py`):**

- `test_rotate_creates_new_key`: Create an initial key, rotate, assert new key differs.
- `test_rotate_persists_new_key`: Rotate, then `load_or_create_api_key`, assert returns the rotated key.
- `test_rotate_atomic_write`: Assert temp file does not persist after rotation.
- `test_rotate_file_permissions`: Assert key file mode is `0o600` after rotation.

---

### S-WP07: Configuration integration and documentation

**Dependencies:** S-WP01 through S-WP06
**Complexity:** S (< 100 lines of code + documentation)

**Files to modify:**

```
config/default.toml               (verify all new fields present)
config/example.toml               (verify all new fields present with comments)
docs/security.md                  (create)
CHANGELOG.md                      (update)
```

**Specification:**

**`docs/security.md`:**

Create a security documentation file covering:

1. **Authentication**: How the API key is generated, where it is stored, how to use it in requests (`Authorization: Bearer YOUR_KEY`), how to use it with WebSocket (`?token=YOUR_KEY`).
2. **Key rotation**: How to rotate the key (`caw rotate-key`), that the server must be restarted after rotation.
3. **Rate limiting**: Default limits, how to configure them, what the `429` response looks like.
4. **Bind-address safety**: What the safeguard does, why `0.0.0.0` requires `require_auth = true`.
5. **Provider API key handling**: Confirmation that provider keys are read from env vars, never stored in config files, never exposed to API clients.
6. **Recommendations**: Keep the server on `127.0.0.1`. If network exposure is needed, use a reverse proxy with TLS. Never commit the key file. Never disable auth on a non-loopback address.

**`CHANGELOG.md`:**

Add an entry under `[Unreleased]`:

```markdown
### Added
- API bearer token authentication on all endpoints (S-WP01, S-WP02).
- WebSocket query parameter authentication (S-WP03).
- Sliding-window rate limiting — global and per-session (S-WP04).
- Bind-address safeguard preventing unauthenticated non-loopback binding (S-WP05).
- API key rotation via `caw rotate-key` CLI command (S-WP06).
- Security documentation at `docs/security.md` (S-WP07).

### Security
- **BREAKING**: All `/api/v1/*` endpoints now require `Authorization: Bearer <key>` header.
- **BREAKING**: WebSocket endpoint now requires `?token=<key>` query parameter.
```

**Acceptance criteria:**

1. `config/default.toml` contains `require_auth`, `rate_limit_global`, `rate_limit_per_session` fields.
2. `config/example.toml` contains the same fields with explanatory comments.
3. `docs/security.md` exists and covers all six sections listed above.
4. `CHANGELOG.md` has a `### Security` subsection documenting the breaking changes.
5. `ruff check` and `mypy --strict` pass on all modified Python files.

**Tests:** None (documentation only).

---

## 3. Dependency Summary

```
S-WP01  API key generation           ← M1-WP02 (config system)
S-WP02  HTTP auth middleware          ← S-WP01, M7 (API routes)
S-WP03  WebSocket auth                ← S-WP01, S-WP02, M7
S-WP04  Rate limiting                 ← S-WP02
S-WP05  Bind-address safeguard        ← S-WP02
S-WP06  Key rotation                  ← S-WP01
S-WP07  Config + docs                 ← S-WP01 through S-WP06
```

Parallelizable: S-WP03, S-WP04, S-WP05, and S-WP06 can all proceed in parallel once S-WP02 is complete.

---

## 4. What This Roadmap Does Not Cover

The following are real security concerns that are **out of scope** for this immediate hardening pass, but should be addressed in future milestones:

- **TLS/HTTPS**: The API serves plaintext HTTP. For any non-localhost deployment, a reverse proxy (nginx, caddy) with TLS termination is required. This is an operational concern, not a code concern.
- **Multi-user authentication**: User accounts, roles, and access control. Deferred per Design Document §21.
- **Audit logging of auth events**: Auth failures are logged at WARNING level, but a dedicated security audit log is not yet implemented.
- **Token scoping**: The single API key grants full access to all endpoints. Fine-grained scopes (read-only, execute-only) are a future enhancement.
- **Automatic key rotation**: The current scheme requires manual rotation + restart. An automated rotation mechanism is a future enhancement.
- **Request body size limits**: FastAPI has configurable limits, but they are not explicitly set in the current spec. Should be addressed in a general hardening pass.
