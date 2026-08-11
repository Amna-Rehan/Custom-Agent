from typing import Any

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str


class ParsedIntent(BaseModel):
    entity_type: str | None = None
    country: str | None = None
    city: str | None = None
    industry: str | None = None
    startup_stage: str | None = None
    investment_stage: str | None = None
    limit: int = 10
    funding_requirement: str | None = None
    opportunity_intent: bool = False


class OpportunityResult(BaseModel):
    application_url: str | None = None
    eligibility: str | None = None
    startup_stage: str | None = None
    investment_stage: str | None = None
    funding_amount: str | None = None
    funding_currency: str | None = None
    equity_required: str | None = None
    program_duration: str | None = None
    benefits: list[str] = Field(default_factory=list)
    application_process: str | None = None
    deadline: str | None = None
    geographic_focus: str | None = None
    sector_focus: str | None = None
    mentorship: str | None = None
    investor_access: str | None = None
    network_access: str | None = None
    office_space: str | None = None
    grants: str | None = None
    credits: str | None = None
    cohort_information: str | None = None
    required_documents: str | None = None
    selection_process: str | None = None
    program_status: str | None = None


class ContactResult(BaseModel):
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None


class VerificationResult(BaseModel):
    score: int = 0
    status: str = "unverified"
    source: str | None = None


class FactSource(BaseModel):
    field: str | None = None
    value: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    verified: bool = False


class SearchResultItem(BaseModel):
    id: str | None = None
    organization_name: str | None = None
    organization_type: str | None = None
    country: str | None = None
    city: str | None = None
    industry: str | None = None
    description: str | None = None
    website: str | None = None
    opportunity: OpportunityResult | None = None
    contact: ContactResult | None = None
    verification: VerificationResult | None = None
    sources: list[FactSource] = Field(default_factory=list)
    confidence_score: int | None = None
    rank_score: float | None = None
    error: str | None = None


class SearchResponse(BaseModel):
    query: str | None = None
    parsed_intent: ParsedIntent | dict[str, Any] | None = None
    count: int
    results: list[SearchResultItem] | list[Any]
