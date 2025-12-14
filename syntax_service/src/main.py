from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import sys

app = FastAPI(title="Syntax Analysis Service", version="2.0.0 (Max Coverage)")

class SourceCodeRequest(BaseModel):
    code: str
    language: str = "python" 

class AnalysisResult(BaseModel):
    error_type: str = "Syntax"
    message: str
    line: int
    column: int
    severity: str = "Critical"
    suggestion: Optional[str] = "Проверьте корректность структуры языка и его правил."

class AnalysisResponse(BaseModel):
    errors: List[AnalysisResult]
    status: str

def check_syntax_maximal(code: str) -> List[AnalysisResult]:
    errors = []
    
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        errors.append(AnalysisResult(
            message=f"Синтаксическая ошибка: {e.msg}",
            line=e.lineno or 1,
            column=e.offset or 1,
            suggestion=f"Ошибка в строке {e.lineno}. Символ: {e.text.strip() if e.text else 'N/A'}"
        ))
    except (ValueError, TypeError) as e:
        errors.append(AnalysisResult(
            message=f"Ошибка компиляции: {str(e)}",
            line=1,
            column=1,
            severity="Critical"
        ))
    except Exception as e:
        errors.append(AnalysisResult(
            message=f"Непредвиденная ошибка анализа: {str(e)}",
            line=0,
            column=0,
            severity="Critical"
        ))
        
    return errors

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_syntax(request: SourceCodeRequest):
    if not request.code:
        return AnalysisResponse(errors=[], status="Empty Code")

    results = check_syntax_maximal(request.code)
    
    status = "Syntax Valid" if not results else "Syntax Error Detected"
    
    return AnalysisResponse(errors=results, status=status)