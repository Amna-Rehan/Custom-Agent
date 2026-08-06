from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from app.schemas.discover import SearchResult
from app.services.filters import BAD_DOMAINS


class DiscoveryService:

    def is_valid(self, url: str):

        domain = urlparse(url).netloc.lower()

        for bad in BAD_DOMAINS:
            if bad in domain:
                return False

        return True

    def is_relevant(self, title: str, description: str):

        text = f"{title} {description}".lower()

        blocked = [
            "checking your browser",
            "attention required",
            "just a moment",
            "cloudflare",
            "captcha",
            "cookie",
            "sign in",
            "log in",
            "privacy policy",
            "terms of use",
            "404",
            "page not found",
            "news",
            "blog",
            "article",
            "broker",
            "stock",
            "crypto",
            "forex",
        ]

        for word in blocked:
            if word in text:
                return False

        return True

    def get_title(self, url):

        try:

            response = requests.get(
                url,
                timeout=5,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            title = soup.title.text.strip() if soup.title else ""

            description = ""

            meta = soup.find(
                "meta",
                attrs={"name": "description"},
            )

            if meta:
                description = meta.get("content", "")

            return title, description

        except Exception:

            return "", ""

    def search(self, query, category, country=None):

        if country:
            query = f"{query} {country}"

        search_query = f"{category} {query}"

        seen = set()

        results = []

        with DDGS() as ddgs:

            for item in ddgs.text(search_query, max_results=50):

                url = item["href"]

                if not self.is_valid(url):
                    continue

                domain = urlparse(url).netloc.lower()

                if domain in seen:
                    continue

                seen.add(domain)

                title, description = self.get_title(url)

                if not title:
                    title = item.get("title", "")

                if not description:
                    description = item.get("body", "")

                if not self.is_relevant(title, description):
                    continue

                results.append(

                    SearchResult(
                        name=title,
                        website=url,
                        description=description,
                        source="Discovery Engine",
                    )

                )

        return results