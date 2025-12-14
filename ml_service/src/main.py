from fastapi import FastAPI, HTTPException
from src.models import CodeFragmentRequest, MLPredictionResponse
from src.ml_core import ml_analyzer

app = FastAPI(title="ML Analysis Service", version="1.0.0")

@app.post("/analyze/ml", response_model=MLPredictionResponse)
async def analyze_with_ml(request: CodeFragmentRequest):
    """
    Основной эндпоинт: принимает фрагмент кода, возвращает предсказание ML-модели.
    Используется Report Service для обогащения данных.
    """
    if not request.code_fragment:
        raise HTTPException(status_code=400, detail="Code fragment cannot be empty")
        
    try:
        prediction_result = ml_analyzer.predict(
            code_fragment=request.code_fragment,
            context=request.context_error_type
        )
        
        return MLPredictionResponse(**prediction_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при выполнении ML-модели: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "MLService"}