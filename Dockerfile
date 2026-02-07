# Production Dockerfile for ClipContext API (CPU-only, slim)
FROM python:3.11-slim

WORKDIR /app

# Install only essential build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install CPU-only PyTorch and compatible numpy (much smaller than full PyTorch)
RUN pip install --no-cache-dir "numpy<2.0"
RUN pip install --no-cache-dir \
    torch==2.4.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Copy and install other requirements
COPY backend/requirements.txt .

# Install remaining deps (skip torch since we installed CPU version)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app

# Expose port
EXPOSE 8000

# Longer health check start period for model download
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
