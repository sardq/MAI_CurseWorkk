from pydantic import BaseModel
from typing import List, Optional


class SourceCodeRequest(BaseModel):
    """
    Модель входящего запроса: исходный код, который нужно проанализировать.
    """
    code: str
    language: str = "python"


class AnalysisResult(BaseModel):
    """
    Модель одной найденной ошибки/замечания. 
    Прямо соответствует полям таблицы Error (Рис. 4, Лаб 2).
    """
    error_type: str       
    message: str           
    line: int              
    column: int           
    severity: str         
    suggestion: Optional[str] = None 


class AnalysisResponse(BaseModel):
    """
    Формат ответа сервиса. Содержит статус и список всех найденных ошибок.
    """
    errors: List[AnalysisResult] 
    status: str           