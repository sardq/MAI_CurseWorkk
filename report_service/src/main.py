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
from typing import List, Optional, Tuple, Dict

SERVICE_URLS = {
    "syntax": "http://syntax_service:8001/analyze",
    "logic": "http://logic_service:8002/analyze",
    "style": "http://style_service:8003/analyze",
    "ml": "http://ml_service:8005/analyze/ml",
    "knowledge_lookup": "http://knowledge_service:8007/knowledge/lookup/",
}


app = FastAPI(title="Analysis Gateway and Report Service", version="1.0.0")

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
