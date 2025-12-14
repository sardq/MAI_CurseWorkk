from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserDB(Base):
    """Модель SQLAlchemy для таблицы User"""
    tablename = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(String(20), default="user") # 'admin', 'moderator', 'user'
    is_active = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

class KnowledgeDB(Base):
    """Модель KnowledgeBaseEntry (должна быть идентична той, что в knowledge_service)"""
    tablename = "knowledge_base_entry"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    correction = Column(Text, nullable=False)
    severity_level = Column(String(50), nullable=False)


class UserCreate(BaseModel):
    """Входная модель для регистрации и создания пользователей"""
    username: str
    password: str
    email: Optional[str] = None
    role: str = "user"

class UserResponse(BaseModel):
    """Модель для вывода данных пользователя (без пароля)"""
    id: int
    username: str
    email: Optional[str]
    role: str
    is_active: bool
    
    class Config:
        orm_mode = True

class KnowledgeEntryUpdate(BaseModel):
    """Модель для обновления записи в Базе Знаний"""
    description: Optional[str] = None
    correction: Optional[str] = None
    severity_level: Optional[str] = None