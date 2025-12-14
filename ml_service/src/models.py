from pydantic import BaseModel
from typing import Optional, List

class CodeFragmentRequest(BaseModel):
    code_fragment: str        
    context_error_type: Optional[str] = None #
    
class MLPredictionResponse(BaseModel):
    ml_error_type: str        
    ml_severity: str          
    ml_correction: str        
    confidence: float         