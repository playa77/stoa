"""Command-line interface for serving and operating CAW locally."""

from __future__ import annotations

import asyncio

import click
import uvicorn
from rich.console import Console

from caw.__version__ import __version__
from caw.api.app import create_app
from caw.api.deps import redact_config_for_display
from caw.core.config import load_config
from caw.core.engine import Engine, ExecutionRequest
from caw.core.permissions import PermissionGate
from caw.core.router import Router
from caw.core.session import SessionManager
from caw.models import SessionMode
from caw.protocols.registry import ProviderRegistry
from caw.skills.registry import SkillRegistry
from caw.storage.database import Database
from caw.storage.repository import MessageRepository, SessionRepository, TraceEventRepository
from caw.traces.collector import TraceCollector

console = Console()


@click.group()
def cli() -> None:
    """Canonical Agent Workbench CLI entrypoint."""


@cli.command("version")
def version_command() -> None:
    """Print CLI and package version."""
    click.echo(__version__)


@cli.group("config")
def config_group() -> None:
    """Configuration display and management commands."""


@config_group.command("show")
def config_show() -> None:
    """Show current merged config with secret-like values redacted."""
    config = load_config()
    redacted = redact_config_for_display(config)
    console.print_json(data=redacted)


@cli.group("db")
def db_group() -> None:
    """Database lifecycle commands."""


@db_group.command("init")
def db_init() -> None:
    """Initialize configured SQLite database and run migrations."""

    async def _run() -> None:
        config = load_config()
        database = Database(config.storage)
        await database.connect()
        try:
            await database.run_migrations()
        finally:
            await database.close()

    asyncio.run(_run())
    click.echo("Database initialized")


@db_group.command("migrate")
def db_migrate() -> None:
    """Run pending migrations on the configured database."""

    async def _run() -> None:
        config = load_config()
        database = Database(config.storage)
        await database.connect()
        try:
            await database.run_migrations()
        finally:
            await database.close()

    asyncio.run(_run())
    click.echo("Migrations complete")


@cli.command("serve")
@click.option("--host", default=None, type=str)
@click.option("--port", default=None, type=int)
def serve(host: str | None, port: int | None) -> None:
    """Start the CAW FastAPI server with uvicorn."""
    config = load_config()
    app = create_app(config)
    uvicorn.run(app, host=host or config.api.host, port=port or config.api.port)


@cli.command("chat")
def chat() -> None:
    """Run a basic interactive terminal chat loop."""

    async def _chat() -> None:
        config = load_config()
        database = Database(config.storage)
        await database.connect()
        await database.run_migrations()

        trace_repo = TraceEventRepository(database)
        collector = TraceCollector(trace_repo, flush_threshold=1)
        await collector.start()

        try:
            provider_registry = ProviderRegistry(config)
            skill_registry = SkillRegistry(config.skills)
            skill_registry.load()

            session_manager = SessionManager(
                SessionRepository(database), MessageRepository(database)
            )
            engine = Engine(
                config=config,
                session_manager=session_manager,
                router=Router(config, provider_registry),
                permission_gate=PermissionGate(config.workspace, collector),
                skill_registry=skill_registry,
                trace_collector=collector,
                provider_registry=provider_registry,
                message_repo=MessageRepository(database),
            )

            session = await session_manager.create(mode=SessionMode.CHAT)
            while True:
                try:
                    content = click.prompt("You", prompt_suffix="> ")
                except (EOFError, KeyboardInterrupt):
                    click.echo()
                    break

                if content.strip().lower() == "exit":
                    break

                result = await engine.execute(
                    ExecutionRequest(session_id=session.id, content=content)
                )
                click.echo(f"Assistant> {result.content}")
        finally:
            await collector.stop()
            await database.close()

    asyncio.run(_chat())
