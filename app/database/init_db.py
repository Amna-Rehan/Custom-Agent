from sqlalchemy import text

from app.database import Base, engine
from app.models import (
    Opportunity,
    Organization,
    ResearchJob,
    Source,
    User,
)


def ensure_schema_upgrades() -> None:
    """Idempotent fixes for databases created before opportunity expansion."""

    statements = [
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'organizationtype'
            ) THEN
                BEGIN
                    ALTER TYPE organizationtype ADD VALUE IF NOT EXISTS 'grant';
                EXCEPTION WHEN duplicate_object THEN NULL;
                END;
                BEGIN
                    ALTER TYPE organizationtype ADD VALUE IF NOT EXISTS 'program';
                EXCEPTION WHEN duplicate_object THEN NULL;
                END;
                BEGIN
                    ALTER TYPE organizationtype ADD VALUE IF NOT EXISTS 'GRANT';
                EXCEPTION WHEN duplicate_object THEN NULL;
                END;
                BEGIN
                    ALTER TYPE organizationtype ADD VALUE IF NOT EXISTS 'PROGRAM';
                EXCEPTION WHEN duplicate_object THEN NULL;
                END;
            END IF;
        END
        $$;
        """,
        """
        ALTER TABLE sources
        ADD COLUMN IF NOT EXISTS field_name VARCHAR(100);
        """,
        """
        ALTER TABLE sources
        ADD COLUMN IF NOT EXISTS value TEXT;
        """,
        """
        ALTER TABLE sources
        ADD COLUMN IF NOT EXISTS verified BOOLEAN NOT NULL DEFAULT false;
        """,
    ]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def init_database():
    Base.metadata.create_all(bind=engine)
    ensure_schema_upgrades()
