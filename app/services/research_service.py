import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.services.ai_service import AIService
from app.services.database_service import DatabaseService
from app.services.verification_service import VerificationService

logger = logging.getLogger(__name__)

database = DatabaseService()
ai = AIService()
verifier = VerificationService()

EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
PHONE_REGEX = r"\+?[1-9]\d{7,14}"

RELEVANT_PATH_KEYWORDS = (
    "apply",
    "application",
    "applications",
    "program",
    "programs",
    "accelerator",
    "incubator",
    "funding",
    "grant",
    "grants",
    "eligibility",
    "portfolio",
    "about",
    "contact",
    "faq",
    "cohort",
    "invest",
    "criteria",
)


class ResearchService:

    def crawl(self, url: str, deep: bool = True):
        headers = {"User-Agent": "Mozilla/5.0"}
        timeout = settings.REQUEST_TIMEOUT

        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
        except Exception as exc:
            logger.warning("Failed to fetch %s: %s", url, exc)
            raise

        soup = BeautifulSoup(response.text, "html.parser")
        homepage_text = soup.get_text(" ", strip=True)

        title = soup.title.text.strip() if soup.title else ""
        description = ""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            description = meta.get("content", "") or ""

        emails = re.findall(EMAIL_REGEX, homepage_text)
        phones = re.findall(PHONE_REGEX, homepage_text)

        linkedin = ""
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "linkedin.com" in href:
                linkedin = href
                break

        pages = [
            {
                "url": url,
                "title": title,
                "text": homepage_text[:8000],
            }
        ]
        pages_scraped = [url]

        if deep:
            internal_links = self._find_relevant_links(url, soup)
            for page_url in internal_links[: settings.RESEARCH_MAX_PAGES - 1]:
                try:
                    page_data = self._fetch_page(page_url, headers, timeout)
                    if page_data:
                        pages.append(page_data)
                        pages_scraped.append(page_url)
                except Exception as exc:
                    logger.info("Skipping page %s: %s", page_url, exc)

        combined_text = "\n\n".join(
            f"URL: {page['url']}\nTITLE: {page.get('title', '')}\n"
            f"{page.get('text', '')}"
            for page in pages
        )

        # Prefer contacts found across pages
        for page in pages[1:]:
            page_text = page.get("text", "")
            if not emails:
                emails = re.findall(EMAIL_REGEX, page_text)
            if not phones:
                phones = re.findall(PHONE_REGEX, page_text)

        website_data = {
            "name": title,
            "website": url,
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "linkedin": linkedin or None,
            "description": description,
            "pages": pages,
            "pages_scraped": pages_scraped,
            "combined_text": combined_text,
        }

        analysis = ai.analyze(website_data)

        verification = verifier.verify(
            url=url,
            title=title or analysis.get("organization_name") or "",
            description=description or analysis.get("summary") or "",
            linkedin=linkedin or analysis.get("linkedin") or "",
            fact_sources=analysis.get("fact_sources") or [],
            opportunity=analysis.get("opportunity"),
        )

        analysis["verification_status"] = verification["status"]
        analysis["verification_source"] = verification["source"]
        analysis["verification_score"] = verification["score"]
        # Keep confidence_score separate from verification_score
        if "confidence_score" not in analysis:
            analysis["confidence_score"] = 0

        opportunity = analysis.get("opportunity") or {}
        fact_sources = analysis.get("fact_sources") or []

        # Enrich fact sources with homepage if empty but verified
        if not fact_sources and verification["status"] != "unverified":
            fact_sources = [
                {
                    "field": "organization_identity",
                    "value": analysis.get("organization_name") or title,
                    "source_url": url,
                    "source_type": "official",
                    "verified": True,
                }
            ]
            analysis["fact_sources"] = fact_sources

        database_info = {
            "saved": False,
            "id": None,
            "verification_status": verification["status"],
            "verification_source": verification["source"],
            "verification_score": verification["score"],
        }

        try:
            saved_org = database.save(analysis)
            database_info = {
                "saved": True,
                "id": str(saved_org.id),
                "verification_status": saved_org.verification_status,
                "verification_source": saved_org.verification_source,
                "verification_score": saved_org.verification_score,
            }
        except Exception as exc:
            logger.error("Database save failed for %s: %s", url, exc)
            database_info["error"] = str(exc)

        return {
            "raw": {
                "name": title,
                "website": url,
                "email": website_data["email"],
                "phone": website_data["phone"],
                "linkedin": website_data["linkedin"],
                "description": description,
                "pages_scraped": pages_scraped,
            },
            "ai_analysis": analysis,
            "opportunity": opportunity,
            "sources": fact_sources,
            "verification": verification,
            "database": database_info,
        }

    def crawl_many(self, urls: list[str], deep: bool = True) -> list[dict]:
        """Research multiple URLs concurrently; one failure does not stop others."""

        results: list[dict] = []
        if not urls:
            return results

        workers = max(1, min(settings.RESEARCH_CONCURRENCY, len(urls)))

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self.crawl, url, deep): url for url in urls
            }
            for future in as_completed(futures):
                url = futures[future]
                try:
                    results.append(future.result())
                except Exception as exc:
                    logger.warning("Research failed for %s: %s", url, exc)
                    results.append(
                        {
                            "raw": {"website": url},
                            "ai_analysis": {"error": str(exc)},
                            "opportunity": None,
                            "sources": [],
                            "verification": {
                                "score": 0,
                                "status": "unverified",
                                "source": None,
                            },
                            "database": {"saved": False},
                            "error": str(exc),
                        }
                    )

        return results

    def _find_relevant_links(self, base_url: str, soup: BeautifulSoup) -> list[str]:
        base = urlparse(base_url)
        found: list[str] = []
        seen = {base_url.rstrip("/")}

        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            if not href or href.startswith("#") or href.startswith("mailto:"):
                continue

            absolute = urljoin(base_url, href)
            parsed = urlparse(absolute)

            if parsed.netloc.lower() != base.netloc.lower():
                continue

            path = parsed.path.lower()
            if not any(keyword in path for keyword in RELEVANT_PATH_KEYWORDS):
                continue

            normalized = absolute.split("#")[0].rstrip("/")
            if normalized in seen:
                continue

            seen.add(normalized)
            found.append(absolute)

            if len(found) >= settings.RESEARCH_MAX_PAGES:
                break

        return found

    def _fetch_page(
        self,
        url: str,
        headers: dict,
        timeout: int,
    ) -> dict | None:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        if len(text) < 40:
            return None
        title = soup.title.text.strip() if soup.title else ""
        return {
            "url": url,
            "title": title,
            "text": text[:8000],
        }
