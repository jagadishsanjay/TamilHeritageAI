# =============================================================================
# தமிழ்ச்சுவடி AI – Production Container Image (Dockerfile)
# Multi-platform deployment for Linux / Cloud Run / Kubernetes / Docker
# =============================================================================

FROM python:3.11-slim

# Set environment variables for UTF-8 encoding and unbuffered output
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

# Install system dependencies: Tesseract OCR with Tamil language support & graphics libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-tam \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose standard Streamlit port
EXPOSE 8501

# Healthcheck probe to verify web application responsiveness
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Launch the Tamil Heritage AI platform
ENTRYPOINT ["streamlit", "run", "app.py"]
