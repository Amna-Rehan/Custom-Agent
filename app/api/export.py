import csv
import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.database import SessionLocal
from app.models.organization import Organization


router = APIRouter(
    prefix="/export",
    tags=["Export"],
)


@router.get("/csv")
def export_csv():

    db = SessionLocal()

    try:
        organizations = (
            db.query(Organization)
            .order_by(Organization.name)
            .all()
        )

        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow([
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
        ])

        for organization in organizations:

            writer.writerow([
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
            ])

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