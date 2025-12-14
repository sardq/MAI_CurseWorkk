from pydantic import BaseModel
from typing import List, Optional

class SourceCodeRequest(BaseModel):
    """Модель входящего запроса с исходным кодом"""
    code: str
    language: str = "python" 
class AnalysisResult(BaseModel):
    """Модель ошибки, соответствующая таблице Error """
    error_type: str        
    message: str           
    line: int             
    column: int            
    severity: str          
    suggestion: Optional[str] = None 

class AnalysisResponse(BaseModel):
    """Формат ответа сервиса"""
    filename: str = "unknown"
    errors: List[AnalysisResult]
    status: str            