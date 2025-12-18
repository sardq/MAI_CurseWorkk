from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from typing import List
from src.database import get_db_session, init_db
from src.models import (
    LookupRequest, UserDB, UserCreate, UserResponse,
    KnowledgeDB, KnowledgeEntryUpdate, KnowledgeResponse
)

app = FastAPI(title="Administration Service", version="1.0.0")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@app.on_event("startup")
async def startup_event():
    await init_db() 
    pass


@app.post("/admin/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        role=user.role
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Пользователь с таким именем или email уже существует.")

@app.get("/admin/users/", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(UserDB))
    return result.scalars().all()


@app.get("/admin/knowledge/", response_model=List[KnowledgeResponse])
async def list_knowledge_entries(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(KnowledgeDB).order_by(KnowledgeDB.id))
    return result.scalars().all()

@app.patch("/admin/knowledge/{entry_id}", response_model=KnowledgeResponse)
async def update_knowledge_entry(
    entry_id: int, 
    update_data: KnowledgeEntryUpdate, 
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(select(KnowledgeDB).where(KnowledgeDB.id == entry_id))
    entry = result.scalars().first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена.")

    update_data_dict = update_data.dict(exclude_unset=True)
    for key, value in update_data_dict.items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry)
    return entry

@app.post("/knowledge/lookup/", response_model=KnowledgeResponse)
async def lookup_knowledge(
    request: LookupRequest, 
    db: AsyncSession = Depends(get_db_session)
):
    query = select(KnowledgeDB).where(KnowledgeDB.error_type.ilike(request.error_type))
    result = await db.execute(query)
    entries = result.scalars().all()
    
    if not entries:
        raise HTTPException(status_code=404, detail="No entries for this error type")

    best_match = None
    
    for entry in entries:
        if entry.keyword_pattern and entry.keyword_pattern.lower() in request.error_message.lower():
            return entry
        
        if not entry.keyword_pattern or entry.keyword_pattern == "":
            best_match = entry
            
    if best_match:
        return best_match
        
    raise HTTPException(status_code=404, detail="Specific recommendation not found")

@app.delete("/admin/knowledge/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_entry(entry_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(KnowledgeDB).where(KnowledgeDB.id == entry_id))
    entry = result.scalars().first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена.")
        
    await db.delete(entry)
    await db.commit()
    return

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "AdminService"}
