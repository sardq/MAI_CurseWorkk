from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func, Boolean
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()



class UserDB(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    email = Column(String(100), unique=True)
    role = Column(String(50), default="user")
    sessions = relationship("AnalysisSessionDB", back_populates="user")


class AnalysisSessionDB(Base):
    __tablename__ = "analysis_session"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    filename = Column(String(255))
    start_time = Column(TIMESTAMP, default=func.now())
    end_time = Column(TIMESTAMP)
    status = Column(String(50))
    error_count = Column(Integer, default=0)

    user = relationship("UserDB", back_populates="sessions")
    errors = relationship("ErrorDB", back_populates="session")


class ErrorDB(Base):
    __tablename__ = "error"

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


class SessionSummaryResponse(BaseModel):
    session_id: int
    filename: str
    start_time: Optional[str]
    end_time: Optional[str]
    status: str
    error_count: int


class SessionDetailResponse(BaseModel):
    session_id: int
    filename: str
    status: str
    error_count: int
    start_time: Optional[str]
    end_time: Optional[str]
    errors: List[FinalReportError]

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
