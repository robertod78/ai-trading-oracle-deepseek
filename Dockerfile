# Trading Bot - Dockerfile
FROM ubuntu:22.04

# Evita prompt interattivi durante l'installazione
ENV DEBIAN_FRONTEND=noninteractive

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    chromium-browser \
    chromium-chromedriver \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Crea directory di lavoro
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Installa dipendenze Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Copia i file del progetto
COPY trading_bot.py .
COPY tradingview_scraper.py .
COPY deepseek_analyzer.py .

# Crea directory per screenshots
RUN mkdir -p /app/screenshots

# Variabili d'ambiente con valori di default
ENV DEEPSEEK_API_KEY=""
ENV SYMBOL="XAUUSD"
ENV BROKER="EIGHTCAP"
ENV INTERVAL="10"
ENV SCREENSHOTS_DIR="/app/screenshots"
ENV RUN_ONCE="false"

# Script di avvio
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Volume per persistenza screenshots
VOLUME ["/app/screenshots"]

# Entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
