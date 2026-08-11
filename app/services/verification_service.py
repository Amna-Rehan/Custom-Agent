from urllib.parse import urlparse

import requests

from app.config import settings


OFFICIAL_SOURCE_TYPES = {
    "official",
    "application",
    "government",
    "program",
    "documentation",
}


class VerificationService:
    """Source-based verification — distinct from AI confidence_score."""

    def verify(
        self,
        url: str,
        title: str,
        description: str,
        linkedin: str,
        fact_sources: list | None = None,
        opportunity: dict | None = None,
    ):
        score = 0
        reasons: list[str] = []
        fact_sources = fact_sources or []
        opportunity = opportunity or {}

        website_accessible = False

        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=settings.REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            if response.status_code == 200:
                website_accessible = True
                score += 30
                reasons.append("Official website is reachable")
        except requests.RequestException:
            pass

        if url.lower().startswith("https://"):
            score += 10
            reasons.append("Website uses HTTPS")

        if title and len(title.strip()) > 3:
            score += 15
            reasons.append("Website has a valid title")

        if description and len(description.strip()) > 20:
            score += 10
            reasons.append("Website contains organization description")

        if linkedin and "linkedin.com" in linkedin.lower():
            score += 10
            reasons.append("LinkedIn organization profile found")

        official_facts = [
            fact
            for fact in fact_sources
            if isinstance(fact, dict)
            and fact.get("source_url")
            and (
                fact.get("verified")
                or (fact.get("source_type") or "").lower()
                in OFFICIAL_SOURCE_TYPES
            )
        ]

        if official_facts:
            score += min(25, 5 * len(official_facts))
            reasons.append(
                f"{len(official_facts)} fact(s) supported by official sources"
            )

        opportunity_fields = [
            "funding_amount",
            "application_url",
            "eligibility",
            "equity_required",
            "deadline",
            "program_duration",
        ]
        supported_opportunity = sum(
            1
            for field in opportunity_fields
            if opportunity.get(field)
        )
        if supported_opportunity:
            score += min(15, 3 * supported_opportunity)
            reasons.append(
                f"{supported_opportunity} opportunity field(s) extracted from sources"
            )

        # Strongest source URL: prefer official fact source, else homepage
        strongest_source = url if website_accessible else None
        for fact in official_facts:
            source_url = fact.get("source_url")
            source_type = (fact.get("source_type") or "").lower()
            if source_url and source_type in {
                "official",
                "application",
                "government",
                "program",
            }:
                strongest_source = source_url
                break

        if score >= 80 and website_accessible and (
            official_facts or (title and description)
        ):
            status = "verified"
        elif score >= 50 and website_accessible:
            status = "partially_verified"
        else:
            status = "unverified"

        # Never mark verified solely because a page loaded with a title
        if status == "verified" and not website_accessible:
            status = "unverified"

        return {
            "score": min(score, 100),
            "status": status,
            "source": strongest_source,
            "reasons": reasons,
        }

    def classify_source_type(self, url: str, page_path: str = "") -> str:
        domain = urlparse(url).netloc.lower()
        path = (page_path or urlparse(url).path).lower()

        if any(
            token in domain
            for token in (".gov", "gov.", "government")
        ):
            return "government"

        if any(
            token in path
            for token in ("/apply", "/application", "/applications")
        ):
            return "application"

        if any(
            token in path
            for token in ("/program", "/accelerator", "/incubator", "/grant")
        ):
            return "program"

        if any(token in path for token in ("/docs", "/documentation", "/faq")):
            return "documentation"

        return "official"
