from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from src.database import get_db_session, init_db
from src.models import KnowledgeDB, KnowledgeBaseEntryCreate, LookupResult, KnowledgeBaseEntryResponse

app = FastAPI(title="Knowledge Base Service (PostgreSQL)", version="3.0.0")

@app.on_event("startup")
async def startup_event():
    """Выполняется при запуске: инициализация подключения и, возможно, таблиц."""
    # В боевом режиме эту функцию лучше отключить и использовать миграции БД
    # await init_db() 
    pass

# --- API Эндпоинты ---

@app.post("/knowledge/add", response_model=KnowledgeBaseEntryResponse, status_code=status.HTTP_201_CREATED)
async def add_knowledge_entry(
    entry: KnowledgeBaseEntryCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Добавляет новую запись в базу знаний."""
    db_entry = KnowledgeDB(**entry.dict())
    db.add(db_entry)
    
    try:
        await db.commit()
        await db.refresh(db_entry)
        return db_entry
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Шаблон ошибки '{entry.pattern}' уже существует."
        )

@app.get("/knowledge/lookup/{error_pattern}", response_model=LookupResult)
async def lookup_correction(
    error_pattern: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Возвращает рекомендацию и уровень серьезности по коду ошибки."""
    
    result = await db.execute(
        select(KnowledgeDB).where(KnowledgeDB.pattern == error_pattern)
    )
    entry = result.scalars().first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Шаблон ошибки '{error_pattern}' не найден в Базе Знаний."
        )
        
    return LookupResult(
        correction=entry.correction,
        description=entry.description,
        severity_level=entry.severity_level
    )

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "KnowledgeService", "database_type": "PostgreSQL Async"}