import re
import requests

from bs4 import BeautifulSoup
from app.services.ai_service import AIService

ai = AIService()
EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
PHONE_REGEX = r"\+?\d[\d\s().-]{8,}"


class ResearchService:

    def crawl(self, url: str):

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        text = soup.get_text(" ", strip=True)

        title = ""

        if soup.title:
            title = soup.title.text.strip()

        description = ""

        meta = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if meta:
            description = meta.get("content", "")

        emails = re.findall(
            EMAIL_REGEX,
            text,
        )

        phones = re.findall(
            PHONE_REGEX,
            text,
        )

        linkedin = ""

        for link in soup.find_all("a", href=True):

            href = link["href"]

            if "linkedin.com" in href:
                linkedin = href
                break

        website = {

           "name": title,
 
           "website": url,

           "email": emails[0] if emails else None,

           "phone": phones[0] if phones else None,

           "linkedin": linkedin,

           "description": description,

        }

        analysis = ai.analyze(website)

        return {

           "raw": website,
 
           "ai_analysis": analysis

        }