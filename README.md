#  AI-Powered Global Startup & Investment Discovery Agent

An AI-powered discovery and research platform that allows users to find **startups, investors, accelerators, incubators, and funding/program opportunities globally using natural-language queries**.

Instead of manually searching multiple websites, opening pages, comparing programs, and collecting application or funding information, the system automatically discovers relevant organizations, researches their websites, extracts structured information using AI, identifies available opportunities, and stores the results in PostgreSQL.

---

#  What the System Does

A user can enter a natural-language request such as:

```text
Find startups in Pakistan
```

or:

```text
Find investors in Germany
```

or:

```text
Find accelerators for early-stage startups in Singapore
```

The backend interprets the request and automatically performs the required discovery and research.

### Example workflow

```text
User Query
    ↓
Natural Language Query Parsing
    ↓
Global Web Discovery
    ↓
Candidate Organizations
    ↓
Website Research / Scraping
    ↓
AI Analysis & Structured Extraction
    ↓
Opportunity Extraction
    ↓
Verification
    ↓
PostgreSQL Database
    ↓
Structured Search Results
    ↓
Frontend Dashboard
```

---

# ✨ Key Features

## 🔎 1. Natural-Language Search

Users can search using normal language instead of manually specifying multiple API parameters.

Examples:

```text
Find startups in Pakistan
```

```text
Find investors in Germany
```

```text
Find accelerators in the United States
```

```text
Find incubators in Singapore
```

The `SearchService` interprets the query and extracts information such as:

* Organization category
* Country
* Search keywords

For example:

```text
Find investors in Germany
```

becomes approximately:

```text
Category: Investor
Country: Germany
```

---

# 🌍 2. Global Web Discovery

The system dynamically discovers organizations across the web instead of relying only on a predefined database.

The discovery layer uses **DDGS (DuckDuckGo Search)** to search for relevant websites based on the user's query.

For example:

```text
Investor + Germany
```

can return candidate organization websites.

The system then:

1. Retrieves search results
2. Filters unwanted domains
3. Removes duplicate domains
4. Checks result relevance
5. Passes valid websites to the research pipeline

This allows the system to discover organizations that may not already exist in the database.

---

#  3. Automated Website Research

After discovering an organization, the backend researches its website.

The research service uses:

* `Requests`
* `BeautifulSoup`
* Python regular expressions

It extracts information such as:

* Organization name
* Website
* Description
* Email
* Phone number
* LinkedIn URL

The extracted website information is then passed to the AI analysis layer.

---

#  4. AI-Powered Organization Analysis

The project uses **Google Vertex AI / Gemini** to convert unstructured website information into structured organization data.

The AI can extract:

* Organization name
* Organization type
* Country
* City
* Founding year
* Industries
* Investment stages
* Startup stage
* Ticket size
* Portfolio examples
* Summary
* Confidence score

Example:

```json
{
  "organization_name": "Techstars",
  "organization_type": "Accelerator",
  "country": "United States",
  "city": "Boulder",
  "investment_stage": [
    "Pre-Seed",
    "Seed"
  ],
  "confidence_score": 98
}
```

---

#  5. Opportunity Discovery

A major feature of the system is the ability to identify **actionable programs and opportunities associated with organizations**.

For example, when a user searches:

```text
Find startups and startup programs in Pakistan
```

the system can provide not only information about the organization, but also relevant opportunity information available from its website.

The goal is to answer questions such as:

* How can I apply?
* Who is eligible?
* What funding is available?
* Is equity required?
* What benefits are provided?
* How long is the program?
* What startup stage is targeted?
* What sectors are supported?
* What documents are required?
* What is the selection process?
* Is there mentorship?
* Is there investor access?
* Are grants available?
* Are credits available?
* Is office space provided?
* What is the program status?
* What is the application deadline?

---

# 📋 Opportunity Data Model

Opportunities are stored separately and linked to their organization.

The `Opportunity` model contains fields including:

