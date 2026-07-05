from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import redis.asyncio as redis
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_timeout=5,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={
        "server_settings": {
            "statement_timeout": "5000",       # kill any single query that runs >5s at the DB level
            "idle_in_transaction_session_timeout": "10000",  # kill stuck open transactions
        },
        "timeout": 5,   # asyncpg-level connection acquisition timeout
    },
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()

redis_pool = redis.ConnectionPool.from_url(
    REDIS_URL,
    decode_responses=True,
    max_connections=50,
    socket_connect_timeout=2,   # fail fast if Redis is unreachable
    socket_timeout=2,           # fail fast if a Redis command hangs
    health_check_interval=30,   # proactively detects dead connections in the pool
    retry_on_timeout=True,      # one automatic retry on transient timeout
)
redis_client = redis.Redis(connection_pool=redis_pool)

async def get_db():
    async with SessionLocal() as db:
        yield db