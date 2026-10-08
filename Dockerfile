FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_INDEX_URL=https://packagefeedproxy.microsoft.io/pypi/simple

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 smartassist \
    && chown --recursive smartassist:smartassist /app

USER smartassist

EXPOSE 8000

CMD ["uvicorn", "smartassist.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
