from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserDB(Base):
    __tablename__  = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(String(20), default="user") 
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=func.now())

class KnowledgeDB(Base):
    __tablename__  = "knowledge_base_entry"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(100), index=True, nullable=False) 
    keyword_pattern = Column(String(255), nullable=True) 
    
    description = Column(Text, nullable=False)
    correction = Column(Text, nullable=False)
    severity_level = Column(String(50), nullable=False) 


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

class KnowledgeEntryUpdate(BaseModel):
    description: Optional[str] = None
    correction: Optional[str] = None
    severity_level: Optional[str] = None
    
class KnowledgeResponse(BaseModel):
    id: int
    pattern: str
    description: str
    correction: str
    severity_level: str

    class Config:
        orm_mode = True
        
class LookupRequest(BaseModel):
    error_type: str
    error_message: str

class MLFeedbackRequest(BaseModel):
    buggy_code: str
    fixed_code: str
    commit_message: str