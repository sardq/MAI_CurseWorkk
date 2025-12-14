FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN python -c "from src.ml_core import train_and_save_model; train_and_save_model()"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]