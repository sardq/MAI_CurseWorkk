from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from pydantic import BaseModel

from src.auth import ALGORITHM, SECRET_KEY
from src.database import get_db_session, init_db
from src.models import KnowledgeCreate, KnowledgeResponse, KnowledgeUpdate, UserCreate, KnowledgeDB, UserDB, UserResponse
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

app = FastAPI(title="Administration Service", version="1.0.0")
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(UserDB).where(UserDB.id == user_id))
    user = result.scalar()

    if not user or not user.is_active:
        raise HTTPException(status_code=401)

    return user
def require_admin(current_user: UserDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user


def require_operator_or_admin(current_user: UserDB = Depends(get_current_user)):
    if current_user.role not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Operator or Admin only")
    return current_user

# --- Эндпоинты управления ПОЛЬЗОВАТЕЛЯМИ (Admin) ---

@app.get("/admin/users/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db_session),
    _: UserDB = Depends(require_admin)
):
    result = await db.execute(select(UserDB).order_by(UserDB.id))
    return result.scalars().all()


@app.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: UserDB = Depends(require_admin)
):
    result = await db.execute(select(UserDB).where(UserDB.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(db_user)
    await db.commit()

    return None

    


@app.get("/admin/knowledge/", response_model=List[KnowledgeResponse])
async def list_knowledge_entries(
    db: AsyncSession = Depends(get_db_session),
    _: UserDB = Depends(require_operator_or_admin)
):
    result = await db.execute(select(KnowledgeDB).order_by(KnowledgeDB.id.desc()))
    return result.scalars().all()


@app.post("/admin/knowledge/", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_entry(
    entry: KnowledgeCreate,
    db: AsyncSession = Depends(get_db_session),
    _: UserDB = Depends(require_operator_or_admin)
):
    db_entry = KnowledgeDB(**entry.dict())
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry


@app.patch("/admin/knowledge/{entry_id}", response_model=KnowledgeResponse)
async def update_knowledge_entry(
    entry_id: int,
    update_data: KnowledgeUpdate,
    db: AsyncSession = Depends(get_db_session),
    _: UserDB = Depends(require_operator_or_admin)
):
    result = await db.execute(select(KnowledgeDB).where(KnowledgeDB.id == entry_id))
    db_entry = result.scalars().first()

    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(db_entry, field, value)

    await db.commit()
    await db.refresh(db_entry)
    return db_entry

@app.delete("/admin/knowledge/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_entry(entry_id: int, db: AsyncSession = Depends(get_db_session)):
    """Удаление записи"""
    result = await db.execute(select(KnowledgeDB).where(KnowledgeDB.id == entry_id))
    db_entry = result.scalars().first()
    
    if not db_entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")
        
    await db.delete(db_entry)
    await db.commit()
    return

@app.on_event("startup")
async def startup_event():
    await init_db()