| Field                  | Purpose                                  |
| ---------------------- | ---------------------------------------- |
| `organization_id`      | Links the opportunity to an organization |
| `application_url`      | Direct application link                  |
| `application_deadline` | Deadline information                     |
| `eligibility`          | Eligibility requirements                 |
| `funding_amount`       | Funding provided                         |
| `funding_currency`     | Funding currency                         |
| `equity_required`      | Equity requirements                      |
| `program_duration`     | Program duration                         |
| `benefits`             | Program benefits                         |
| `application_process`  | How to apply                             |
| `startup_stage`        | Target startup stage                     |
| `investment_stage`     | Investment stage                         |
| `geographic_focus`     | Geographic eligibility                   |
| `sector_focus`         | Supported sectors                        |
| `program_status`       | Current program status                   |
| `mentorship`           | Mentorship information                   |
| `investor_access`      | Investor access                          |
| `network_access`       | Network benefits                         |
| `office_space`         | Office-space availability                |
| `grants`               | Grant information                        |
| `credits`              | Credits offered                          |
| `cohort_information`   | Cohort information                       |
| `required_documents`   | Required application documents           |
| `selection_process`    | Selection process                        |

This allows the frontend to display useful information and direct links rather than only showing a company name and website.

---

# 🔗 Actionable Links

Where the source website provides them, the system can surface relevant links such as:

```text
Organization Website
        ↓
Program / Opportunity
        ↓
Application URL
```

This allows a user to move from **discovery → evaluation → application**.

For example:

```text
Organization: Example Accelerator

Program:
Early Stage Startup Accelerator

Funding:
$100,000

Equity:
5%

Eligibility:
Early-stage technology startups

Benefits:
- Mentorship
- Investor access
- Network access
- Credits

Application:
https://example.com/apply
```

The important principle is that information should be based on the **respective organization's website**, rather than being invented by the AI.

---

#  6. Verification

The system includes verification information so that discovered organizations can be distinguished from less reliable results.

Verification can consider evidence such as:

* Official website availability
* Organization identity on the website
* LinkedIn presence
* AI confidence
* Supporting source information

The database stores:

```text
verification_score
verification_status
verification_source
```

Example:

```json
{
  "verification_score": 95,
  "verification_status": "verified",
  "verification_source": "Official Website, LinkedIn"
}
```

Verification is intended to provide **evidence-based confidence** in the discovered result and is not a guarantee of an organization's legitimacy.

---

#  7. PostgreSQL Database

The backend uses:

* PostgreSQL
* SQLAlchemy ORM
* Alembic migrations

The database contains organization information and associated opportunities.

Conceptually:

```text
Organization
     │
     ├── Organization Information
     │
     ├── Verification Information
     │
     └── Opportunities
             ├── Funding
             ├── Eligibility
             ├── Application
             ├── Benefits
             ├── Program Details
             └── Selection Information
```

The `Opportunity` table is linked to the `Organization` table through:

```text
organization_id
```

---

#  8. Organization Search, Filtering & Sorting

The organizations API supports:

### Pagination

```text
?page=1&page_size=10
```

### Country filtering

```text
?country=Germany
```

### City filtering

```text
?city=Berlin
```

### Organization type

```text
?organization_type=investor
```

### Industry

```text
?industry=technology
```

### Verification status

```text
?verification_status=verified
```

### Search

```text
?search=Techstars
```

### Sorting

```text
?sort_by=verification_score&sort_order=desc
```

This allows the frontend to provide searchable and sortable organization tables.

---

#  9. Statistics

The backend provides statistics for the discovered organizations.

Examples include:

* Total organizations
* Organization types
* Countries
* Cities

Example:

```json
{
  "total_organizations": 25,
  "organization_types": {
    "accelerator": 3,
    "startup": 20,
    "incubator": 1,
    "investor": 1
  },
  "countries": {
    "United States": 3,
    "Germany": 14,
    "Netherlands": 1
  }
}
```

These statistics can be used by the frontend dashboard to create charts and summary cards.

---

#  System Architecture

