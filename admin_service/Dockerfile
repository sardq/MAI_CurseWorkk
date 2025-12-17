FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade --no-cache-dir pip --disable-pip-version-check
RUN pip install --no-cache-dir -r requirements.txt 
COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8004"]