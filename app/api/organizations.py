from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import joinedload

from app.database.session import SessionLocal
from app.models.organization import Organization


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


def _serialize_organization(org: Organization) -> dict:
    opportunity = None
    if getattr(org, "opportunities", None):
        opp = org.opportunities[0] if org.opportunities else None
        if opp:
            opportunity = {
                "application_url": opp.application_url,
                "application_deadline": opp.application_deadline,
                "eligibility": opp.eligibility,
                "funding_amount": opp.funding_amount,
                "funding_currency": opp.funding_currency,
                "equity_required": opp.equity_required,
                "program_duration": opp.program_duration,
                "benefits": opp.benefits or [],
                "application_process": opp.application_process,
                "startup_stage": opp.startup_stage,
                "investment_stage": opp.investment_stage,
                "geographic_focus": opp.geographic_focus,
                "sector_focus": opp.sector_focus,
                "program_status": opp.program_status,
            }

    sources = []
    for source in getattr(org, "sources", []) or []:
        sources.append(
            {
                "field": source.field_name,
                "value": source.value,
                "source_url": source.url,
                "source_type": source.source_type,
                "verified": source.verified,
            }
        )

    return {
        "id": str(org.id),
        "name": org.name,
        "organization_type": (
            org.organization_type.value if org.organization_type else None
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
        "opportunity": opportunity,
        "sources": sources,
    }


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
                Organization.country.ilike(f"%{country.strip()}%")
            )

        if city:
            query = query.filter(
                Organization.city.ilike(f"%{city.strip()}%")
            )

        if organization_type:
            query = query.filter(
                func.lower(Organization.organization_type)
                == organization_type.lower().strip()
            )

        if industry:
            query = query.filter(
                Organization.industry.ilike(f"%{industry.strip()}%")
            )

        if verification_status:
            query = query.filter(
                func.lower(Organization.verification_status)
                == verification_status.lower().strip()
            )

        if search:
            search_term = f"%{search.strip()}%"
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
            sort_by.lower(),
            Organization.name,
        )

        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        total = query.count()
        offset = (page - 1) * page_size

        organizations = (
            query.options(
                joinedload(Organization.opportunities),
                joinedload(Organization.sources),
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        results = [_serialize_organization(org) for org in organizations]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "results": results,
        }

    finally:
        db.close()


@router.get("/{organization_id}")
def get_organization(organization_id: str):
    db = SessionLocal()

    try:
        org = (
            db.query(Organization)
            .options(
                joinedload(Organization.opportunities),
                joinedload(Organization.sources),
            )
            .filter(Organization.id == organization_id)
            .first()
        )

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        return _serialize_organization(org)

    finally:
        db.close()
