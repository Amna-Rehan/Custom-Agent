from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class Source(BaseModel):
    """Source URL for an organization, optionally tied to a specific fact/field."""

    __tablename__ = "sources"

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id"),
        index=True,
    )

    url: Mapped[str] = mapped_column(
        String(700),
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        default="official",
    )

    field_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    organization = relationship(
        "Organization",
        back_populates="sources",
    )
