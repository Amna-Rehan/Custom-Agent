from fastapi import APIRouter

from app.schemas.search import (
    ResearchRequest,
    ResearchResponse,
)

from app.services.research_service import ResearchService

router = APIRouter(
    prefix="/research",
    tags=["Research"],
)

service = ResearchService()


@router.post(
    "/",
    response_model=ResearchResponse,
)
def research(data: ResearchRequest):

    return service.crawl(
        data.url
    )