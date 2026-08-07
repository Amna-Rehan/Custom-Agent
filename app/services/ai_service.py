import json

import vertexai
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

from app.config import settings

credentials = service_account.Credentials.from_service_account_file(
    settings.GOOGLE_APPLICATION_CREDENTIALS
)

vertexai.init(
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION,
    credentials=credentials,
)


class AIService:

    def __init__(self):
        self.model = GenerativeModel(settings.VERTEX_MODEL)

    def analyze(self, website_data: dict):

        website = website_data.get("website")
        name = website_data.get("name")

        prompt = f"""
You are a senior venture capital and startup ecosystem analyst.

Analyze the organization using ONLY the supplied website data.

Do NOT invent facts that are not supported by the website data.

Website Data:

{json.dumps(website_data, indent=2)}

Return ONLY valid JSON in exactly this structure:

{{
  "organization_name": "",
  "organization_type": "",
  "country": "",
  "city": "",
  "website": "",
  "email": "",
  "phone": "",
  "linkedin": "",
  "founding_year": "",
  "industries": [],
  "investment_stage": [],
  "startup_stage": "",
  "ticket_size": "",
  "portfolio_examples": [],
  "summary": "",
  "confidence_score": 0,
  "verification_status": "",
  "verification_source": ""
}}

IMPORTANT VERIFICATION RULES:

1. The supplied website is the primary verification source.

2. If the website was successfully fetched and contains meaningful
   organization information, set:

   "verification_status": "verified"

3. If the supplied website does not contain enough information to
   establish that the organization is legitimate, set:

   "verification_status": "unverified"

4. If verified, set:

   "verification_source": "{website}"

5. If unverified, set:

   "verification_source": ""

6. Do not mark an organization as verified simply because you know
   the organization from your training data.

7. confidence_score must be between 0 and 100.

Organization Type MUST be exactly one of:

Investor
Startup
Incubator
Accelerator

Return ONLY JSON.
"""

        try:

            response = self.model.generate_content(prompt)

            text = response.text.strip()

            if text.startswith("```json"):
                text = (
                    text.replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            elif text.startswith("```"):
                text = (
                    text.replace("```", "")
                    .strip()
                )

            analysis = json.loads(text)

            
            analysis.setdefault(
                "organization_name",
                website_data.get("name")
            )

            analysis.setdefault(
                "website",
                website
            )

            analysis.setdefault(
                "email",
                website_data.get("email")
            )

            analysis.setdefault(
                "phone",
                website_data.get("phone")
            )

            analysis.setdefault(
                "linkedin",
                website_data.get("linkedin")
            )

            analysis.setdefault(
                "confidence_score",
                0
            )

            analysis.setdefault(
                "verification_status",
                "unverified"
            )

            analysis.setdefault(
                "verification_source",
                ""
            )

            if analysis["verification_status"] == "verified":
                analysis["verification_source"] = website

            else:
                analysis["verification_status"] = "unverified"
                analysis["verification_source"] = ""

            return analysis

        except Exception as e:

            print("Vertex AI Error:", e)

            return {
                "organization_name": website_data.get("name"),
                "organization_type": "Startup",
                "country": "",
                "city": "",
                "website": website,
                "email": website_data.get("email"),
                "phone": website_data.get("phone"),
                "linkedin": website_data.get("linkedin"),
                "founding_year": "",
                "industries": [],
                "investment_stage": [],
                "startup_stage": "",
                "ticket_size": "",
                "portfolio_examples": [],
                "summary": website_data.get("description"),
                "confidence_score": 0,

                # Failed AI analysis should NEVER be called verified
                "verification_status": "unverified",
                "verification_source": "",

                "error": str(e),
            }