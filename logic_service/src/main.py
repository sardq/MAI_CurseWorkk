from fastapi import FastAPI, HTTPException
from src.models import SourceCodeRequest, AnalysisResponse, AnalysisResult
from src.analyzer import analyze_logic

app = FastAPI(title="Logic Analysis Service", version="1.0.0")

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: SourceCodeRequest):
    """
    Эндпоинт для анализа логики выполнения.
    Принимает код, возвращает список ошибок и рекомендаций.
    """
    if not request.code:
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    raw_errors = analyze_logic(request.code)
    
    results = []
    for err in raw_errors:
        results.append(AnalysisResult(
            error_type="Logical",
            message=err["msg"],
            line=err["line"],
            column=err["col"],
            severity=err["severity"],
            suggestion=err["suggestion"]
        ))

    status = "Completed" if results else "No Errors Found" 

    return AnalysisResponse(
        errors=results,
        status=status
    )

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "LogicAnalysis"}