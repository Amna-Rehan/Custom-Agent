from fastapi import FastAPI
from app.database.init_db import init_database

app = FastAPI(
    title="Global Intelligence Platform",
    version="1.0.0",
)

from app.api.research import router as research_router
from app.api.export import router as export_router
from app.api.organizations import router as organization_router
from app.api.dashboard import router as dashboard_router
from app.api.search import router as search_router
app.include_router(search_router)
app.include_router(dashboard_router)
app.include_router(organization_router)
app.include_router(research_router)
app.include_router(export_router)
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