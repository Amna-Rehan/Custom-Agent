from app.database import Base, engine

from app.models import (
    User,
    Organization,
    Source,
    ResearchJob,
)


def init_database():
    Base.metadata.create_all(bind=engine)