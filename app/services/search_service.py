import logging
from urllib.parse import urlparse

from app.config import settings
from app.services.ai_service import AIService
from app.services.discovery_service import DiscoveryService
from app.services.research_service import ResearchService

logger = logging.getLogger(__name__)


class SearchService:

    def __init__(self):
        self.discovery = DiscoveryService()
        self.research = ResearchService()
        self.ai = AIService()

    def parse_query(self, query: str) -> dict:
        """
        Backward-compatible parser.

        Returns legacy keys (query/category/country) plus full intent fields.
        """
        intent = self.ai.parse_search_intent(query)

        category = intent.get("entity_type") or "Organization"
        country = intent.get("country") or ""

        # Legacy clean_query fragment for discovery
        clean_parts = []
        if intent.get("industry"):
            clean_parts.append(intent["industry"])
        if intent.get("city"):
            clean_parts.append(intent["city"])
        if intent.get("startup_stage"):
            clean_parts.append(intent["startup_stage"])
        clean_query = " ".join(clean_parts).strip() or category

        return {
            "query": clean_query,
            "category": category,
            "country": country,
            **intent,
        }

    def search(self, user_query: str) -> dict:
        parsed = self.parse_query(user_query)
        intent = {
            "entity_type": parsed.get("entity_type") or parsed.get("category"),
            "country": parsed.get("country") or None,
            "city": parsed.get("city"),
            "industry": parsed.get("industry"),
            "startup_stage": parsed.get("startup_stage"),
            "investment_stage": parsed.get("investment_stage"),
            "limit": parsed.get("limit") or settings.SEARCH_DEFAULT_LIMIT,
            "funding_requirement": parsed.get("funding_requirement"),
            "opportunity_intent": bool(parsed.get("opportunity_intent")),
        }

        limit = int(intent["limit"])
        discovery_limit = max(
            limit * 2,
            min(settings.SEARCH_DISCOVERY_LIMIT, max(limit * 3, 20)),
        )
        research_limit = min(
            settings.SEARCH_RESEARCH_LIMIT,
            max(limit + 5, limit),
        )

        logger.info(
            "Search intent=%s discovery=%s research=%s",
            intent,
            discovery_limit,
            research_limit,
        )

        try:
            discovered = self.discovery.search(
                query=parsed.get("query"),
                category=intent.get("entity_type"),
                country=intent.get("country"),
                intent=intent,
                max_results=discovery_limit,
            )
        except Exception as exc:
            logger.error("Discovery failed: %s", exc)
            discovered = []

        # Rank candidates before expensive research
        ranked = sorted(
            discovered,
            key=lambda item: self.discovery.score_candidate(item, intent),
            reverse=True,
        )
        shortlist = ranked[:research_limit]

        researched = self.research.crawl_many(
            [item.website for item in shortlist],
            deep=True,
        )

        # Map website → discovery metadata for ranking fallbacks
        discovery_by_domain = {}
        for item in shortlist:
            domain = urlparse(item.website).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            discovery_by_domain[domain] = item


        shaped = []
        for item in researched:
            analysis = item.get("ai_analysis") or {}
            has_signal = bool(
                analysis.get("organization_name")
                or analysis.get("organization_type")
                or analysis.get("summary")
                or analysis.get("country")
            )
            # Skip hard failures with no extracted organization data
            if item.get("error") and not has_signal:
                continue

            shaped_item = self._shape_result(item, intent, discovery_by_domain)
            if not shaped_item:
                continue
            # Prefer real orgs over bare error stubs
            if shaped_item.get("error") and not shaped_item.get(
                "organization_type"
            ):
                continue
            shaped.append(shaped_item)

        shaped.sort(
            key=lambda row: (
                1 if row.get("organization_type") else 0,
                1 if row.get("description") else 0,
                1 if row.get("opportunity") else 0,
                row.get("rank_score") or 0,
            ),
            reverse=True,
        )

        results = shaped[:limit]

        # If too few successes, include best remaining researched items
        if len(results) < min(3, limit):
            for item in researched:
                website = (item.get("raw") or {}).get("website")
                if not website:
                    continue
                if any(r.get("website") == website for r in results):
                    continue
                stub = self._shape_result(item, intent, discovery_by_domain)
                if stub:
                    results.append(stub)
                if len(results) >= limit:
                    break

        return {
            "query": user_query,
            "parsed_intent": {
                "entity_type": intent.get("entity_type"),
                "country": intent.get("country"),
                "city": intent.get("city"),
                "industry": intent.get("industry"),
                "startup_stage": intent.get("startup_stage"),
                "investment_stage": intent.get("investment_stage"),
                "limit": limit,
                "funding_requirement": intent.get("funding_requirement"),
                "opportunity_intent": intent.get("opportunity_intent"),
            },
            "count": len(results),
            "results": results,
        }

    def _shape_result(
        self,
        researched: dict,
        intent: dict,
        discovery_by_domain: dict,
    ) -> dict | None:
        analysis = researched.get("ai_analysis") or {}
        raw = researched.get("raw") or {}
        verification = researched.get("verification") or {}
        opportunity = researched.get("opportunity") or analysis.get("opportunity") or {}
        sources = researched.get("sources") or analysis.get("fact_sources") or []

        website = raw.get("website") or analysis.get("website")
        if not website:
            return None

        domain = urlparse(website).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        discovered = discovery_by_domain.get(domain)

        industries = analysis.get("industries") or []
        if isinstance(industries, list):
            industry = ", ".join(str(i) for i in industries if i) or None
        else:
            industry = str(industries) if industries else None

        org_name = (
            analysis.get("organization_name")
            or raw.get("name")
            or (discovered.name if discovered else None)
        )

        db_info = researched.get("database") or {}
        save_error = db_info.get("error")
        crawl_error = researched.get("error") or analysis.get("error")
        # Don't surface SQL/DB errors when extraction succeeded
        public_error = None
        if crawl_error and not (
            analysis.get("organization_name") or analysis.get("organization_type")
        ):
            public_error = crawl_error
        elif save_error and not db_info.get("saved"):
            public_error = None  # extraction still usable

        opportunity_payload = None
        if isinstance(opportunity, dict) and any(opportunity.values()):
            benefits = opportunity.get("benefits") or []
            if isinstance(benefits, str):
                benefits = [benefits] if benefits.strip() else []

            opportunity_payload = {
                "application_url": opportunity.get("application_url"),
                "eligibility": opportunity.get("eligibility"),
                "startup_stage": opportunity.get("startup_stage"),
                "investment_stage": (
                    opportunity.get("investment_stage")
                    if not isinstance(opportunity.get("investment_stage"), list)
                    else ", ".join(opportunity.get("investment_stage") or [])
                ),
                "funding_amount": opportunity.get("funding_amount"),
                "funding_currency": opportunity.get("funding_currency"),
                "equity_required": opportunity.get("equity_required"),
                "program_duration": opportunity.get("program_duration"),
                "benefits": benefits,
                "application_process": opportunity.get("application_process"),
                "deadline": opportunity.get("deadline")
                or opportunity.get("application_deadline"),
                "geographic_focus": opportunity.get("geographic_focus"),
                "sector_focus": opportunity.get("sector_focus"),
                "mentorship": opportunity.get("mentorship"),
                "investor_access": opportunity.get("investor_access"),
                "network_access": opportunity.get("network_access"),
                "office_space": opportunity.get("office_space"),
                "grants": opportunity.get("grants"),
                "credits": opportunity.get("credits"),
                "cohort_information": opportunity.get("cohort_information"),
                "required_documents": opportunity.get("required_documents"),
                "selection_process": opportunity.get("selection_process"),
                "program_status": opportunity.get("program_status"),
            }

        fact_sources = []
        for fact in sources:
            if not isinstance(fact, dict):
                continue
            fact_sources.append(
                {
                    "field": fact.get("field") or fact.get("field_name"),
                    "value": fact.get("value"),
                    "source_url": fact.get("source_url") or fact.get("url"),
                    "source_type": fact.get("source_type"),
                    "verified": bool(fact.get("verified")),
                }
            )

        rank_score = self._rank_result(
            {
                "organization_name": org_name,
                "organization_type": analysis.get("organization_type"),
                "country": analysis.get("country"),
                "city": analysis.get("city"),
                "industry": industry,
                "description": analysis.get("summary") or raw.get("description"),
                "website": website,
                "opportunity": opportunity_payload,
                "verification": verification,
                "discovered_score": (
                    self.discovery.score_candidate(discovered, intent)
                    if discovered
                    else 0
                ),
            },
            intent,
        )

        return {
            "id": db_info.get("id"),
            "organization_name": org_name,
            "organization_type": analysis.get("organization_type"),
            "country": analysis.get("country"),
            "city": analysis.get("city"),
            "industry": industry,
            "description": analysis.get("summary") or raw.get("description"),
            "website": website,
            "opportunity": opportunity_payload,
            "contact": {
                "email": analysis.get("email") or raw.get("email"),
                "phone": analysis.get("phone") or raw.get("phone"),
                "linkedin": analysis.get("linkedin") or raw.get("linkedin"),
            },
            "verification": {
                "score": verification.get("score")
                or db_info.get("verification_score")
                or 0,
                "status": verification.get("status")
                or db_info.get("verification_status")
                or "unverified",
                "source": verification.get("source")
                or db_info.get("verification_source"),
            },
            "sources": fact_sources,
            "confidence_score": analysis.get("confidence_score"),
            "rank_score": rank_score,
            "error": public_error,
        }

    def _rank_result(self, result: dict, intent: dict) -> float:
        score = float(result.get("discovered_score") or 0)

        entity = (intent.get("entity_type") or "").lower()
        org_type = (result.get("organization_type") or "").lower()
        if entity and entity == org_type:
            score += 40
        elif entity and entity in org_type:
            score += 20

        country = (intent.get("country") or "").lower()
        result_country = (result.get("country") or "").lower()
        if country and country == result_country:
            score += 30
        elif country and country in (
            result.get("description") or ""
        ).lower():
            score += 10

        city = (intent.get("city") or "").lower()
        if city and city == (result.get("city") or "").lower():
            score += 15

        industry = (intent.get("industry") or "").lower()
        result_industry = (result.get("industry") or "").lower()
        if industry and industry in result_industry:
            score += 25

        stage = (
            intent.get("startup_stage") or intent.get("investment_stage") or ""
        ).lower()
        opportunity = result.get("opportunity") or {}
        if stage:
            opp_stage = (
                f"{opportunity.get('startup_stage') or ''} "
                f"{opportunity.get('investment_stage') or ''}"
            ).lower()
            if stage in opp_stage:
                score += 15

        if intent.get("opportunity_intent"):
            if opportunity.get("application_url"):
                score += 20
            if opportunity.get("funding_amount") or opportunity.get(
                "eligibility"
            ):
                score += 15
            if opportunity.get("deadline") or opportunity.get("benefits"):
                score += 10

        verification = result.get("verification") or {}
        status = (verification.get("status") or "").lower()
        if status == "verified":
            score += 25
        elif status == "partially_verified":
            score += 12

        score += min(15, (verification.get("score") or 0) / 10)

        # Completeness
        filled = sum(
            1
            for key in (
                "organization_name",
                "organization_type",
                "country",
                "website",
                "description",
                "industry",
            )
            if result.get(key)
        )
        score += filled * 2

        if result.get("website"):
            score += 10

        return score
