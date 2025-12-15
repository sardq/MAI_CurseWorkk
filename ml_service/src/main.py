import os
from fastapi import FastAPI, HTTPException
import pandas as pd
from pydantic import BaseModel
from src.train_model import DATA_PATH, train
from src.models import CodeFragmentRequest, MLPredictionResponse
from src.ml_core import ml_analyzer
from fastapi import BackgroundTasks

class FeedbackRequest(BaseModel):
    buggy_code: str
    fixed_code: str
    commit_message: str
def append_to_csv_and_retrain(buggy, fixed, msg):
    """
    1. Добавляет новую строку в CSV.
    2. Запускает переобучение.
    3. Перезагружает модель в памяти.
    """
    # 1. Добавляем в CSV
    new_data = pd.DataFrame([[buggy, fixed, msg]], columns=["buggy_code", "fixed_code", "commit_message"])
    # mode='a' - append (добавление), header=False (не пишем заголовок снова)
    new_data.to_csv(DATA_PATH, mode='a', header=not os.path.exists(DATA_PATH), index=False)
    
    # 2. Переобучаем файлы pkl
    train()
    
    # 3. Обновляем модель в памяти (чтобы сразу начало работать)
    # Нужно добавить метод reload в ваш класс MLAnalyzer
    ml_analyzer.reload_model() 
def update_dataset_file(buggy, fixed, msg):
    import pandas as pd
    new_data = pd.DataFrame([[buggy, fixed, msg]], columns=["buggy_code", "fixed_code", "commit_message"])
    new_data.to_csv("data/code_bug_fix_pairs.csv", mode='a', header=False, index=False)
app = FastAPI(title="ML Analysis Service", version="1.0.0")

@app.post("/train/feedback")
async def feedback_loop(data: FeedbackRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(append_to_csv_and_retrain, data.buggy_code, data.fixed_code, data.commit_message)
    return {"status": "Feedback accepted, model will be updated"}

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