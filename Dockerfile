FROM python:3.10-slim

WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# System deps for Playwright headless Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2 \
    libxcomposite1 libxdamage1 libxfixes3 libxrender1 libxrandr2 libgtk-3-0 \
    ca-certificates fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# Python deps + Playwright browsers
COPY requirements.txt .
RUN pip install -r requirements.txt && python -m playwright install --with-deps

# App code
COPY src ./src
COPY data ./data

# Default: headless perf run on sample data; override with `docker run ... --file ...`
CMD ["python", "-m", "src.main", "--file", "data/sample.csv", "--headless", "--perf"]

