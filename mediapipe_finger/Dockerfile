# Use Python 3.12 on a lightweight Debian Linux image
FROM python:3.12-slim-bookworm

# Set the main application directory
WORKDIR /app

# Install Linux libraries required by OpenCV and MediaPipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libegl1 \
    libgles2 \
    libglib2.0-0 \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MediaPipe model and application
COPY models/ models/
COPY web_demo/backend/ web_demo/backend/

# Run from the directory containing app.py
WORKDIR /app/web_demo/backend

# Document the port used by the application
EXPOSE 8080

# Start FastAPI using Uvicorn
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]