from app.services.discovery_service import DiscoveryService
from app.services.research_service import ResearchService


class EnrichmentService:

    def __init__(self):
        self.discovery = DiscoveryService()
        self.research = ResearchService()

    def enrich(
        self,
        query: str,
        category: str = "Investor",
        country: str = ""
    ):

        websites = self.discovery.search(
            query=query,
            category=category,
            country=country,
        )

        results = []

        for item in websites:

            try:

                data = self.research.crawl(
                    item.website
                )

                results.append(data)

            except Exception as e:

                results.append({

                    "website": item.website,

                    "error": str(e)

                })

        return results