from urllib.parse import urlparse

import requests


class VerificationService:

    def verify(
        self,
        url: str,
        title: str,
        description: str,
        linkedin: str,
    ):

        score = 0
        reasons = []

        website_accessible = False

        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=10,
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
            score += 20
            reasons.append("Website has a valid title")


        if description and len(description.strip()) > 20:
            score += 10
            reasons.append("Website contains organization description")


        if linkedin and "linkedin.com" in linkedin.lower():
            score += 15
            reasons.append("LinkedIn organization profile found")


        if title and len(title.strip()) > 3:
            score += 15
            reasons.append("Organization identity found on website")


        if score >= 80:
            status = "verified"
        elif score >= 50:
            status = "partially_verified"
        else:
            status = "unverified"

        return {
            "score": min(score, 100),
            "status": status,
            "source": url,
            "reasons": reasons,
        }