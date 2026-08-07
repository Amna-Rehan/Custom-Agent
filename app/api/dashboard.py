from collections import Counter

from fastapi import APIRouter

from app.database.session import SessionLocal
from app.models.organization import Organization


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def get_dashboard_stats():

    db = SessionLocal()

    try:

        organizations = db.query(Organization).all()

        total = len(organizations)

        type_counts = Counter()
        country_counts = Counter()
        city_counts = Counter()

        for org in organizations:

            if org.organization_type:

                organization_type = (
                    org.organization_type.value
                    if hasattr(org.organization_type, "value")
                    else str(org.organization_type)
                )

                type_counts[organization_type] += 1

            if org.country:
                country_counts[org.country] += 1

            if org.city:
                city_counts[org.city] += 1

        return {
            "total_organizations": total,

            "organization_types": dict(type_counts),

            "countries": dict(country_counts),

            "cities": dict(city_counts),

        }

    finally:

        db.close()