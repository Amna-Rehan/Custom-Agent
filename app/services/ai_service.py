import json

import vertexai
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

from app.config import settings


# Load service account credentials
credentials = service_account.Credentials.from_service_account_file(
    settings.GOOGLE_APPLICATION_CREDENTIALS
)

# Initialize Vertex AI
vertexai.init(
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION,
    credentials=credentials,
)


class AIService:

    def __init__(self):
        self.model = GenerativeModel(settings.VERTEX_MODEL)

    def analyze(self, website_data: dict):

        prompt = f"""
You are a senior venture capital and startup ecosystem analyst.

Analyze the organization below.

Return ONLY valid JSON.

Website Data:

{json.dumps(website_data, indent=2)}

Required JSON:

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
  "confidence_score": 95
}}

Organization Type must be one of:

Investor
Startup
Incubator
Accelerator
Angel
Venture Capital
Government
University
Corporate
Other

Return ONLY JSON.
"""

        try:
            response = self.model.generate_content(prompt)

            text = response.text.strip()

            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()

            return json.loads(text)

        except Exception as e:

            print("Vertex AI Error:", e)

            return {
                "organization_name": website_data.get("name"),
                "organization_type": "Unknown",
                "country": "",
                "city": "",
                "website": website_data.get("website"),
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
                "error": str(e)
            }