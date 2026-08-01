FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY app ./app

RUN pip install --no-cache-dir -e .

COPY . .

RUN chmod +x /app/entrypoint.sh

ENV PYTHONPATH=/app

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
