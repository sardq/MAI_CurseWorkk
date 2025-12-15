FROM tensorflow/tensorflow:2.15.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV CUDA_VISIBLE_DEVICES="-1"

RUN python src/train_model.py

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]
