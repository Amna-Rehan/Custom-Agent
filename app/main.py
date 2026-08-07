from fastapi import FastAPI
from app.api.discover import router as discover_router
from app.database.init_db import init_database

app = FastAPI(
    title="Global Intelligence Platform",
    version="1.0.0",
)

from app.api.search import router as search_router
from app.api.enrich import router as enrich_router
from app.api.organizations import router as organization_router
from app.api.dashboard import router as dashboard_router

app.include_router(dashboard_router)
app.include_router(organization_router)
app.include_router(enrich_router)
app.include_router(search_router)
app.include_router(discover_router)

@app.on_event("startup")
def startup():
    init_database()


@app.get("/")
def root():
    return {
        "status": "running",
        "platform": "Global Intelligence Platform",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}