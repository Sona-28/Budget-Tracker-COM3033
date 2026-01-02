import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.transaction_service.database.connection import Base
from services.transaction_service.models.transaction import Transaction

# Load env vars
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


config = context.config

# Set DB URL strictly from env
DATABASE_URL = os.getenv("TRANSACTIONS_DATABASE_URI")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))


# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
