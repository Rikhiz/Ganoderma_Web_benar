FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (required by OpenCV & ultralytics)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Railway provides PORT dynamically — use shell form so $PORT is expanded
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 app:app