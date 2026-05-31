FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install uv and build dependencies
RUN pip install --no-cache-dir uv && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy project metadata for dependency resolution
COPY pyproject.toml uv.lock ./

# Install dependencies only (no editable install yet)
RUN uv sync --frozen --no-dev --no-install-project

# Copy all source code
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev

# Make entrypoint script executable
RUN chmod +x /app/postgres_docker_entrypoint.sh

EXPOSE 8000

# Default to API server — override CMD in docker-compose per service
ENTRYPOINT ["/app/postgres_docker_entrypoint.sh"]
CMD ["uvicorn", "cinemind.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
