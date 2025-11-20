# Trading Bot - Dockerfile con Playwright
# Molto più semplice e stabile rispetto a Selenium!
FROM ubuntu:22.04

# Evita prompt interattivi durante l'installazione
ENV DEBIAN_FRONTEND=noninteractive

# Installa Python e dipendenze di base
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crea directory di lavoro
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Installa dipendenze Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Installa i browser di Playwright (gestisce tutto automaticamente!)
RUN playwright install --with-deps chromium

# Copia i file del progetto
COPY app.py .
COPY trading_bot.py .
COPY tradingview_scraper.py .
COPY deepseek_analyzer.py .
COPY templates/ ./templates/

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

# Esponi porta per interfaccia web
EXPOSE 5555

# Entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
