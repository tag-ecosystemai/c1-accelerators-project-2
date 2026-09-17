"""Alembic configuration for the TalentMatch database."""

from alembic import context
from sqlalchemy import create_engine

from backend.app.database import Base, engine as app_engine
from backend.app.models.job import Job
from backend.app.models.job_profile import JobProfile
from backend.app.models.session import Session
from backend.app.models.user import User


target_metadata = Base.metadata


def get_database_url() -> str:
    """Use an Alembic-configured URL when provided, otherwise app settings."""

    configured_url = context.config.get_main_option(
        "sqlalchemy.url"
    )

    if configured_url:
        return configured_url

    return app_engine.url.render_as_string(
        hide_password=False
    )


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using the configured database connection."""

    configured_url = context.config.get_main_option(
        "sqlalchemy.url"
    )

    if configured_url:
        migration_engine = create_engine(configured_url)
    else:
        migration_engine = app_engine

    try:
        with migration_engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        if configured_url:
            migration_engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()