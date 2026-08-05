from sqlalchemy import ForeignKey, String

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


class Source(BaseModel):
    __tablename__ = "sources"

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id")
    )

    url: Mapped[str] = mapped_column(
        String(700)
    )

    source_type: Mapped[str] = mapped_column(
        String(100)
    )