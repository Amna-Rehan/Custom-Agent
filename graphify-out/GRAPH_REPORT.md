# Graph Report - .  (2026-08-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 97 nodes · 192 edges · 10 communities (9 shown, 1 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `74538d4c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- organization.py
- DiscoveryService
- BaseModel
- models/__init__.py
- research_service.py
- main.py
- api/search.py
- VerificationService

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 21 edges
2. `DiscoveryService` - 12 edges
3. `ResearchService` - 11 edges
4. `Organization` - 10 edges
5. `Base` - 8 edges
6. `OrganizationType` - 8 edges
7. `SearchService` - 7 edges
8. `DatabaseService` - 6 edges
9. `JobStatus` - 5 edges
10. `ResearchJob` - 5 edges

## Surprising Connections (you probably didn't know these)
- `BaseModel` --uses--> `Base`  [INFERRED]
  app/models/base_model.py → app/database/base.py
- `Organization` --uses--> `BaseModel`  [INFERRED]
  app/models/organization.py → app/models/base_model.py
- `ResearchJob` --uses--> `BaseModel`  [INFERRED]
  app/models/research_job.py → app/models/base_model.py
- `Source` --uses--> `BaseModel`  [INFERRED]
  app/models/source.py → app/models/base_model.py
- `User` --uses--> `BaseModel`  [INFERRED]
  app/models/user.py → app/models/base_model.py

## Import Cycles
- None detected.

## Communities (10 total, 1 thin omitted)

### Community 0 - "organization.py"
Cohesion: 0.17
Nodes (13): get_dashboard_stats(), get, export_csv(), get, get_organizations(), get, JobStatus, OrganizationType (+5 more)

### Community 1 - "DiscoveryService"
Cohesion: 0.20
Nodes (5): SearchResult, DiscoveryService, EnrichmentService, ResearchService, SearchService

### Community 2 - "BaseModel"
Cohesion: 0.21
Nodes (11): post, research(), BaseModel, DiscoverRequest, DiscoverResponse, EnrichRequest, EnrichResponse, AIAnalysis (+3 more)

### Community 3 - "models/__init__.py"
Cohesion: 0.28
Nodes (5): Base, Investor, Source, User, DeclarativeBase

### Community 4 - "research_service.py"
Cohesion: 0.29
Nodes (3): Settings, AIService, BaseSettings

### Community 5 - "main.py"
Cohesion: 0.36
Nodes (6): init_database(), health(), get, root(), startup(), on_event

### Community 6 - "api/search.py"
Cohesion: 0.53
Nodes (4): post, search(), SearchRequest, SearchResponse

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseModel` connect `BaseModel` to `organization.py`, `DiscoveryService`, `models/__init__.py`, `api/search.py`?**
  _High betweenness centrality (0.311) - this node is a cross-community bridge._
- **Why does `ResearchService` connect `DiscoveryService` to `organization.py`, `BaseModel`, `research_service.py`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `Organization` connect `organization.py` to `BaseModel`, `models/__init__.py`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `BaseModel` (e.g. with `Base` and `Organization`) actually correct?**
  _`BaseModel` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `DiscoveryService` (e.g. with `SearchResult` and `EnrichmentService`) actually correct?**
  _`DiscoveryService` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `ResearchService` (e.g. with `EnrichmentService` and `AIService`) actually correct?**
  _`ResearchService` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Organization` (e.g. with `BaseModel` and `OrganizationType`) actually correct?**
  _`Organization` has 3 INFERRED edges - model-reasoned connections that need verification._