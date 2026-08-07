from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel
from app.models.enums import OrganizationType


class Organization(BaseModel):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    organization_type: Mapped[OrganizationType] = mapped_column(
        Enum(OrganizationType),
        index=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    linkedin: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    verification_score: Mapped[int] = mapped_column(
        default=0,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
    )

    verification_source: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )