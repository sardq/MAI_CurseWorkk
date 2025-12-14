import asyncio
import httpx
import time
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db_session 
from src.models import (
    AnalysisSessionDB, ErrorDB, 
    SourceCodeRequest, AnalysisResultFromService, FinalReportResponse, FinalReportError
)
from typing import List

SERVICE_URLS = {
    "syntax": "http://syntax_service:8001/analyze",
    "logic": "http://logic_service:8003/analyze",
    "style": "http://style_service:8002/analyze",
    "knowledge_lookup": "http://knowledge_service:8004/knowledge/lookup/",
}

app = FastAPI(title="Analysis Gateway and Report Service", version="1.0.0")

async def run_analysis_tasks(code: str) -> List[AnalysisResultFromService]:
    """Запускает Syntax, Logic и Style анализ параллельно."""
    
    payload = {"code": code}
    all_errors: List[AnalysisResultFromService] = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        tasks = []
        for service_name, url in SERVICE_URLS.items():
            if service_name != "knowledge_lookup": 
                tasks.append(client.post(url, json=payload))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in responses:
            if isinstance(result, httpx.Response):
                try:
                    data = result.json()
                    if data and data.get("errors"):
                        for error_data in data["errors"]:
                            all_errors.append(AnalysisResultFromService(**error_data))
                except Exception:
                    print(f"Error parsing response from {result.url}")
            elif isinstance(result, Exception):
                print(f"Service connection error: {result}")
    
    return all_errors

@app.post("/api/v1/analyze_code", response_model=FinalReportResponse)
async def analyze_and_report(
    request: SourceCodeRequest,
    db: AsyncSession = Depends(get_db_session)
):
    start_time_ms = time.time() * 1000
    
    session_db = AnalysisSessionDB(
        user_id=request.user_id,
        filename=request.filename,
        status="PENDING"
    )
    db.add(session_db)
    await db.commit()
    await db.refresh(session_db)
    
    raw_errors = await run_analysis_tasks(request.code)
    
    final_errors: List[FinalReportError] = []
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for error in raw_errors:
            error_pattern = f"{error.error_type}_{error.severity}" 
            
            report_error = FinalReportError(**error.dict())
            
            try:
                kb_response = await client.get(SERVICE_URLS["knowledge_lookup"] + error_pattern)
                kb_response.raise_for_status()
                kb_data = kb_response.json()
                report_error.suggestion = kb_data.get("correction", report_error.suggestion)
                report_error.description = kb_data.get("description", report_error.description)
                report_error.severity = kb_data.get("severity_level", report_error.severity)
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
        duration_ms=round(duration_ms, 2)
    )