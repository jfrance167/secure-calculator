# syntax=docker/dockerfile:1
FROM python:3.12.7-slim@sha256:60d9996b6a8a3689d36db740b49f4327be3be09a21122bd02fb8895abb38b50d AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip wheel --no-deps --wheel-dir /wheels .

FROM python:3.12.7-slim@sha256:60d9996b6a8a3689d36db740b49f4327be3be09a21122bd02fb8895abb38b50d AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --gid 10001 calculator \
    && useradd --uid 10001 --gid calculator --no-create-home \
        --shell /usr/sbin/nologin calculator

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels secure-calculator \
    && rm -rf /wheels

WORKDIR /app
USER 10001:10001
ENTRYPOINT ["secure-calculator"]
CMD ["--help"]
