FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app/__init__.py
ENV FLASK_ENV production
ENV SQLALCHEMY_DATABASE_URI postgresql://neondb_owner:npg_Qmt0nrHAXC9u@ep-winter-wind-a8bzlq2q-pooler.eastus2.azure.neon.tech/neondb?sslmode=require

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run migrations and start the application
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:8000 'app:create_app()'"]
