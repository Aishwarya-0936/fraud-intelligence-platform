from fastapi import FastAPI
from app.routers import router
from app.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fraud Intelligence Platform",
    description="Real-time transaction monitoring and fraud risk analysis",
    version="1.0.0"
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "running"}