FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libasound2 libxss1 libxcomposite1 libxrandr2 libgbm-dev \
    libxdamage1 libx11-xcb1 xvfb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m playwright install --with-deps

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Environment configs
ENV HEADLESS=false
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/entrypoint.sh"]
