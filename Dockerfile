FROM python:3.12-slim

# uv dentro de la imagen
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Primero las dependencias (se cachean si no cambia el lock)
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

# Después el código
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]