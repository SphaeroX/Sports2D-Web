FROM python:3.11-slim

# Install system deps: ffmpeg, build tools, opencv deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    gcc \
    g++ \
    tcl \
    tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Sports2D from parent repo first
COPY . /app/Sports2D-Web/
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPORTS2D=0.12.0
RUN pip install --no-cache-dir -e /app/Sports2D-Web

# Copy backend requirements and install
COPY web/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY web/backend/ ./backend/

WORKDIR /app/backend

# Create data dirs
RUN mkdir -p /app/data/uploads /app/data/results /app/data/previews

ENV PYTHONPATH=/app/backend:/app/Sports2D-Web
ENV MPLBACKEND=Agg
ENV REDIS_URL=redis://redis:6379/0
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
