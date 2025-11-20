# Trading Bot - Guida Docker

Questa guida spiega come eseguire il Trading Bot in un container Docker.

## Prerequisiti

- Docker installato (versione 20.10 o superiore)
- Docker Compose installato (versione 1.29 o superiore)
- Chiave API DeepSeek

## Installazione Docker

### Ubuntu/Debian
```bash
# Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installa Docker Compose
sudo apt-get install docker-compose-plugin

# Aggiungi utente al gruppo docker (opzionale)
sudo usermod -aG docker $USER
```

### Verifica installazione
```bash
docker --version
docker compose version
```

## Configurazione

### 1. Crea il file .env

Copia il template e modifica con i tuoi valori:

```bash
cp .env.template .env
nano .env
```

Inserisci almeno la chiave API:
```bash
DEEPSEEK_API_KEY=sk-la-tua-chiave-api
```

### 2. Variabili d'ambiente disponibili

| Variabile | Descrizione | Default | Obbligatorio |
|-----------|-------------|---------|--------------|
| `DEEPSEEK_API_KEY` | Chiave API DeepSeek | - | ✅ Sì |
| `SYMBOL` | Simbolo CFD | XAUUSD | ❌ No |
| `BROKER` | Broker | EIGHTCAP | ❌ No |
| `INTERVAL` | Intervallo in minuti | 10 | ❌ No |
| `RUN_ONCE` | Esecuzione singola | false | ❌ No |

## Utilizzo

### Build dell'immagine

```bash
docker compose build
```

### Avvio del bot (loop continuo)

```bash
docker compose up -d
```

Il bot:
- Si avvia in background
- Cattura screenshot ogni 10 minuti (o l'intervallo configurato)
- Chiede analisi a DeepSeek AI
- Stampa i segnali di trading
- ⚠️ **Le operazioni suggerite durano MASSIMO 5 MINUTI**

### Visualizza i log

```bash
# Log in tempo reale
docker compose logs -f

# Ultimi 100 log
docker compose logs --tail=100
```

### Esecuzione singola

Per una singola analisi invece del loop continuo:

```bash
# Modifica .env
RUN_ONCE=true

# Avvia
docker compose up
```

Oppure override diretto:
```bash
docker compose run --rm -e RUN_ONCE=true trading-bot
```

### Stop del bot

```bash
docker compose down
```

### Riavvio

```bash
docker compose restart
```

## Screenshot

Gli screenshot vengono salvati in `./screenshots/` sulla macchina host grazie al volume Docker.

Formato: `YYYYMMDD_HHMMSS_timeframe.png`

Esempio:
```
screenshots/
├── 20251120_143052_1min.png
├── 20251120_143052_15min.png
└── 20251120_143052_60min.png
```

## Esempi di configurazione

### Analisi EUR/USD ogni 5 minuti

File `.env`:
```bash
DEEPSEEK_API_KEY=sk-xxxxx
SYMBOL=EURUSD
BROKER=OANDA
INTERVAL=5
```

### Analisi Bitcoin una sola volta

File `.env`:
```bash
DEEPSEEK_API_KEY=sk-xxxxx
SYMBOL=BTCUSD
BROKER=BINANCE
RUN_ONCE=true
```

### Analisi Gold con parametri custom

```bash
docker compose run --rm \
  -e DEEPSEEK_API_KEY=sk-xxxxx \
  -e SYMBOL=XAUUSD \
  -e BROKER=EIGHTCAP \
  -e INTERVAL=15 \
  trading-bot
```

## Troubleshooting

### Container si ferma immediatamente

Verifica i log:
```bash
docker compose logs
```

Causa comune: `DEEPSEEK_API_KEY` non impostata.

### Screenshot non vengono salvati

Verifica i permessi della directory:
```bash
ls -la screenshots/
```

Se necessario:
```bash
chmod 777 screenshots/
```

### Errore "ChromeDriver not found"

Il Dockerfile include già ChromeDriver. Se l'errore persiste, ricostruisci l'immagine:
```bash
docker compose build --no-cache
```

### Memoria insufficiente

Aumenta `shm_size` in `docker-compose.yaml`:
```yaml
shm_size: '4gb'  # Aumenta da 2gb a 4gb
```

### Container usa troppa CPU

Chrome headless può essere pesante. Considera:
- Aumentare l'intervallo (`INTERVAL=15` o più)
- Limitare le risorse Docker

## Comandi utili

```bash
# Rebuild forzato
docker compose build --no-cache

# Rimuovi tutto (container, volumi, network)
docker compose down -v

# Accedi al container in esecuzione
docker compose exec trading-bot bash

# Visualizza risorse usate
docker stats trading-bot

# Esporta logs in file
docker compose logs > bot_logs.txt
```

## Aggiornamenti

Per aggiornare il bot:

```bash
# Stop
docker compose down

# Pull nuovi file (se da Git)
git pull

# Rebuild
docker compose build

# Restart
docker compose up -d
```

## Produzione

Per uso in produzione:

1. **Usa restart policy appropriato**:
   ```yaml
   restart: always
   ```

2. **Configura log rotation**:
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "50m"
       max-file: "5"
   ```

3. **Monitora il container**:
   ```bash
   docker compose ps
   docker compose logs -f
   ```

4. **Backup degli screenshot**:
   ```bash
   tar -czf screenshots_backup_$(date +%Y%m%d).tar.gz screenshots/
   ```

## Sicurezza

⚠️ **IMPORTANTE**:

- Non committare il file `.env` su Git
- Proteggi la chiave API DeepSeek
- Limita l'accesso alla directory screenshots
- Usa variabili d'ambiente sicure in produzione

## Note sulle operazioni a 5 minuti

Il bot è configurato per richiedere a DeepSeek AI operazioni che si chiudono entro **massimo 5 minuti**, indipendentemente dall'intervallo di richiesta del bot.

Questo significa:
- Se `INTERVAL=10`, il bot chiede analisi ogni 10 minuti
- Ma ogni operazione suggerita deve chiudersi entro 5 minuti
- Stop loss e take profit sono calibrati per operazioni ultra-brevi
- Focus sul timeframe 1 minuto per il momentum immediato

## Supporto

Per problemi o domande:
- Controlla i log: `docker compose logs`
- Verifica la configurazione: `docker compose config`
- Consulta il README.md principale per dettagli sul bot
