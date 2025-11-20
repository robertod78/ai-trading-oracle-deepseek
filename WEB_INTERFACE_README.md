# 🌐 Interfaccia Web - AI Trading Oracle

## 🎯 Nuove Funzionalità

### 1. **Interfaccia Web con Log in Tempo Reale**
- Dashboard accessibile su **http://localhost:5555**
- Visualizzazione log in tempo reale con **Server-Sent Events**
- Design moderno con gradiente viola e effetti glassmorphism
- Auto-scroll configurabile
- Colorazione automatica dei log (successo, errore, warning, info)

### 2. **Volume Mapping per Sviluppo Live**
- Tutti i file `.py` sono mappati dal host al container
- Modifica i file sul tuo computer → cambiano immediatamente nel container
- Non serve ricostruire l'immagine Docker per ogni modifica!

### 3. **Auto-Reload con Uvicorn**
- Uvicorn monitora i file Python
- Quando modifichi un file `.py`, l'app si riavvia automaticamente
- Sviluppo rapido senza dover riavviare manualmente il container

---

## 🚀 Come Usare

### Avvio Normale

```bash
# 1. Configura .env
echo "DEEPSEEK_API_KEY=sk-your-key" > .env

# 2. Avvia il container
docker compose up -d

# 3. Apri il browser
open http://localhost:5555
```

### Sviluppo con Modifiche Live

```bash
# 1. Avvia il container
docker compose up -d

# 2. Modifica i file Python sul tuo computer
nano app.py
nano trading_bot.py
nano tradingview_scraper.py
nano deepseek_analyzer.py

# 3. Uvicorn rileva le modifiche e riavvia automaticamente!
# Guarda i log per vedere il reload:
docker compose logs -f
```

### Vedere i Log

```bash
# Log del container
docker compose logs -f

# Oppure apri il browser
open http://localhost:5555
```

---

## 📂 File Mappati (Volume Mapping)

I seguenti file sono mappati dalla directory locale al container:

```yaml
volumes:
  - ./screenshots:/app/screenshots          # Screenshot persistenti
  - ./app.py:/app/app.py                   # Flask app
  - ./trading_bot.py:/app/trading_bot.py   # Bot principale
  - ./tradingview_scraper.py:/app/tradingview_scraper.py
  - ./deepseek_analyzer.py:/app/deepseek_analyzer.py
  - ./templates:/app/templates              # Template HTML
```

**Cosa significa?**
- Modifichi `app.py` sul tuo computer → cambia immediatamente in `/app/app.py` nel container
- Uvicorn rileva il cambiamento → riavvia l'app
- Vedi le modifiche in tempo reale nel browser!

---

## 🎨 Interfaccia Web

### Pagina Principale

