FROM python:3.12-slim

# ffmpeg es necesario para que yt-dlp convierta el audio descargado
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render asigna el puerto por variable de entorno PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
