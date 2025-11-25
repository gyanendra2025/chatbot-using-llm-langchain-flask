# Use Python 3.10 slim image for smaller footprint
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables to prevent .pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for some python packages
# gcc and python3-dev might be needed for some libraries
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory/file to ensure permissions (optional, but good practice)
RUN touch app.log && chmod 666 app.log

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application using the production WSGI server
CMD ["python", "wsgi.py"]

