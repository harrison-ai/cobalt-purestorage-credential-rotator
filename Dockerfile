# builder stage
FROM python:3.10-slim-bullseye as builder

WORKDIR /app

COPY requirements.txt .

RUN pip wheel --no-deps --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

COPY . .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels .

# final stage
FROM python:3.10-slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive
# ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install \
    ca-certificates \
    --no-install-recommends -y

COPY --from=builder /app/wheels/* /app/wheels/

RUN pip install --no-index /app/wheels/*.whl
