# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=CISProject.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a script to handle startup
RUN echo '#!/bin/bash\n\
# Collect static files (skip if STATIC_ROOT not configured)\n\
python manage.py collectstatic --noinput || echo "Static collection skipped"\n\
\n\
# Run migrations (skip if no database)\n\
python manage.py migrate || echo "Migrations skipped"\n\
\n\
# Get port from environment variable (Railway sets PORT)\n\
PORT=${PORT:-8000}\n\
\n\
# Start gunicorn\n\
exec gunicorn --bind 0.0.0.0:$PORT CISProject.wsgi:application\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port (Railway will override this)
EXPOSE 8000

# Start command
CMD ["/app/start.sh"] 