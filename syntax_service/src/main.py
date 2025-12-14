from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict
from src.analyzer import analyze_syntax_with_ast

app = FastAPI(title="Syntax Analysis Service", version="2.1.0")

class SourceCodeRequest(BaseModel):
    code: str
    language: str = "python"

class AnalysisResult(BaseModel):
    error_type: str
    message: str
    line: int
    column: int
    severity: str
    suggestion: Optional[str] = None

class AnalysisResponse(BaseModel):
    errors: List[AnalysisResult]
    ast_summary: Dict
    status: str

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_syntax(request: SourceCodeRequest):
    if not request.code:
        return AnalysisResponse(
            errors=[],
            ast_summary={},
            status="Empty Code"
        )

    raw_errors, ast_summary = analyze_syntax_with_ast(request.code)

    errors = [AnalysisResult(**e) for e in raw_errors]

    status = "Syntax Valid" if not errors else "Syntax Error Detected"

    return AnalysisResponse(
        errors=errors,
        ast_summary=ast_summary,
        status=status
    )
