from pydantic import BaseModel, Field
from typing import Optional, List

class CodeFragmentRequest(BaseModel):
    code_fragment: str        
    context_error_type: Optional[str] = None #
    
class MLPredictionResponse(BaseModel):
    ml_error_type: str        
    ml_severity: str          
    ml_correction: str        
    confidence: float         
class FeedbackRequest(BaseModel):
    buggy_code: str = Field(..., min_length=5)
    fixed_code: str = Field(..., min_length=5)
    commit_message: str = Field(..., min_length=3)