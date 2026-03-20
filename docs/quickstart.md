# Quickstart (Backend + GUI Integration)

## 1. Install

```bash
uv sync --all-extras
```

## 2. Configure

```bash
cp config/example.toml config/local.toml
```

Set provider key env vars referenced by `api_key_env` in your config (for example `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).

## 3. Start server

```bash
uv run python -m caw.cli.main serve --host 127.0.0.1 --port 8420
```

- Swagger UI: `http://127.0.0.1:8420/docs`
- OpenAPI: `http://127.0.0.1:8420/openapi.json`

## 4. Minimal API smoke flow

### 4.1 Health

```bash
curl http://127.0.0.1:8420/api/v1/health
```

### 4.2 Create session

```bash
curl -X POST http://127.0.0.1:8420/api/v1/sessions \
  -H 'content-type: application/json' \
  -d '{"mode":"chat"}'
```

### 4.3 Send message

```bash
curl -X POST http://127.0.0.1:8420/api/v1/sessions/<SESSION_ID>/messages \
  -H 'content-type: application/json' \
  -d '{"content":"Hello"}'
```

### 4.4 Read trace

```bash
curl http://127.0.0.1:8420/api/v1/traces/<TRACE_ID>/summary
```

## 5. GUI local-dev recommendations

- Keep backend and GUI on localhost during development.
- Configure frontend base URL as `http://127.0.0.1:8420`.
- Build a shared API client that always unwraps CAW response envelopes.
- Add global error handling for non-200 and `status=error` responses.

## 6. Verification commands

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```
