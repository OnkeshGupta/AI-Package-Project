# ---- Base image ----
FROM python:3.11-slim

# ---- Environment settings ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- Working directory ----
WORKDIR /app

# ---- System dependencies ----
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# ---- Python dependencies ----
COPY requirements.docker.txt .
RUN pip install --no-cache-dir -r requirements.docker.txt

# ---- Copy application ----
COPY app ./app

# ---- Create uploads directory ----
RUN mkdir -p /app/uploads

# ---- Expose port ----
EXPOSE 8000

# ---- Run server ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]