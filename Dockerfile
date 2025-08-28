# Base image
FROM python:3.13-slim-bookworm AS base
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.4.30 /uv /uvx /bin/
# Build stage
FROM base AS build
WORKDIR /app
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --group remote --no-install-project
COPY . .

# Runtime stage
FROM base AS runtime
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"
RUN echo "source /app/.venv/bin/activate" >> /etc/profile.d/venv.sh

# Expose port
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "store.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
