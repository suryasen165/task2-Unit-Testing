# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for psycopg2 and curl for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Add a startup script to handle database connection
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

# Health check with longer timeout and more retries
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the app with startup script
CMD ["/startup.sh"]