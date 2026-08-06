from pydantic import BaseModel


class EnrichRequest(BaseModel):

    query: str

    category: str = "Investor"

    country: str = ""


class EnrichResponse(BaseModel):

    results: list