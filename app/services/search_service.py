import re

from app.services.discovery_service import DiscoveryService
from app.services.research_service import ResearchService


class SearchService:

    def __init__(self):
        self.discovery = DiscoveryService()
        self.research = ResearchService()

    def parse_query(self, query: str):

        text = query.strip()

        lower = text.lower()


        if "investor" in lower or "investors" in lower:
            category = "Investor"

        elif "startup" in lower or "startups" in lower:
            category = "Startup"

        elif "incubator" in lower or "incubators" in lower:
            category = "Incubator"

        elif "accelerator" in lower or "accelerators" in lower:
            category = "Accelerator"

        elif "angel" in lower:
            category = "Angel"

        else:
            category = "Organization"

        countries = [
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
        ]

        country = ""

        for item in countries:

            if item.lower() in lower:
                country = item
                break

        clean_query = text

        clean_query = re.sub(
            r"\b(find|show|search|look for|get|give me)\b",
            "",
            clean_query,
            flags=re.IGNORECASE,
        )

        clean_query = re.sub(
            r"\b(investor|investors|startup|startups|"
            r"incubator|incubators|accelerator|accelerators|angel)\b",
            "",
            clean_query,
            flags=re.IGNORECASE,
        )

        if country:
            clean_query = re.sub(
                rf"\b{re.escape(country)}\b",
                "",
                clean_query,
                flags=re.IGNORECASE,
            )

        clean_query = re.sub(
            r"\s+",
            " ",
            clean_query,
        ).strip()

        if not clean_query:
            clean_query = category

        return {
            "query": clean_query,
            "category": category,
            "country": country,
        }

    def search(self, user_query: str):


        parsed = self.parse_query(user_query)

        query = parsed["query"]
        category = parsed["category"]
        country = parsed["country"]


        discovered = self.discovery.search(
            query=query,
            category=category,
            country=country,
        )


        results = []

        for item in discovered:

            try:

                researched = self.research.crawl(
                    item.website
                )

                results.append(
                    researched
                )

            except Exception as e:

                results.append(
                    {
                        "raw": {
                            "name": item.name,
                            "website": item.website,
                            "description": item.description,
                        },
                        "ai_analysis": {
                            "error": str(e)
                        },
                    }
                )

        return {
            "count": len(results),
            "results": results,
        }