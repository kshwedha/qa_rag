FROM python:3.9-slim

WORKDIR /app

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Command to run
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]