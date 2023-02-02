FROM python:3.10-slim-bullseye as builder

ARG DEBIAN_FRONTEND=noninteractive

# RUN apt-get update \
#     && apt-get install \
#     ca-certificates \
#     --no-install-recommends -y

RUN pip install -U pip && \
    pip install build

COPY . ./

RUN python -m build --wheel

FROM python:3.10-slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install \
    ca-certificates \
    --no-install-recommends -y

COPY --from=builder /dist/*.whl ./

RUN pip install /*.whl
