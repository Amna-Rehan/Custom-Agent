from fastapi import APIRouter, Query
from sqlalchemy import asc, desc

from app.database.session import SessionLocal
from app.models.organization import Organization


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get("/")
def get_organizations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),

    country: str | None = None,
    city: str | None = None,
    organization_type: str | None = None,
    industry: str | None = None,
    verification_status: str | None = None,
    search: str | None = None,

    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
):

    db = SessionLocal()

    try:

        query = db.query(Organization)

        if country:
            query = query.filter(
                Organization.country.ilike(f"%{country}%")
            )

        if city:
            query = query.filter(
                Organization.city.ilike(f"%{city}%")
            )

        if organization_type:
            query = query.filter(
                Organization.organization_type == organization_type.lower()
            )

        if industry:
            query = query.filter(
                Organization.industry.ilike(f"%{industry}%")
            )

        if verification_status:
            query = query.filter(
                Organization.verification_status.ilike(
                    f"%{verification_status}%"
                )
            )

        if search:
            search_term = f"%{search}%"

            query = query.filter(
                Organization.name.ilike(search_term)
                | Organization.website.ilike(search_term)
                | Organization.description.ilike(search_term)
                | Organization.industry.ilike(search_term)
                | Organization.city.ilike(search_term)
                | Organization.country.ilike(search_term)
            )

        
        allowed_sort_fields = {
            "name": Organization.name,
            "country": Organization.country,
            "city": Organization.city,
            "organization_type": Organization.organization_type,
            "verification_score": Organization.verification_score,
        }

        sort_column = allowed_sort_fields.get(
            sort_by,
            Organization.name
        )

        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        total = query.count()

        offset = (page - 1) * page_size

        organizations = (
            query
            .offset(offset)
            .limit(page_size)
            .all()
        )

        results = []

        for org in organizations:

            results.append({

                "id": str(org.id),

                "name": org.name,

                "organization_type": (
                    org.organization_type.value
                    if org.organization_type
                    else None
                ),

                "country": org.country,

                "city": org.city,

                "website": org.website,

                "industry": org.industry,

                "description": org.description,

                "email": org.email,

                "phone": org.phone,

                "linkedin": org.linkedin,

                "verification_score": org.verification_score,

                "verification_status": org.verification_status,

                "verification_source": org.verification_source,

            })

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (
                (total + page_size - 1) // page_size
            ),
            "results": results,
        }

    finally:

        db.close()