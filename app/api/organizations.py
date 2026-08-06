from typing import Optional

from fastapi import APIRouter
from numpy import sort
from sqlalchemy import and_,desc

from app.database.session import SessionLocal
from app.models.organization import Organization
from app.models.enums import OrganizationType

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get("/")
def get_organizations(
    country: Optional[str] = None,
    city: Optional[str] = None,
    organization_type: Optional[str] = None,
    industry: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    sort: str = "verification_score",
):

    db = SessionLocal()

    try:

        query = db.query(Organization)

        filters = []

        if country:
            filters.append(Organization.country.ilike(f"%{country}%"))

        if city:
            filters.append(Organization.city.ilike(f"%{city}%"))

        if industry:
            filters.append(Organization.industry.ilike(f"%{industry}%"))

        if organization_type:

            org_type = organization_type.lower()

            if org_type in [e.value for e in OrganizationType]:
                filters.append(
                    Organization.organization_type == OrganizationType(org_type)
                )

        if filters:
            query = query.filter(and_(*filters))

        # Sorting
        if sort == "name":
          query = query.order_by(Organization.name)

        elif sort == "city":
          query = query.order_by(Organization.city)

        elif sort == "country":
          query = query.order_by(Organization.country)

        elif sort == "organization_type":
          query = query.order_by(Organization.organization_type)

        elif sort == "verification_score":
          query = query.order_by(desc(Organization.verification_score))

        elif sort == "created_at":
          query = query.order_by(desc(Organization.created_at))

        else:
          query = query.order_by(desc(Organization.verification_score))
        # Pagination
        organizations = (
            query.offset((page - 1) * limit)
            .limit(limit)
            .all()
        )


        return [
            {
                "id": str(org.id),
                "name": org.name,
                "organization_type": org.organization_type.value,
                "country": org.country,
                "city": org.city,
                "website": org.website,
                "industry": org.industry,
                "description": org.description,
                "email": org.email,
                "phone": org.phone,
                "linkedin": org.linkedin,
                "verification_score": org.verification_score,
            }
            for org in organizations
        ]

    finally:
        db.close()