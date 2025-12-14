from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models import Base

DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "db_host" 
DB_NAME = "analysis_db"
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

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