import os
import asyncio
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.models import CodeFragmentRequest, FeedbackRequest, MLPredictionResponse
from src.ml_core import ml_analyzer
from src.train_model import train, DATA_PATH

app = FastAPI(title="ML Analysis Service", version="1.0.0")

scheduler = AsyncIOScheduler()

IS_TRAINING = False

async def run_training_task():
    global IS_TRAINING
    if IS_TRAINING:
        print("⚠️ Training already in progress. Skipping.")
        return

    IS_TRAINING = True
    try:
        await asyncio.to_thread(train)
        
        ml_analyzer.reload_model()
    except Exception as e:
        print(f"Training failed: {e}")
    finally:
        IS_TRAINING = False

@app.on_event("startup")
async def startup_event():
    scheduler.add_job(run_training_task, 'interval', hours=2)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


@app.post("/train/feedback")
async def feedback_loop(data: FeedbackRequest):
    new_data = pd.DataFrame([[data.buggy_code, data.fixed_code, data.commit_message]], 
                            columns=["buggy_code", "fixed_code", "commit_message"])
    
    header = not os.path.exists(DATA_PATH)
    new_data.to_csv(DATA_PATH, mode='a', header=header, index=False)
    
    return {"status": "Feedback saved. Model will be updated in the next scheduled run."}

@app.post("/train/force")
async def force_training(background_tasks: BackgroundTasks):
    """
    Ручка для админа: если нужно срочно применить изменения, не дожидаясь расписания.
    """
    if IS_TRAINING:
         raise HTTPException(status_code=409, detail="Training already running")
         
    background_tasks.add_task(run_training_task)
    return {"status": "Force training started."}

@app.post("/analyze/ml", response_model=MLPredictionResponse)
async def analyze_with_ml(request: CodeFragmentRequest):
    if not request.code_fragment:
        raise HTTPException(status_code=400, detail="Empty code")
        
    try:
        prediction_result = ml_analyzer.predict(
            code_fragment=request.code_fragment,
            context=request.context_error_type
        )
        return MLPredictionResponse(**prediction_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "active", 
        "training_in_progress": IS_TRAINING,
        "model_loaded": ml_analyzer.embedder is not None
    }