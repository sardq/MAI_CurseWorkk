from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class KnowledgeDB(Base):
    """Модель SQLAlchemy, соответствующая таблице knowledge_base_entry"""
    tablename = "knowledge_base_entry"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    correction = Column(Text, nullable=False)
    language = Column(String(50), default="python")
    severity_level = Column(String(50), nullable=False)
    source_service = Column(String(100))
    created_at = Column(TIMESTAMP, default=func.now())

class KnowledgeBaseEntryCreate(BaseModel):
    """Модель для создания новой записи через API"""
    pattern: str
    description: str
    correction: str
    language: str = "python"
    severity_level: str
    source_service: Optional[str] = None

class LookupResult(BaseModel):
    """Модель ответа при поиске рекомендации"""
    correction: str
    description: str
    severity_level: str

class KnowledgeBaseEntryResponse(KnowledgeBaseEntryCreate):
    """Полная модель ответа с ID и временем создания"""
    id: int
    created_at: str 
    
    class Config:
        orm_mode = True 