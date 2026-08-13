from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from app.config import settings
from app.schemas.discover import SearchResult
from app.services.filters import (
    BAD_DOMAINS,
    BAD_PATH_FRAGMENTS,
    BLOCKED_TEXT_PATTERNS,
    is_blocked_domain,
    is_blocked_path,
    is_blocked_text,
)


class DiscoveryService:

    def is_valid(self, url: str) -> bool:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        if is_blocked_domain(domain):
            return False

        if is_blocked_path(path):
            return False

        # Skip obvious article deep-links
        if path.count("/") >= 3 and any(
            token in path
            for token in ("-startup-", "/20", "/news", "/blog")
        ):
            return False

        return True

    def is_relevant(
        self,
        title: str,
        description: str,
        intent: dict | None = None,
        url: str = "",
    ) -> bool:
        text = f"{title} {description}".lower()
        intent = intent or {}

        if is_blocked_text(text, BLOCKED_TEXT_PATTERNS):
            return False

        # Reject newsy titles when looking for organizations
        newsy_title = is_blocked_text(
            title or "",
            [
                "news",
                "eyes",
                "posted",
                "rethinking",
                "directory",
                "complete list",
                "unlock your",
                "success stories",
            ],
        )
        if newsy_title:
            return False

        entity = (intent.get("entity_type") or "").lower()
        if entity and entity not in text:
            # Allow through if URL/domain looks organizational
            domain = urlparse(url).netloc.lower()
            country = (intent.get("country") or "").lower()
            country_tlds = {
                "pakistan": ".pk",
                "germany": ".de",
                "united kingdom": ".uk",
                "india": ".in",
                "france": ".fr",
                "singapore": ".sg",
            }
            tld = country_tlds.get(country)
            if tld and domain.endswith(tld):
                return True
            # Weak match — keep only if description mentions company/org signals
            if not any(
                token in text
                for token in (
                    "company",
                    "founder",
                    "venture",
                    "capital",
                    "incubator",
                    "accelerator",
                    "portfolio",
                    "apply",
                    "program",
                )
            ):
                return False

        return True

    def get_title(self, url):
        try:
            response = requests.get(
                url,
                timeout=min(5, settings.REQUEST_TIMEOUT),
                headers={"User-Agent": "Mozilla/5.0"},
            )
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.text.strip() if soup.title else ""
            description = ""
            meta = soup.find("meta", attrs={"name": "description"})
            if meta:
                description = meta.get("content", "")
            return title, description
        except Exception:
            return "", ""

    def build_search_query(self, intent: dict | None = None, **legacy) -> str:
        """Build a discovery query biased toward official organization websites."""

        intent = intent or {}
        category = intent.get("entity_type") or legacy.get("category") or ""
        country = intent.get("country") or legacy.get("country") or ""
        city = intent.get("city")
        industry = intent.get("industry")
        stage = intent.get("startup_stage") or intent.get("investment_stage")

        parts = []
        if industry:
            parts.append(industry)
        if category and category != "Organization":
            # Pluralize lightly for search engines
            plural_map = {
                "Startup": "startups",
                "Investor": "investors",
                "Accelerator": "accelerators",
                "Incubator": "incubators",
                "Grant": "grants",
                "Program": "startup programs",
            }
            parts.append(plural_map.get(category, category))
        if stage:
            parts.append(stage)
        if city:
            parts.append(city)
        if country:
            parts.append(country)

        parts.append("official website")

        if intent.get("opportunity_intent"):
            parts.append("apply program funding")

        # Soft exclusions for news aggregators
        parts.append("-news -blog -linkedin -wikipedia")

        country_tlds = {
            "Pakistan": "site:.pk",
            "Germany": "site:.de",
            "India": "site:.in",
            "Singapore": "site:.sg",
            "United Kingdom": "site:.uk",
            "France": "site:.fr",
        }
        # Keep TLD bias as a second query signal via appended token
        # (some engines ignore site: when mixed; still helpful when supported)
        if country in country_tlds:
            parts.append(country_tlds[country])

        seen = set()
        cleaned = []
        for part in parts:
            token = str(part).strip()
            if not token:
                continue
            key = token.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(token)

        return " ".join(cleaned).strip() or "startup organization official website"

    def search(
        self,
        query=None,
        category=None,
        country=None,
        intent: dict | None = None,
        max_results: int | None = None,
    ):
        intent = intent or {
            "entity_type": category,
            "country": country,
        }

        search_query = self.build_search_query(
            intent,
            query="",
            category=category,
            country=country,
        )

        limit = max_results or settings.SEARCH_DISCOVERY_LIMIT
        fetch_count = max(limit * 3, 40)

        seen = set()
        results = []

        queries = [search_query]
        # Fallback without site: operator if primary is too narrow
        if "site:" in search_query:
            queries.append(
                search_query.replace("site:.pk", "")
                .replace("site:.de", "")
                .replace("site:.in", "")
                .replace("site:.sg", "")
                .replace("site:.uk", "")
                .replace("site:.fr", "")
                .strip()
            )

        with DDGS() as ddgs:
            for q in queries:
                if len(results) >= limit:
                    break
                for item in ddgs.text(q, max_results=fetch_count):
                    url = item.get("href") or item.get("link")
                    if not url:
                        continue

                    if not self.is_valid(url):
                        continue

                    domain = urlparse(url).netloc.lower()
                    if domain.startswith("www."):
                        domain_key = domain[4:]
                    else:
                        domain_key = domain

                    if domain_key in seen:
                        continue
                    seen.add(domain_key)

                    title = item.get("title", "") or ""
                    description = (
                        item.get("body", "")
                        or item.get("snippet", "")
                        or ""
                    )

                    # Only hit the network for promising candidates
                    if self.is_relevant(title, description, intent, url):
                        page_title, page_description = self.get_title(url)
                        if page_title:
                            title = page_title
                        if page_description:
                            description = page_description

                    if not self.is_relevant(title, description, intent, url):
                        continue

                    results.append(
                        SearchResult(
                            name=title,
                            website=url,
                            description=description,
                            source="Discovery Engine",
                        )
                    )

                    if len(results) >= limit:
                        break

        return results

    def score_candidate(self, candidate: SearchResult, intent: dict) -> float:
        """Relevance score for ranking before deep research."""

        text = f"{candidate.name} {candidate.description or ''}".lower()
        score = 0.0
        parsed = urlparse(candidate.website)
        domain = parsed.netloc.lower()
        path = parsed.path.strip("/")

        entity = (intent.get("entity_type") or "").lower()
        if entity and entity in text:
            score += 30
        elif entity:
            synonyms = {
                "accelerator": ["accelerate", "cohort"],
                "incubator": ["incubate"],
                "investor": ["venture", "capital", "vc"],
                "startup": ["company", "founder", "saas", "product"],
                "grant": ["funding", "award"],
                "program": ["programme", "application"],
            }
            for syn in synonyms.get(entity, []):
                if syn in text:
                    score += 15
                    break

        country = (intent.get("country") or "").lower()
        if country and country in text:
            score += 25

        country_tlds = {
            "pakistan": ".pk",
            "germany": ".de",
            "united kingdom": ".uk",
            "india": ".in",
            "france": ".fr",
            "singapore": ".sg",
        }
        tld = country_tlds.get(country)
        if tld and domain.endswith(tld):
            score += 35

        city = (intent.get("city") or "").lower()
        if city and city in text:
            score += 15

        industry = (intent.get("industry") or "").lower()
        if industry and industry in text:
            score += 20

        stage = (
            intent.get("startup_stage") or intent.get("investment_stage") or ""
        ).lower()
        if stage and stage in text:
            score += 10

        if intent.get("opportunity_intent"):
            if any(
                token in text
                for token in ("apply", "application", "program", "cohort", "grant")
            ):
                score += 15

        if any(
            token in text
            for token in (
                "top 10",
                "best startups",
                "news",
                "blog",
                "article",
                "directory",
                "posted on",
            )
        ):
            score -= 40

        if not path or path.count("/") == 0:
            score += 15
        else:
            score -= 5

        return score
