# Quickstart

## 1. Install dependencies

```bash
uv sync --all-extras
```

## 2. Configure runtime

Copy example config and edit provider credentials and workspace paths:

```bash
cp config/example.toml config/local.toml
```

Then set the provider API key environment variable referenced by `api_key_env`.

## 3. Initialize and run API

```bash
uv run python -m caw.cli.main serve --host 127.0.0.1 --port 8420
```

The API starts with automatic migration execution and serves endpoints under `/api/v1/*`.

## 4. Create a session

```bash
curl -X POST http://127.0.0.1:8420/api/v1/sessions \
  -H 'content-type: application/json' \
  -d '{"mode":"chat"}'
```

## 5. Run a capability flow

Example research ingestion request:

```bash
curl -X POST http://127.0.0.1:8420/api/v1/research/ingest \
  -H 'content-type: application/json' \
  -d '{"session_id":"<session-id>","path":"tests/fixtures/research/sample.txt"}'
```

## 6. Development workflow

- Run tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Format check: `uv run ruff format --check .`
- Type-check: `uv run mypy src`
