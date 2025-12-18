from pydantic import BaseModel
from typing import List, Optional

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
    filename: str = "unknown"
    errors: List[AnalysisResult]
    status: str            