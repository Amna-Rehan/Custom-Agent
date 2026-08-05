from app.database.base import Base
from app.database import engine

from app.models.investors import Investor

Base.metadata.create_all(bind=engine)

print("Tables created")