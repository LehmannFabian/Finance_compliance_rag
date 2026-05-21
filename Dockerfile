FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SERVICE_TYPE=api

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 8000 8501

CMD if [ "$SERVICE_TYPE" = "frontend" ]; then \
        streamlit run src/frontend.py \
            --server.address 0.0.0.0 \
            --server.port ${PORT:-8501} \
            --server.headless true; \
    else \
        uvicorn src.main:app \
            --host 0.0.0.0 \
            --port ${PORT:-8000}; \
    fi
