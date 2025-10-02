FROM python:3.11-slim

WORKDIR /app

COPY ./backend/requirements.txt /app/requirements.txt
COPY ./static/favicon.ico /app/static/favicon.ico

# Install system dependencies and then Python dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of backend application
COPY ./backend /app/backend

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
