from fastapi import FastAPI, HTTPException
from src.models import SourceCodeRequest, AnalysisResponse, AnalysisResult # Используем общие модели
from src.semantic_analyzer import analyze_semantic

app = FastAPI(title="Semantic Analysis Service", version="1.0.0")

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: SourceCodeRequest):
    """
    Эндпоинт для анализа семантики и неструктурированных ресурсов (комментариев/документации).
    """
    if not request.code:
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    raw_errors = analyze_semantic(request.code)
    
    results = []
    for err in raw_errors:
        results.append(AnalysisResult(
            error_type=err["error_type"],
            message=err["msg"],
            line=err["line"],
            column=err["col"],
            severity=err["severity"],
            suggestion=err["suggestion"]
        ))

    status = "Completed" if results else "No Semantic Errors Found"

    return AnalysisResponse(
        errors=results,
        status=status
    )