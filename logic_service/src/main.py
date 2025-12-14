# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from analyzer import analyze_logic

class SourceCodeRequest(BaseModel):
    code: str

class AnalysisResult(BaseModel):
    error_type: str
    message: str
    line: int
    column: int
    severity: str
    suggestion: Optional[str] = None

class AnalysisResponse(BaseModel):
    errors: List[AnalysisResult]
    status: str

app = FastAPI(title="Logic Analysis Service", version="1.0.0")

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: SourceCodeRequest):
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
    return AnalysisResponse(errors=results, status=status)

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "LogicAnalysis"}
