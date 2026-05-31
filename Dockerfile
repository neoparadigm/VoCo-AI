FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/ ./backend/
COPY mock_data/ ./mock_data/

RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
