import re
import requests

from bs4 import BeautifulSoup

from app.services.ai_service import AIService
from app.services.database_service import DatabaseService


database = DatabaseService()
ai = AIService()

EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
PHONE_REGEX = r"\+?[1-9]\d{7,14}"


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

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        text = soup.get_text(
            " ",
            strip=True
        )

        
        title = ""

        if soup.title:
            title = soup.title.text.strip()

        description = ""

        meta = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if meta:
            description = meta.get(
                "content",
                ""
            )

       
        emails = re.findall(
            EMAIL_REGEX,
            text
        )

        
        phones = re.findall(
            PHONE_REGEX,
            text
        )

        
        linkedin = ""

        for link in soup.find_all(
            "a",
            href=True
        ):

            href = link["href"]

            if "linkedin.com" in href:

                linkedin = href

                break

        
        website_data = {

            "name": title,

            "website": url,

            "email": (
                emails[0]
                if emails
                else None
            ),

            "phone": (
                phones[0]
                if phones
                else None
            ),

            "linkedin": linkedin,

            "description": description,
        }

        
        analysis = ai.analyze(
            website_data
        )

        
        if response.status_code == 200 and (
            title or description or len(text) > 100
        ):

            analysis["verification_status"] = "verified"

            analysis["verification_source"] = url

        else:

            analysis["verification_status"] = "unverified"

            analysis["verification_source"] = ""

       
        saved_org = database.save(
            analysis
        )

        return {

            "raw": website_data,

            "ai_analysis": analysis,

            "database": {

                "saved": True,

                "id": str(saved_org.id),

                "verification_status": (
                    saved_org.verification_status
                ),

                "verification_source": (
                    saved_org.verification_source
                ),
            },
        }