```text
                         USER
                           │
                           ▼
                 Natural-Language Query
                           │
                           ▼
                    SearchService
                           │
                           ▼
                  Query Interpretation
                           │
                           ▼
                   DiscoveryService
                           │
                           ▼
                         DDGS
                           │
                           ▼
                 Candidate Websites
                           │
                           ▼
                   ResearchService
                           │
                           ▼
             Requests + BeautifulSoup
                           │
                           ▼
                     Website Data
                           │
                           ▼
                      AIService
                           │
                           ▼
                   Vertex AI / Gemini
                           │
                           ▼
               Structured Organization Data
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       Verification              Opportunity
          Service                 Extraction
              │                         │
              └────────────┬────────────┘
                           ▼
                   DatabaseService
                           │
                           ▼
                       PostgreSQL
                           │
                           ▼
                     FastAPI API
                           │
                           ▼
                    Frontend Dashboard
```

---

#  Main Backend Components

## SearchService

The main orchestration layer.

Responsibilities:

* Parse natural-language queries
* Identify organization categories
* Identify countries
* Clean search queries
* Trigger discovery
* Trigger research
* Return structured results

---

## DiscoveryService

Responsible for global web discovery.

Technologies:

* DDGS
* Requests
* BeautifulSoup

Responsibilities:

* Search the web
* Find candidate websites
* Filter unwanted results
* Remove duplicate domains
* Check relevance

---

## ResearchService

Responsible for deeper website research.

Responsibilities:

* Download webpages
* Extract webpage text
* Extract metadata
* Extract emails
* Extract phone numbers
* Extract LinkedIn URLs
* Pass information to AI
* Persist analyzed organizations

---

## AIService

Responsible for AI-powered extraction and enrichment.

Technology:

```text
Google Vertex AI / Gemini
```

It transforms unstructured website information into structured organization and program information.

---

## VerificationService

Responsible for evaluating evidence associated with discovered organizations.

Outputs include:

```text
Verification Score
Verification Status
Verification Source
```

---

## DatabaseService

Responsible for storing analyzed organizations and preventing duplicate organization websites from being inserted.

---

#  Technology Stack

## Backend

* Python
* FastAPI
* Uvicorn

## AI

* Google Vertex AI
* Gemini
* Google Cloud Service Account Authentication

## Web Discovery

* DDGS

## Web Scraping

* Requests
* BeautifulSoup4
* Regular Expressions

## Database

* PostgreSQL
* SQLAlchemy
* Alembic

## Data Validation

* Pydantic

## Development

* Cursor
* Git
* GitHub
* Graphify

---

#  Project Structure

```text
agent-scraper/
│
├── .cursor/
│   └── rules/
│       └── graphify.mdc
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── api/
│   │   ├── search.py
│   │   ├── research.py
│   │   ├── organizations.py
│   │   └── statistics.py
│   │
│   ├── database/
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── base_model.py
│   │   ├── enums.py
│   │   ├── organization.py
│   │   ├── investors.py
│   │   └── opportunity.py
│   │
│   ├── schemas/
│   │   └── ...
│   │
│   ├── services/
│   │   ├── search_service.py
│   │   ├── discovery_service.py
│   │   ├── research_service.py
│   │   ├── ai_service.py
│   │   ├── verification_service.py
│   │   └── database_service.py
│   │
│   ├── config.py
│   └── main.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🔌 API

The backend is built using FastAPI and provides REST endpoints for the frontend.

## Search

```text
POST /search/
```

Example:

```json
{
  "query": "Find investors in Germany"
}
```

The search endpoint performs the discovery and research workflow.

---

## Research

```text
POST /research/
```

Example:

```json
{
  "url": "https://www.techstars.com"
}
```

This endpoint performs detailed research on a specific website.

---

## Organizations

```text
GET /organizations/
```

Supports:

* Pagination
* Search
* Country filtering
* City filtering
* Organization-type filtering
* Industry filtering
* Verification filtering
* Sorting

---

## Statistics

```text
GET /organizations/stats
```

Provides aggregated organization statistics for the frontend dashboard.

---

#  Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd agent-scraper
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file containing the required configuration:

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=your-location
GOOGLE_APPLICATION_CREDENTIALS=path-to-service-account.json
VERTEX_MODEL=your-model
DATABASE_URL=your-postgresql-connection-string
```

