from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from src.models import KnowledgeResponse
from src.database import get_db_session, init_db
from src.models import KnowledgeDB, KnowledgeBaseEntryCreate, LookupResult, KnowledgeBaseEntryResponse

app = FastAPI(title="Knowledge Base Service (PostgreSQL)", version="3.0.0")

@app.on_event("startup")
async def startup_event():
    # В боевом режиме эту функцию лучше отключить и использовать миграции БД
    # await init_db() 
    pass


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

app.post("/knowledge/lookup/", response_model=KnowledgeResponse)
async def lookup_knowledge(
    error_type: str, 
    error_message: str, 
    db: AsyncSession = Depends(get_db_session)
):
    """
    Ищет рекомендацию. Сначала по точному типу, затем фильтрует по вхождению паттерна в сообщение.
    """
    # 1. Ищем все записи с таким типом ошибки
    query = select(KnowledgeDB).where(KnowledgeDB.error_type == error_type)
    result = await db.execute(query)
    entries = result.scalars().all()
    
    # 2. Фильтрация на уровне Python (простейшая "ассоциативность")
    # Пытаемся найти запись, чей keyword_pattern содержится в тексте ошибки
    best_match = None
    
    for entry in entries:
        if entry.keyword_pattern and entry.keyword_pattern.lower() in error_message.lower():
            return entry # Нашли специфичный совет
        
        # Сохраним "общий" совет (где паттерн пустой) на случай, если специфичный не найдем
        if not entry.keyword_pattern:
            best_match = entry
            
    if best_match:
        return best_match
        
    raise HTTPException(status_code=404, detail="Recommendation not found")

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "KnowledgeService", "database_type": "PostgreSQL Async"}