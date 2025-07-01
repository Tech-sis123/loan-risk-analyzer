FROM python:3.11-slim

# Create a non-root user and switch to it
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
WORKDIR /app
USER appuser

# Rest of your Dockerfile remains the same
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=1

COPY --chown=appuser:appuser requirements.txt .

RUN pip install --user --no-warn-script-location -r requirements.txt

COPY --chown=appuser:appuser . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]