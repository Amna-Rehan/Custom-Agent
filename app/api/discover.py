from fastapi import APIRouter

from app.schemas.discover import (
    DiscoverRequest,
    DiscoverResponse,
)

from app.services.discovery_service import DiscoveryService
from app.services.research_service import ResearchService

router = APIRouter(
    prefix="/discover",
    tags=["Discovery"],
)

discovery = DiscoveryService()
research = ResearchService()


@router.post(
    "/",
    response_model=DiscoverResponse,
)
def discover(data: DiscoverRequest):

    websites = discovery.search(
        data.query,
        data.category,
        data.country,
    )

    organizations = []

    for website in websites:

        try:

            result = research.crawl(website.website)

            organizations.append(
                result["ai_analysis"]
            )

        except Exception as e:

            print(e)

    return {
        "count": len(organizations),
        "results": organizations,
    }