from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from app.schemas.search import SearchResult
from app.services.filters import BAD_DOMAINS


class DiscoveryService:

    def is_valid(self, url: str):

        domain = urlparse(url).netloc.lower()

        for bad in BAD_DOMAINS:
            if bad in domain:
                return False

        return True

    def get_title(self, url):

        try:

            html = requests.get(
                url,
                timeout=5,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
            )

            soup = BeautifulSoup(html.text, "html.parser")

            title = soup.title.text.strip() if soup.title else ""

            meta = soup.find(
                "meta",
                attrs={"name": "description"},
            )

            description = ""

            if meta:
                description = meta.get("content", "")

            return title, description

        except Exception:

            return "", ""

    def search(self, query, category, country):

        if country:
            query = f"{query} {country}"

        search_query = f"{category} {query}"

        seen = set()

        results = []

        with DDGS() as ddgs:

            for item in ddgs.text(search_query, max_results=30):

                url = item["href"]

                if not self.is_valid(url):
                    continue

                domain = urlparse(url).netloc

                if domain in seen:
                    continue

                seen.add(domain)

                title, description = self.get_title(url)

                if not title:
                    title = item.get("title", "")

                if not description:
                    description = item.get("body", "")

                results.append(

                    SearchResult(
                        name=title,
                        website=url,
                        description=description,
                        source="Discovery Engine",
                    )

                )

        return results