FROM python:3.14.2-slim AS final

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Install git for uv to fetch dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy only the dependency files first (better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies with `uv` without copying the whole app yet
RUN uv sync --frozen --no-install-project --no-dev

# Now copy the rest of the app
COPY . .

# Sync the project itself
RUN uv sync --frozen --no-dev

ENV PYTHONPATH=/app/src

EXPOSE 8001

ENTRYPOINT ["/app/entrypoint.sh"]

# Use the venv path directly or let uv run handle it
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