**Never commit `.env` files, API keys, or service-account credentials to GitHub.**

---

#  Running the Backend

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

#  Example End-to-End Scenario

### User

```text
Find startups in Pakistan
```

### Step 1 — Query Parsing

The system identifies:

```text
Category: Startup
Country: Pakistan
```

### Step 2 — Discovery

DDGS searches the web for relevant startup organizations.

### Step 3 — Website Research

The system visits discovered websites and extracts available information.

### Step 4 — AI Analysis

Vertex AI structures the organization information.

### Step 5 — Opportunity Extraction

Where applicable, the system identifies program/opportunity information such as:

```text
Funding
Eligibility
Application URL
Application Process
Equity
Benefits
Startup Stage
Investment Stage
Program Duration
Mentorship
Investor Access
Network Access
Grants
Credits
Required Documents
Selection Process
```

### Step 6 — Verification

The system evaluates available evidence and records the verification status and score.

### Step 7 — Database

Organization and opportunity information is stored in PostgreSQL.

### Step 8 — Frontend

The frontend can display:

```text
Startup / Organization
        │
        ├── Website
        ├── Location
        ├── Industry
        ├── Description
        ├── Verification
        │
        └── Opportunities
              ├── Funding
              ├── Eligibility
              ├── Benefits
              ├── Application Link
              ├── Deadline
              └── Program Details
```

This transforms the system from a simple organization search tool into an **actionable discovery platform**.

---

#  Project Objective

The primary objective is to automate the process of discovering and researching organizations and opportunities within the global startup and investment ecosystem.

Traditional workflow:

```text
Search the web
     ↓
Open multiple websites
     ↓
Find organization information
     ↓
Find programs
     ↓
Find funding information
     ↓
Find eligibility
     ↓
Find application links
     ↓
Verify information
     ↓
Collect everything manually
```

Automated workflow:

```text
Natural-Language Request
          ↓
Global Discovery
          ↓
Website Research
          ↓
AI Extraction
          ↓
Opportunity Extraction
          ↓
Verification
          ↓
Structured Database
          ↓
Actionable Results
```

---

#  Future Improvements

Potential improvements include:

* Google Programmable Search / Google Search integration
* More independent verification sources
* Advanced semantic query understanding
* Opportunity-specific search
* Funding and investment filters
* Industry and sector filters
* Geographic eligibility filters
* Advanced frontend dashboard
* Background processing for large searches
* Caching
* Scheduled data refresh
* Better duplicate detection
* Authentication and user accounts
* Cloud deployment
* More verification providers

---

# 📌 Project Status

### Backend

* ✅ Natural-language search
* ✅ Global web discovery
* ✅ DDGS integration
* ✅ Website scraping
* ✅ AI-powered organization analysis
* ✅ Organization enrichment
* ✅ Verification system
* ✅ PostgreSQL database
* ✅ SQLAlchemy ORM
* ✅ Alembic migrations
* ✅ Organization deduplication
* ✅ Pagination
* ✅ Sorting
* ✅ Filtering
* ✅ Organization search
* ✅ Statistics API
* ✅ Opportunity data model
* ✅ Program/application information support
* ✅ FastAPI REST API
* ✅ Swagger API documentation
* ✅ Graphify codebase knowledge graph

### Frontend

The frontend consumes the backend REST APIs and provides the user-facing search experience, organization results, opportunity information, filters, and dashboard.

---

#  System Overview

The project combines **web discovery, web scraping, AI-powered information extraction, verification, database persistence, and opportunity discovery** into one automated backend pipeline.

The core idea is:

> **Give the system a goal in natural language, and let the backend discover, research, structure, verify, and return actionable information from relevant organizations and their programs.**
