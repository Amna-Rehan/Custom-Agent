from fastapi import APIRouter

from app.schemas.search import (
    SearchRequest,
    SearchResponse,
)

from app.services.search_service import SearchService


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


service = SearchService()


@router.post(
    "/",
    response_model=SearchResponse,
)
def search(data: SearchRequest):

    return service.search(
        data.query
    )