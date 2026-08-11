import json
import logging
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.config import settings
from app.schemas.ai_extraction import (
    OrganizationExtractionSchema,
    SearchIntentSchema,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

COUNTRIES = [
    "Germany",
    "United States",
    "United Kingdom",
    "France",
    "Canada",
    "Australia",
    "Pakistan",
    "India",
    "Singapore",
    "Netherlands",
    "Switzerland",
    "Sweden",
    "Denmark",
    "Norway",
    "Finland",
    "Spain",
    "Italy",
    "Belgium",
    "Austria",
    "Ireland",
    "Israel",
    "Japan",
    "South Korea",
    "United Arab Emirates",
    "Europe",
    "EU",
    "Middle East",
    "Asia",
    "Africa",
    "North America",
    "South America",
]


def extract_json_payload(text: str) -> dict[str, Any] | None:
    """Safely extract a JSON object from model output (fences, noise, etc.)."""

    if not text:
        return None

    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None

    candidate = match.group(0)
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        repaired = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            parsed = json.loads(repaired)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return None

    return None


def validate_ai_payload(
    payload: dict[str, Any] | None,
    schema: type[T],
) -> T | None:
    if not payload:
        return None
    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        logger.warning("AI payload validation failed: %s", exc)
        try:
            return schema.model_validate(
                {k: v for k, v in payload.items() if v is not None}
            )
        except ValidationError:
            return None


class AIService:

    def __init__(self):
        self._model = None
        self._initialized = False

    def _ensure_model(self):
        if self._initialized:
            return self._model

        self._initialized = True
        try:
            import vertexai
            from google.oauth2 import service_account
            from vertexai.generative_models import GenerativeModel

            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_APPLICATION_CREDENTIALS
            )
            vertexai.init(
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION,
                credentials=credentials,
            )
            self._model = GenerativeModel(settings.VERTEX_MODEL)
        except Exception as exc:
            logger.error("Failed to initialize Vertex AI: %s", exc)
            self._model = None

        return self._model

    def _generate_json(self, prompt: str) -> dict[str, Any] | None:
        model = self._ensure_model()
        if model is None:
            return None
        try:
            response = model.generate_content(prompt)
            text = (response.text or "").strip()
            return extract_json_payload(text)
        except Exception as exc:
            logger.error("Vertex AI error: %s", exc)
            return None

    def parse_search_intent(self, query: str) -> dict[str, Any]:
        """Parse NL query into structured intent (Gemini + deterministic fallback)."""

        deterministic = self._deterministic_intent(query)

        prompt = f"""
You are a search intent parser for a startup/investor intelligence platform.

Parse this user query into structured JSON.

User query:
{query}

Return ONLY valid JSON:
{{
  "entity_type": "Startup|Investor|Accelerator|Incubator|Grant|Program|null",
  "country": "string or null",
  "city": "string or null",
  "industry": "string or null",
  "startup_stage": "string or null",
  "investment_stage": "string or null",
  "limit": 10,
  "funding_requirement": "string or null",
  "opportunity_intent": false
}}

Rules:
- entity_type should be the primary target (Accelerator, Startup, Investor, etc.)
- opportunity_intent=true if user wants programs, applications, funding to apply for,
  grants, accelerators/incubators they can join, or similar
- Extract limit if user asks for N results (default 10)
- Do not invent locations or industries not implied by the query
- Return ONLY JSON
"""

        payload = self._generate_json(prompt)
        validated = validate_ai_payload(payload, SearchIntentSchema)

        if validated:
            data = validated.model_dump()
            for key in (
                "entity_type",
                "country",
                "city",
                "industry",
                "startup_stage",
                "investment_stage",
                "funding_requirement",
            ):
                if not data.get(key) and deterministic.get(key):
                    data[key] = deterministic[key]

            if not data.get("limit"):
                data["limit"] = deterministic["limit"]

            if deterministic.get("opportunity_intent"):
                data["opportunity_intent"] = True

            if data.get("entity_type"):
                data["entity_type"] = self._normalize_entity_type(
                    data["entity_type"]
                )

            return data

        return deterministic

    def _normalize_entity_type(self, value: str | None) -> str | None:
        if not value:
            return None
        cleaned = value.strip().lower()
        mapping = {
            "investor": "Investor",
            "investors": "Investor",
            "angel": "Investor",
            "angels": "Investor",
            "vc": "Investor",
            "startup": "Startup",
            "startups": "Startup",
            "incubator": "Incubator",
            "incubators": "Incubator",
            "accelerator": "Accelerator",
            "accelerators": "Accelerator",
            "grant": "Grant",
            "grants": "Grant",
            "program": "Program",
            "programs": "Program",
            "funding": "Grant",
            "opportunity": "Program",
            "opportunities": "Program",
        }
        return mapping.get(cleaned, value.strip().title())

    def _deterministic_intent(self, query: str) -> dict[str, Any]:
        text = query.strip()
        lower = text.lower()

        entity_type = None
        if re.search(r"\b(investor|investors|angel|vc|venture capital)\b", lower):
            entity_type = "Investor"
        elif re.search(r"\b(accelerator|accelerators)\b", lower):
            entity_type = "Accelerator"
        elif re.search(r"\b(incubator|incubators)\b", lower):
            entity_type = "Incubator"
        elif re.search(r"\b(grant|grants)\b", lower):
            entity_type = "Grant"
        elif re.search(
            r"\b(program|programs|funding opportunit|opportunities)\b",
            lower,
        ):
            entity_type = "Program"
        elif re.search(r"\b(startup|startups)\b", lower):
            entity_type = "Startup"

        country = None
        for item in COUNTRIES:
            if item.lower() in lower:
                country = "Europe" if item == "EU" else item
                break

        if "pakistani" in lower and not country:
            country = "Pakistan"
        if "german" in lower and not country:
            country = "Germany"

        city = None
        cities = [
            "Lahore",
            "Karachi",
            "Islamabad",
            "Berlin",
            "Munich",
            "London",
            "Paris",
            "Dubai",
            "Singapore",
            "New York",
            "San Francisco",
            "Toronto",
        ]
        for item in cities:
            if item.lower() in lower:
                city = item
                break

        industry = None
        industries = [
            ("fintech", "Fintech"),
            ("financial technology", "Fintech"),
            ("artificial intelligence", "AI"),
            ("machine learning", "AI"),
            (r"\bai\b", "AI"),
            ("healthtech", "Healthtech"),
            ("healthcare", "Healthcare"),
            ("edtech", "Edtech"),
            ("climate", "Climate"),
            ("cleantech", "Cleantech"),
            ("saas", "SaaS"),
            ("blockchain", "Blockchain"),
            ("biotech", "Biotech"),
        ]
        for pattern, label in industries:
            if re.search(pattern, lower):
                industry = label
                break

        startup_stage = None
        stage_patterns = [
            (r"\bpre[-\s]?seed\b", "Pre-seed"),
            (r"\bearly[-\s]?stage\b", "Early-stage"),
            (r"\blate[-\s]?stage\b", "Late-stage"),
            (r"\bseries\s*a\b", "Series A"),
            (r"\bseries\s*b\b", "Series B"),
            (r"\bseed\b", "Seed"),
            (r"\bgrowth\b", "Growth"),
        ]
        for pattern, label in stage_patterns:
            if re.search(pattern, lower):
                startup_stage = label
                break

        investment_stage = startup_stage

        limit = settings.SEARCH_DEFAULT_LIMIT
        limit_match = re.search(r"\b(\d{1,2})\b", lower)
        if limit_match:
            limit = max(1, min(int(limit_match.group(1)), 50))

        opportunity_intent = bool(
            re.search(
                r"\b(apply|application|applications|program|programs|"
                r"funding opportunit|grant|grants|"
                r"incubator|incubators|accelerator|accelerators|"
                r"can apply|opportunities)\b",
                lower,
            )
        )

        if entity_type == "Startup" and not re.search(
            r"\b(apply|application|funding opportunit|grant|program)\b",
            lower,
        ):
            opportunity_intent = False

        funding_requirement = None
        if re.search(r"\b(funding|investment|grant money|capital)\b", lower):
            funding_requirement = "funding"

        return {
            "entity_type": entity_type,
            "country": country,
            "city": city,
            "industry": industry,
            "startup_stage": startup_stage,
            "investment_stage": investment_stage,
            "limit": limit,
            "funding_requirement": funding_requirement,
            "opportunity_intent": opportunity_intent,
        }

    def analyze(self, website_data: dict) -> dict[str, Any]:
        """Deep organization + opportunity extraction from scraped website data."""

        website = website_data.get("website")
        name = website_data.get("name")
        pages = website_data.get("pages", [])
        combined_text = website_data.get("combined_text", "")
        text_excerpt = (combined_text or "")[:12000]

        prompt = f"""
You are a senior venture capital and startup ecosystem analyst.

Analyze the organization using ONLY the supplied website data.
Do NOT invent facts that are not supported by the website data.
If a field is not supported, return null or an empty list.

Website URL: {website}
Homepage title/name: {name}

Pages scraped:
{json.dumps(pages, indent=2)[:4000]}

Extracted contact hints:
{json.dumps({
    "email": website_data.get("email"),
    "phone": website_data.get("phone"),
    "linkedin": website_data.get("linkedin"),
    "description": website_data.get("description"),
}, indent=2)}

Website text excerpt:
{text_excerpt}

Return ONLY valid JSON:
{{
  "organization_name": null,
  "organization_type": "Investor|Startup|Incubator|Accelerator|Grant|Program",
  "country": null,
  "city": null,
  "website": "{website}",
  "email": null,
  "phone": null,
  "linkedin": null,
  "founding_year": null,
  "industries": [],
  "investment_stage": [],
  "startup_stage": null,
  "ticket_size": null,
  "portfolio_examples": [],
  "summary": null,
  "confidence_score": 0,
  "opportunity": {{
    "application_url": null,
    "eligibility": null,
    "startup_stage": null,
    "investment_stage": null,
    "funding_amount": null,
    "funding_currency": null,
    "equity_required": null,
    "program_duration": null,
    "benefits": [],
    "application_process": null,
    "deadline": null,
    "geographic_focus": null,
    "sector_focus": null,
    "mentorship": null,
    "investor_access": null,
    "network_access": null,
    "office_space": null,
    "grants": null,
    "credits": null,
    "cohort_information": null,
    "required_documents": null,
    "selection_process": null,
    "program_status": null
  }},
  "fact_sources": [
    {{
      "field": "funding_amount",
      "value": "$120,000",
      "source_url": "https://example.org/program",
      "source_type": "official",
      "verified": true
    }}
  ]
}}

Rules:
1. confidence_score is YOUR confidence in extraction quality (0-100).
   It is NOT the same as verification_status.
2. Only include fact_sources for important fields that appear in the text,
   with the page URL where the fact was found.
3. Prefer official application/program pages for opportunity fields.
4. organization_type MUST be one of the allowed values.
5. Return ONLY JSON.
"""

        payload = self._generate_json(prompt)
        validated = validate_ai_payload(payload, OrganizationExtractionSchema)

        if validated:
            analysis = validated.model_dump()
        elif payload:
            analysis = payload
        else:
            analysis = {}

        analysis.setdefault("organization_name", website_data.get("name"))
        analysis.setdefault("website", website)
        analysis.setdefault("email", website_data.get("email"))
        analysis.setdefault("phone", website_data.get("phone"))
        analysis.setdefault("linkedin", website_data.get("linkedin"))
        analysis.setdefault("summary", website_data.get("description"))
        analysis.setdefault("confidence_score", 0)
        analysis.setdefault("industries", [])
        analysis.setdefault("investment_stage", [])
        analysis.setdefault("portfolio_examples", [])
        analysis.setdefault("fact_sources", [])
        analysis.setdefault("opportunity", None)

        analysis.pop("verification_status", None)
        analysis.pop("verification_source", None)

        if not analysis.get("organization_name"):
            analysis["organization_name"] = website_data.get("name") or website

        if "error" not in analysis and not payload:
            analysis["error"] = "Failed to parse AI response"
            analysis["confidence_score"] = 0

        return analysis
