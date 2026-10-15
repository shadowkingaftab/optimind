# EyeDx backend image.
#
# Build (from the backend/ directory):
#   docker build -t eyedx-backend .
#
# The image runs as a non-root user and starts Gunicorn with Uvicorn workers.

FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System dependencies kept minimal; build-essential removed after build.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source.
COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
COPY gunicorn.conf.py ./

# Create and switch to an unprivileged user.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/v1/health || exit 1

CMD ["gunicorn", "app.main:app", "--config", "gunicorn.conf.py"]
