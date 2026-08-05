from pathlib import Path
import os
from sqlalchemy import create_engine, text


def load_database_url() -> str | None:
    env_path = Path(__file__).with_name(".env")
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "DATABASE_URL":
                return value.strip().strip("\"'")
    return os.getenv("DATABASE_URL")


DATABASE_URL = load_database_url()
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL was not found in .env or environment variables.")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
