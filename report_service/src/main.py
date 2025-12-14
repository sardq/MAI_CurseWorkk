import asyncio
import httpx
import time
import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from src.database import get_db_session, init_db 
from src.auth import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM

from src.models import (
    AnalysisSessionDB, ErrorDB, 
    SourceCodeRequest, AnalysisResultFromService, FinalReportResponse, FinalReportError, SessionDetailResponse, SessionSummaryResponse,
    UserDB, UserCreate, UserLogin, TokenResponse
)
from typing import List, Optional, Tuple, Dict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Analysis Gateway and Report Service", version="1.0.0")

# Разрешаем запросы с фронтенда
origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:5173",  # если используешь Vite dev-сервер
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup_event():
    await init_db()
    
SERVICE_URLS = {
    "syntax": "http://syntax_service:8001/analyze",
    "logic": "http://logic_service:8003/analyze",
    "style": "http://style_service:8002/analyze",
    "ml": "http://ml_service:8005/analyze/ml",
    "knowledge_lookup": "http://knowledge_service:8007/knowledge/lookup/",
}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(UserDB).where(UserDB.id == user_id)
    )
    user = result.scalar()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
def require_admin(current_user: UserDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

async def run_analysis_tasks(
    code: str
) -> Tuple[List[AnalysisResultFromService], Optional[Dict]]:
    """
    Запускает Syntax, Logic и Style анализ параллельно.
    Дополнительно извлекает AST summary из Syntax Service.
    """

    payload = {"code": code}
    all_errors: List[AnalysisResultFromService] = []
    ast_summary: Optional[Dict] = None

    async with httpx.AsyncClient(timeout=30.0) as client:

        tasks = {}
        for service_name, url in SERVICE_URLS.items():
            if service_name != "knowledge_lookup":
                tasks[service_name] = client.post(url, json=payload)

        responses = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for service_name, result in zip(tasks.keys(), responses):
            if isinstance(result, httpx.Response):
                try:
                    data = result.json()

                    if service_name == "syntax":
                        ast_summary = data.get("ast_summary")

                    if data and data.get("errors"):
                        for error_data in data["errors"]:
                            all_errors.append(
                                AnalysisResultFromService(**error_data)
                            )

                except Exception as e:
                    print(f"Error parsing response from {service_name}: {e}")

            elif isinstance(result, Exception):
                print(f"Service connection error ({service_name}): {result}")

    return all_errors, ast_summary

@app.post("/api/v1/analyze_code", response_model=FinalReportResponse)
async def analyze_and_report(
    request: SourceCodeRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserDB = Depends(get_current_user)
):
    start_time_ms = time.time() * 1000
    
    session_db = AnalysisSessionDB(
    user_id=current_user.id,
    filename=request.filename,
    status="PENDING"
    )

    db.add(session_db)
    await db.commit()
    await db.refresh(session_db)
    
    raw_errors, ast_summary = await run_analysis_tasks(request.code)
    
    final_errors: List[FinalReportError] = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for error in raw_errors:
            report_error = FinalReportError(**error.dict())
            try:
                ml_payload = {
                    "code_fragment": error.message,
                    "context_error_type": error.error_type
                }
                ml_response = await client.post(
                    SERVICE_URLS["ml"],
                    json=ml_payload
                )
                ml_response.raise_for_status()
                ml_data = ml_response.json()

                report_error.ml_error_type = ml_data.get("ml_error_type")
                report_error.ml_severity = ml_data.get("ml_severity")
                report_error.ml_correction = ml_data.get("ml_correction")
                report_error.ml_confidence = ml_data.get("confidence")

                report_error.severity = ml_data.get("ml_severity", report_error.severity)

            except (httpx.HTTPStatusError, httpx.RequestError):
                pass

            try:
                error_pattern = f"{error.error_type}_{report_error.severity}"
                kb_response = await client.get(
                    SERVICE_URLS["knowledge_lookup"] + error_pattern
                )
                kb_response.raise_for_status()
                kb_data = kb_response.json()

                report_error.suggestion = kb_data.get(
                    "correction", report_error.ml_correction
                )
                report_error.description = kb_data.get("description")

            except (httpx.HTTPStatusError, httpx.RequestError):
                report_error.description = "Нет готового шаблона в Базе Знаний."

            final_errors.append(report_error)

    for report_error in final_errors:
        error_db = ErrorDB(
            session_id=session_db.id,
            error_type=report_error.error_type,
            message=report_error.message,
            line=report_error.line,
            column=report_error.column,
            severity=report_error.severity,
            suggestion=report_error.suggestion
        )
        db.add(error_db)
        
    session_db.error_count = len(final_errors)
    session_db.end_time = datetime.datetime.now()
    session_db.status = "COMPLETED"
    
    await db.commit()
    
    end_time_ms = time.time() * 1000
    duration_ms = end_time_ms - start_time_ms

    return FinalReportResponse(
    session_id=session_db.id,
    status=session_db.status,
    total_errors=len(final_errors),
    errors=final_errors,
    duration_ms=round(duration_ms, 2),
    ast_summary=ast_summary
)
@app.get(
    "/api/v1/sessions",
    response_model=List[SessionSummaryResponse]
)
async def get_user_sessions(
    db: AsyncSession = Depends(get_db_session),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Возвращает историю анализов пользователя.
    """
    result = await db.execute(
        select(AnalysisSessionDB)
        .where(AnalysisSessionDB.user_id == current_user.id)
        .order_by(AnalysisSessionDB.start_time.desc())
    )
    sessions = result.scalars().all()

    return [
        SessionSummaryResponse(
            session_id=s.id,
            filename=s.filename,
            start_time=str(s.start_time),
            end_time=str(s.end_time) if s.end_time else None,
            status=s.status,
            error_count=s.error_count
        )
        for s in sessions
    ]
@app.get(
    "/api/v1/sessions/{session_id}",
    response_model=SessionDetailResponse
)
async def get_session_details(
    session_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Возвращает подробный отчёт по конкретной сессии анализа.
    """
    result = await db.execute(
        select(AnalysisSessionDB)
        .where(AnalysisSessionDB.id == session_id)
    )
    session = result.scalars().first()

    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    errors = [
        FinalReportError(
            error_type=e.error_type,
            message=e.message,
            line=e.line,
            column=e.column,
            severity=e.severity,
            suggestion=e.suggestion
        )
        for e in session.errors
    ]

    return SessionDetailResponse(
        session_id=session.id,
        filename=session.filename,
        status=session.status,
        error_count=session.error_count,
        start_time=str(session.start_time),
        end_time=str(session.end_time) if session.end_time else None,
        errors=errors
    )
@app.post("/api/v1/auth/register")
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(UserDB).where(UserDB.username == user.username)
    )
    if result.scalar():
        raise HTTPException(status_code=400, detail="User already exists")

    db_user = UserDB(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    await db.commit()

    return {"status": "User registered"}
@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login_user(
    user: UserLogin,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(UserDB).where(UserDB.username == user.username)
    )
    db_user = result.scalar()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(db_user.id)})

    return TokenResponse(access_token=token)

