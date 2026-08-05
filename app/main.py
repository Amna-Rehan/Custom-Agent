from fastapi import FastAPI

from app.database.init_db import init_database

app = FastAPI(
    title="Global Intelligence Platform",
    version="1.0.0",
)

from app.api.search import router as search_router

app.include_router(search_router)


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