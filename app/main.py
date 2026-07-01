from fastapi import FastAPI
from app.routers import router, login_router
from app.db import engine, Base
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# LangSmith observability — traces every LangChain/LangGraph call automatically
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "fraud-intelligence-platform")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all DB tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Fraud Intelligence Platform",
    description="Real-time transaction monitoring and fraud risk analysis using Agentic AI, LangGraph, RAG, and multi-agent orchestration",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(router)
app.include_router(login_router)

@app.get("/health")
async def health_check():
    return {
        "status": "running",
        "version": "2.0.0",
        "ai_stack": ["LangChain", "LangGraph", "LangSmith", "Qdrant", "Claude API", "OpenAI API"]
    }