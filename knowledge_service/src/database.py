from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from src.models import Base

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")  
DB_HOST = os.getenv("DB_HOST", "postgres_db")
DB_NAME = os.getenv("DB_NAME", "analysis_db")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    """Создает таблицы в БД, если они не существуют (только для разработки)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session():
    """Dependency Injection для FastAPI: возвращает сессию и закрывает ее"""
    async with AsyncSessionLocal() as session:
        yield session