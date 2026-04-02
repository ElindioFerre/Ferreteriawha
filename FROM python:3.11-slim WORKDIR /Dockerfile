FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Forzamos que use el puerto 8000
CMD uvicorn agent.main:app --host 0.0.0.0 --port 8000
