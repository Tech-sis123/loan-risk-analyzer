# Use official Python 3.10 image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y build-essential

# Install pip tools
RUN pip install --upgrade pip setuptools wheel

# Install dependencies
RUN pip install -r requirements.txt

# Expose app port
EXPOSE 8000

# Start your Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
