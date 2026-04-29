FROM alpine:3.19

RUN apk add --no-cache python3 py3-pip curl libgcc libstdc++

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN adduser -D finskyuser
WORKDIR /home/finskyuser

COPY . .

RUN uv sync --frozen

RUN chown -R finskyuser:finskyuser /home/finskyuser
USER finskyuser

ENTRYPOINT ["uv", "run", "python", "app/main.py"]