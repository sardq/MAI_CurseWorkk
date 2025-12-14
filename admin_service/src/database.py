import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base 

from src.models import Base 


DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "postgres_db") 
DB_NAME = os.getenv("DB_NAME", "analysis_db")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(
    DATABASE_URL, 
    echo=False 
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession, 
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def init_db():
    """
    Создает таблицы в базе данных на основе моделей, если они не существуют.
    Используется только для первого запуска или тестирования.
    В боевой среде для этого обычно используется Alembic.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session():
    """
    Функция-генератор, используемая как зависимость (Dependency Injection) в FastAPI.
    Обеспечивает создание, использование и корректное закрытие сессии БД.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            pass