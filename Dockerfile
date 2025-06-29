FROM python:3.10-slim as builder

# Install system build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# First copy only requirements to leverage Docker cache
COPY requirements.txt .

# Install dependencies in virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install -r requirements.txt

# Final lightweight image
FROM python:3.10-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /opt/venv /opt/venv
COPY . .

# Use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]


