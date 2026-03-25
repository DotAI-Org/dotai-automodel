"""SQLAlchemy async engine and session factory setup."""
import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/churn",
)

# Render provides postgres:// but asyncpg requires postgresql+asyncpg://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """Yield a database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Create tables and add any missing columns from model definitions."""
    from app.db.models import Base
    from sqlalchemy import inspect as sa_inspect, text

    async with engine.begin() as conn:
        # Drop stale tables from a previous app (e.g. JACPL) that conflict
        # with our schema. Detected by checking if users.id is not UUID.
        def _drop_stale_tables(sync_conn):
            inspector = sa_inspect(sync_conn)
            if not inspector.has_table("users"):
                return
            cols = {c["name"]: c for c in inspector.get_columns("users")}
            id_col = cols.get("id")
            if id_col and str(id_col["type"]) != "UUID":
                sync_conn.execute(text("DROP SCHEMA public CASCADE"))
                sync_conn.execute(text("CREATE SCHEMA public"))

        await conn.run_sync(_drop_stale_tables)
        await conn.run_sync(Base.metadata.create_all)

        # Add missing columns to existing tables
        def _migrate_columns(sync_conn):
            inspector = sa_inspect(sync_conn)
            for table_name, table in Base.metadata.tables.items():
                if not inspector.has_table(table_name):
                    continue
                existing = {c["name"] for c in inspector.get_columns(table_name)}
                for col in table.columns:
                    if col.name not in existing:
                        col_type = col.type.compile(sync_conn.dialect)
                        sync_conn.execute(
                            text(f'ALTER TABLE "{table_name}" ADD COLUMN "{col.name}" {col_type}')
                        )

        await conn.run_sync(_migrate_columns)
