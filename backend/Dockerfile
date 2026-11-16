FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY scripts ./scripts
CMD ["sh","-c","python -m scripts.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
