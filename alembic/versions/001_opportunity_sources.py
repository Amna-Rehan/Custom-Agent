from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = "001_opportunity_sources"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        text(
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
            """
        )
    )

    op.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS opportunities (
                id UUID PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                organization_id UUID NOT NULL REFERENCES organizations(id),
                application_url VARCHAR(700),
                application_deadline VARCHAR(255),
                eligibility TEXT,
                funding_amount VARCHAR(255),
                funding_currency VARCHAR(50),
                equity_required VARCHAR(255),
                program_duration VARCHAR(255),
                benefits JSON,
                application_process TEXT,
                startup_stage VARCHAR(255),
                investment_stage VARCHAR(255),
                geographic_focus VARCHAR(500),
                sector_focus VARCHAR(500),
                program_status VARCHAR(100),
                mentorship TEXT,
                investor_access TEXT,
                network_access TEXT,
                office_space TEXT,
                grants TEXT,
                credits TEXT,
                cohort_information TEXT,
                required_documents TEXT,
                selection_process TEXT
            );
            """
        )
    )

    op.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_opportunities_organization_id "
            "ON opportunities (organization_id);"
        )
    )

    op.execute(
        text(
            "ALTER TABLE sources "
            "ADD COLUMN IF NOT EXISTS field_name VARCHAR(100);"
        )
    )
    op.execute(
        text("ALTER TABLE sources ADD COLUMN IF NOT EXISTS value TEXT;")
    )
    op.execute(
        text(
            "ALTER TABLE sources "
            "ADD COLUMN IF NOT EXISTS verified BOOLEAN NOT NULL DEFAULT false;"
        )
    )


def downgrade() -> None:
    op.execute(text("ALTER TABLE sources DROP COLUMN IF EXISTS verified;"))
    op.execute(text("ALTER TABLE sources DROP COLUMN IF EXISTS value;"))
    op.execute(text("ALTER TABLE sources DROP COLUMN IF EXISTS field_name;"))
    op.execute(text("DROP TABLE IF EXISTS opportunities;"))
