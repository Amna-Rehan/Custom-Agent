from uuid import UUID

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class Opportunity(BaseModel):
    """Program / funding opportunity linked to an organization."""

    __tablename__ = "opportunities"

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id"),
        index=True,
    )

    application_url: Mapped[str | None] = mapped_column(
        String(700),
        nullable=True,
    )

    application_deadline: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    eligibility: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    funding_amount: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    funding_currency: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    equity_required: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    program_duration: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    benefits: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    application_process: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    startup_stage: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    investment_stage: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    geographic_focus: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    sector_focus: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    program_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    mentorship: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    investor_access: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    network_access: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    office_space: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    grants: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    credits: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cohort_information: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    required_documents: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    selection_process: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    organization = relationship(
        "Organization",
        back_populates="opportunities",
    )
