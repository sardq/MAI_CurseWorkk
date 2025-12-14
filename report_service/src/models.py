from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel
from typing import List, Optional
import datetime

Base = declarative_base()


class AnalysisSessionDB(Base):
    """Таблица AnalysisSession: хранит метаданные о сессии анализа."""
    __tablename__  = "analysis_session"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True) 
    filename = Column(String(255))
    start_time = Column(TIMESTAMP, default=func.now())
    end_time = Column(TIMESTAMP)
    status = Column(String(50))
    error_count = Column(Integer, default=0)

    errors = relationship("ErrorDB", back_populates="session")

class ErrorDB(Base):
    """Таблица Error: хранит все найденные ошибки."""
    __tablename__  = "error"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('analysis_session.id'), nullable=False)
    
    error_type = Column(String(50), nullable=False) 
    message = Column(Text, nullable=False)
    line = Column(Integer)
    column = Column(Integer)
    severity = Column(String(50))
    suggestion = Column(Text)
    

    session = relationship("AnalysisSessionDB", back_populates="errors")


class SourceCodeRequest(BaseModel):
    code: str
    user_id: Optional[int] = None
    filename: str = "main.py"

class AnalysisResultFromService(BaseModel):
    """Входящий формат ошибки от Syntax/Logic/Style сервисов"""
    error_type: str
    message: str
    line: int
    column: int
    severity: str
    suggestion: Optional[str] = None

class FinalReportError(AnalysisResultFromService):
    description: Optional[str] = None
    ml_error_type: Optional[str] = None
    ml_severity: Optional[str] = None
    ml_correction: Optional[str] = None
    ml_confidence: Optional[float] = None
    
class ASTSummary(BaseModel):
    total_nodes: int
    node_types: dict
    functions: int
    classes: int
    loops: int
    conditions: int
class FinalReportResponse(BaseModel):
    session_id: int
    status: str
    total_errors: int
    errors: List[FinalReportError]
    duration_ms: float
    ast_summary: Optional[ASTSummary] = None