![Dashboard](https://via.placeholder.com/800x400?text=AI+Trading+Oracle+Dashboard)

**Elementi:**
- **Status Bar**: Mostra stato, simbolo, broker, intervallo, ultimo aggiornamento
- **Log Container**: Log in tempo reale con colorazione automatica
- **Auto-Scroll Toggle**: Pulsante per attivare/disattivare lo scroll automatico

### API Endpoints

#### `GET /`
Pagina principale con interfaccia web

#### `GET /logs`
Stream di log in tempo reale (Server-Sent Events)

#### `GET /api/status`
Stato del bot in formato JSON

```json
{
  "status": "running",
  "symbol": "XAUUSD",
  "broker": "EIGHTCAP",
  "interval": "10",
  "timestamp": "2025-11-20T16:30:00"
}
```

#### `GET /api/logs/history`
Cronologia degli ultimi 100 log

```json
{
  "logs": [
    "[2025-11-20 16:30:00] 🚀 Avvio Trading Bot",
    "[2025-11-20 16:30:05] ✅ Screenshot catturati: 3/3",
    ...
  ]
}
```

---

## 🔧 Configurazione Avanzata

### Cambiare Porta

Modifica `docker-compose.yaml`:

```yaml
ports:
  - "8080:5555"  # Ora accessibile su http://localhost:8080
```

### Disabilitare Auto-Reload

Modifica `docker-entrypoint.sh`:

```bash
# Rimuovi --reload
exec uvicorn app:app \
    --host 0.0.0.0 \
    --port 5555 \
    --log-level info
```

### Aggiungere Altri File Mappati

Modifica `docker-compose.yaml`:

```yaml
volumes:
  - ./screenshots:/app/screenshots
  - ./nuovo_file.py:/app/nuovo_file.py  # Aggiungi qui
```

---

## 🐛 Troubleshooting

### Il browser non si connette

```bash
# Verifica che il container sia in esecuzione
docker ps

# Verifica i log
docker compose logs -f

# Verifica che la porta sia esposta
docker port trading-bot
```

### Le modifiche ai file non vengono rilevate

```bash
# Verifica i volume mapping
docker inspect trading-bot | grep -A 10 Mounts

# Riavvia il container
docker compose restart
```

### Errore "Address already in use"

```bash
# Trova il processo che usa la porta 5555
lsof -i :5555

# Oppure cambia porta in docker-compose.yaml
ports:
  - "5556:5555"
```

---

## 📊 Architettura

```
┌─────────────────────────────────────────────────┐
│  Browser (http://localhost:5555)                │
└────────────────┬────────────────────────────────┘
                 │ HTTP / SSE
┌────────────────▼────────────────────────────────┐
│  Flask App (app.py)                             │
│  - Interfaccia web                              │
│  - API REST                                     │
│  - Server-Sent Events per log streaming        │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Trading Bot (trading_bot.py)                   │
│  - Ciclo principale                             │
│  - Coordinamento                                │
└────┬───────────┬────────────────────────────────┘
     │           │
     │           └──────────────────────────┐
     │                                      │
┌────▼────────────────────┐  ┌─────────────▼──────────────┐
│  TradingView Scraper    │  │  DeepSeek Analyzer         │
│  (Playwright)           │  │  (Vision API)              │
│  - Cattura screenshot   │  │  - Analisi AI              │
└─────────────────────────┘  └────────────────────────────┘
```

---

## 🎯 Workflow di Sviluppo

1. **Avvia il container**
   ```bash
   docker compose up -d
   ```

2. **Apri il browser**
   ```bash
   open http://localhost:5555
   ```

3. **Modifica i file Python**
   ```bash
   nano trading_bot.py
   # Salva le modifiche
   ```

4. **Uvicorn rileva le modifiche**
   - Vedi nel browser: "INFO: Detected file change in '/app/trading_bot.py'"
   - L'app si riavvia automaticamente

5. **Verifica le modifiche**
   - Guarda i log nel browser
   - Testa le nuove funzionalità

6. **Commit quando sei soddisfatto**
   ```bash
   git add trading_bot.py
   git commit -m "Fix: ..."
   git push
   ```

---

## 💡 Tips

### Sviluppo Rapido

```bash
# Terminale 1: Log del container
docker compose logs -f

# Terminale 2: Modifica file
nano app.py

# Browser: Vedi i log in tempo reale
open http://localhost:5555
```

### Debug

```python
# Aggiungi print() nel codice
def analyze_charts(self, screenshots):
    print(f"🐛 DEBUG: screenshots = {screenshots}")
    # ...

# I print appariranno nei log del browser!
```

### Performance

- I log vengono limitati a 500 righe nel browser
- Il container mantiene tutti i log (max 10MB × 3 file)
- Gli screenshot vengono salvati su disco (persistenti)

---

## 🎉 Vantaggi

✅ **Sviluppo veloce**: Modifiche live senza rebuild  
✅ **Debug facile**: Log in tempo reale nel browser  
✅ **Interfaccia moderna**: Dashboard professionale  
✅ **Persistenza**: Screenshot salvati su disco  
✅ **Scalabile**: Facile aggiungere nuove API  

---

## 📝 Note

- **Uvicorn** è un server ASGI ad alte prestazioni
- **Flask** gestisce le route e il rendering HTML
- **Server-Sent Events** (SSE) per streaming log unidirezionale
- **Volume mapping** permette modifiche live dei file
- **Auto-reload** riavvia l'app quando i file cambiano

---

## 🚀 Prossimi Passi

- [ ] Aggiungere autenticazione (login)
- [ ] Salvare segnali di trading in database
- [ ] Grafici storici delle performance
- [ ] Notifiche push per nuovi segnali
- [ ] API per integrazione con broker

---

**Buon trading! 🤖📈**
