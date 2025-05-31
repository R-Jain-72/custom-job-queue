
# Use official Python 3.8 slim image as base
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY api.py worker.py app.py ./

# Expose ports for Flask API (5000) and Streamlit (8501)
EXPOSE 5000 8501

# Default command (will be overridden in docker-compose.yml)
CMD ["python", "api.py"]
