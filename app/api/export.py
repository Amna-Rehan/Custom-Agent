import csv
import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models.organization import Organization


router = APIRouter(
    prefix="/export",
    tags=["Export"],
)

CSV_HEADERS = [
    "id",
    "name",
    "organization_type",
    "website",
    "country",
    "city",
    "industry",
    "description",
    "email",
    "phone",
    "linkedin",
    "verification_score",
    "verification_status",
    "verification_source",
    "application_url",
    "application_deadline",
    "eligibility",
    "funding_amount",
    "funding_currency",
    "equity_required",
    "program_duration",
    "benefits",
    "application_process",
]


@router.get("/csv")
def export_csv():
    db = SessionLocal()

    try:
        organizations = (
            db.query(Organization)
            .options(joinedload(Organization.opportunities))
            .order_by(Organization.name)
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(CSV_HEADERS)

        for organization in organizations:
            opportunity = (
                organization.opportunities[0]
                if organization.opportunities
                else None
            )

            benefits = ""
            if opportunity and opportunity.benefits:
                if isinstance(opportunity.benefits, list):
                    benefits = "; ".join(
                        str(item) for item in opportunity.benefits
                    )
                else:
                    benefits = str(opportunity.benefits)

            writer.writerow(
                [
                    organization.id,
                    organization.name,
                    (
                        organization.organization_type.value
                        if organization.organization_type
                        else ""
                    ),
                    organization.website or "",
                    organization.country or "",
                    organization.city or "",
                    organization.industry or "",
                    organization.description or "",
                    organization.email or "",
                    organization.phone or "",
                    organization.linkedin or "",
                    organization.verification_score or 0,
                    organization.verification_status or "",
                    organization.verification_source or "",
                    (opportunity.application_url if opportunity else "") or "",
                    (
                        opportunity.application_deadline if opportunity else ""
                    )
                    or "",
                    (opportunity.eligibility if opportunity else "") or "",
                    (opportunity.funding_amount if opportunity else "") or "",
                    (opportunity.funding_currency if opportunity else "") or "",
                    (opportunity.equity_required if opportunity else "") or "",
                    (opportunity.program_duration if opportunity else "") or "",
                    benefits,
                    (
                        opportunity.application_process if opportunity else ""
                    )
                    or "",
                ]
            )

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    "attachment; filename=organizations.csv"
                )
            },
        )

    finally:
        db.close()
