FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY main.py ./

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

RUN useradd --system --no-create-home --uid 1000 appuser

USER 1000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]