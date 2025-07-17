FROM python:3.11-slim-buster AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

####################

FROM python:3.11-slim-buster AS runtime

WORKDIR /app

COPY --from=builder /.venv /.venv

ENV PATH="/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY src /app/src
COPY chainlit.md /app/chainlit.md

CMD ["chainlit", "run", "src/webui/chainlit_main.py", "-h", "--no-cache", "--host", "0.0.0.0", "--port", "8080"]