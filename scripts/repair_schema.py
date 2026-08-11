"""Idempotent schema repair for opportunity expansion."""

from sqlalchemy import text

from app.database.session import engine


STATEMENTS = [
    # Enum labels — SQLAlchemy may emit names (PROGRAM) or values (program)
    """
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'organizationtype') THEN
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


def main() -> None:
    with engine.begin() as conn:
        for statement in STATEMENTS:
            conn.execute(text(statement))
        print("Schema repair complete")


if __name__ == "__main__":
    main()
