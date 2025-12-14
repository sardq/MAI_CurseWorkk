from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from src.checker import check_style_maximal

app = FastAPI(title="Style Analysis Service", version="2.0.0 (Max Coverage)")

class SourceCodeRequest(BaseModel):
    code: str

class AnalysisResult(BaseModel):
    error_type: str = "Style"
    message: str
    line: int
    column: int
    severity: str 
    suggestion: Optional[str] = "Приведите код в соответствие с принятыми стандартами (например, PEP 8)."

class AnalysisResponse(BaseModel):
    errors: List[AnalysisResult]
    status: str

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_style(request: SourceCodeRequest):
    if not request.code:
        return AnalysisResponse(errors=[], status="Empty Code")

    errors_data = check_style_maximal(request.code)
    
    results = []
    for e in errors_data:
        results.append(AnalysisResult(
            message=e["msg"],
            line=e["line"],
            column=e["col"],
            severity=e["severity"],
            suggestion="Приведите код в соответствие с принятыми стандартами (например, PEP 8)."
        ))

    return AnalysisResponse(
        errors=results,
        status="Style Checked"
    )