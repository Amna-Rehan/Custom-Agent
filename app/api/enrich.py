from fastapi import APIRouter

from app.schemas.enrich import (
    EnrichRequest,
    EnrichResponse,
)

from app.services.enrichment_service import EnrichmentService


router = APIRouter(
    prefix="/enrich",
    tags=["Enrichment"],
)

service = EnrichmentService()


@router.post(
    "/",
    response_model=EnrichResponse,
)
def enrich(data: EnrichRequest):

    return {

        "results": service.enrich(

            query=data.query,

            category=data.category,

            country=data.country,

        )

    }