from sqlalchemy import text

from app.database.session import engine


def main() -> None:
    with engine.connect() as conn:
        cols = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='sources' ORDER BY ordinal_position"
            )
        ).fetchall()
        print("sources columns:", [row[0] for row in cols])

        enums = conn.execute(
            text(
                "SELECT e.enumlabel FROM pg_type t "
                "JOIN pg_enum e ON t.oid = e.enumtypid "
                "WHERE t.typname = 'organizationtype' "
                "ORDER BY e.enumsortorder"
            )
        ).fetchall()
        print("enum values:", [row[0] for row in enums])

        tables = conn.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            )
        ).fetchall()
        print("tables:", [row[0] for row in tables])


if __name__ == "__main__":
    main()
