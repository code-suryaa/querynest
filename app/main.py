
from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.documents import router as documents_router

app = FastAPI(
    title="QueryNest API",
    description="AI-powered Document Intelligence Platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to QueryNest API",
        "status": "running"
    }


app.include_router(health_router)
app.include_router(
    documents_router,
    prefix="/documents",
    tags=["Documents"]
)
