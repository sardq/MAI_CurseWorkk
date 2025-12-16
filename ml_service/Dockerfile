FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir torch==2.3.1


RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

ENV CUDA_VISIBLE_DEVICES="-1"
ENV PYTHONPATH=/app

RUN python src/train_model.py

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]