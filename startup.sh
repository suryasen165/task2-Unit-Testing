#!/bin/bash

# startup.sh - Handle database connection and app startup

echo "Starting FastAPI application..."

# Wait for database to be available
echo "Checking database connectivity..."

# Retry logic for database connection
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    python -c "
import psycopg2
import os
import sys

def get_db_url():
    if os.path.exists('/.dockerenv'):
        return 'postgresql://postgres:password@host.docker.internal:5432/fastapi_db'
    else:
        return 'postgresql://postgres:password@localhost:5432/fastapi_db'

try:
    import urllib.parse
    url = get_db_url()
    parsed = urllib.parse.urlparse(url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password
    )
    conn.close()
    print('Database connection successful!')
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        echo "Database is ready!"
        break
    fi
    
    retry_count=$((retry_count + 1))
    echo "Database not ready, attempt $retry_count/$max_retries. Retrying in 2 seconds..."
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "Failed to connect to database after $max_retries attempts"
    exit 1
fi

# Start the FastAPI application
echo "Starting uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000