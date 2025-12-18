from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class KnowledgeDB(Base):
    __tablename__  = "knowledge_base_entry"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(100), index=True, nullable=False) 
    keyword_pattern = Column(String(255), nullable=True) 
    
    description = Column(Text, nullable=False)
    correction = Column(Text, nullable=False)
    severity_level = Column(String(50), nullable=False)

class KnowledgeBaseEntryCreate(BaseModel):
    pattern: str
    description: str
    correction: str
    language: str = "python"
    severity_level: str
    source_service: Optional[str] = None

class LookupResult(BaseModel):
    correction: str
    description: str
    severity_level: str

class KnowledgeBaseEntryResponse(KnowledgeBaseEntryCreate):
    id: int
    created_at: str 
    
    class Config:
        orm_mode = True 
class KnowledgeResponse(BaseModel):
    id: int
    pattern: str
    description: str
    correction: str
    severity_level: str

    class Config:
        orm_mode = True
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: str = "user" 

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str
    is_active: bool

    class Config:
        orm_mode = True

class KnowledgeCreate(BaseModel):
    error_type: str
    keyword_pattern: Optional[str] = ""
    description: str
    correction: str
    severity_level: str = "Warning"

class KnowledgeUpdate(BaseModel):
    error_type: Optional[str] = None
    keyword_pattern: Optional[str] = None
    description: Optional[str] = None
    correction: Optional[str] = None
    severity_level: Optional[str] = None

class KnowledgeResponse(KnowledgeCreate):
    id: int

    class Config:
        orm_mode = True
class UserDB(Base):
    __tablename__  = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(String(20), default="user")  
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=func.now())