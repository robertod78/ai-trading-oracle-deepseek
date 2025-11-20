# Trading Bot - Dockerfile Corretto per Chrome Headless
FROM ubuntu:22.04

# Evita prompt interattivi durante l'installazione
ENV DEBIAN_FRONTEND=noninteractive

# Aggiorna e installa dipendenze di base
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    wget \
    curl \
    gnupg \
    ca-certificates \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Aggiungi repository Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

# Installa Google Chrome e dipendenze
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
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
    libxshmfence1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Installa ChromeDriver compatibile con la versione di Chrome
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) \
    && CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") \
    && wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && apt-get update && apt-get install -y unzip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm chromedriver_linux64.zip \
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

# Modifica tradingview_scraper.py per usare il path corretto di chromedriver
RUN sed -i "s|service = Service('/usr/bin/chromedriver')|service = Service('/usr/bin/chromedriver')|g" tradingview_scraper.py

# Crea directory per screenshots
RUN mkdir -p /app/screenshots

# Variabili d'ambiente con valori di default
ENV DEEPSEEK_API_KEY=""
ENV SYMBOL="XAUUSD"
ENV BROKER="EIGHTCAP"
ENV INTERVAL="10"
ENV SCREENSHOTS_DIR="/app/screenshots"
ENV RUN_ONCE="false"

# Variabili d'ambiente per Chrome headless
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER=/usr/bin/chromedriver

# Script di avvio
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Volume per persistenza screenshots
VOLUME ["/app/screenshots"]

# Entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
