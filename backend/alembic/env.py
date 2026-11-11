from logging.config import fileConfig

import os
import sys

from dotenv import load_dotenv

from sqlalchemy import create_engine, pool

from alembic import context


# =====================================================
# PROJECT PATH
# =====================================================

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()


# =====================================================
# DATABASE / SQLALCHEMY
# =====================================================

from app.database import Base


# =====================================================
# IMPORT ALL MODELS
# =====================================================
#
# IMPORTANT:
# Explicitly importing RolePermission makes sure
# Alembic sees the new role_permissions table.
#
# =====================================================

from app.models.user import User
from app.models.role_permission import RolePermission


# =====================================================
# ALEMBIC CONFIGURATION
# =====================================================

config = context.config


# =====================================================
# DATABASE URL
# =====================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


if not DATABASE_URL:

    raise RuntimeError(
        "DATABASE_URL is not configured in the environment."
    )


# =====================================================
# OVERRIDE alembic.ini DATABASE URL
# =====================================================

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL
)


# =====================================================
# LOGGING
# =====================================================

if config.config_file_name is not None:

    fileConfig(
        config.config_file_name
    )


# =====================================================
# TARGET METADATA
# =====================================================

target_metadata = Base.metadata


# =====================================================
# OFFLINE MIGRATIONS
# =====================================================

def run_migrations_offline():

    context.configure(

        url=DATABASE_URL,

        target_metadata=target_metadata,

        literal_binds=True,

        compare_type=True,

        compare_server_default=True,
    )

    with context.begin_transaction():

        context.run_migrations()


# =====================================================
# ONLINE MIGRATIONS
# =====================================================

def run_migrations_online():

    connectable = create_engine(

        DATABASE_URL,

        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(

            connection=connection,

            target_metadata=target_metadata,

            compare_type=True,

            compare_server_default=True,
        )

        with context.begin_transaction():

            context.run_migrations()


# =====================================================
# RUN MIGRATIONS
# =====================================================

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()