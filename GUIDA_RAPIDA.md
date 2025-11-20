# 🚀 Guida Rapida - Trading Bot

## Installazione veloce

### 1. Installa le dipendenze

```bash
sudo pip3 install selenium openai pillow
sudo apt-get install chromium-chromedriver
```

### 2. Configura la chiave API DeepSeek

**Opzione A - Variabile d'ambiente (consigliata):**
```bash
export DEEPSEEK_API_KEY="sk-la-tua-chiave-api"
```

**Opzione B - Parametro da linea di comando:**
```bash
python3 trading_bot.py --api-key "sk-la-tua-chiave-api" --symbol XAUUSD
```

### 3. Avvia il bot

**Modo più semplice (con script):**
```bash
./start.sh XAUUSD EIGHTCAP 10
```

**Modo manuale:**
```bash
python3 trading_bot.py --symbol XAUUSD --broker EIGHTCAP
```

## Esempi di utilizzo

### Analisi singola (test)
```bash
python3 trading_bot.py --symbol XAUUSD --once
```

### Loop continuo ogni 10 minuti (default)
```bash
python3 trading_bot.py --symbol XAUUSD
```

### Cambio intervallo (ogni 5 minuti)
```bash
python3 trading_bot.py --symbol XAUUSD --interval 5
```

### Analisi di altri simboli
```bash
# EUR/USD
python3 trading_bot.py --symbol EURUSD --broker OANDA

# Bitcoin
python3 trading_bot.py --symbol BTCUSD --broker COINBASE

# S&P 500
python3 trading_bot.py --symbol SPX500 --broker OANDA
```

## Dove trovare gli screenshot

Gli screenshot vengono salvati nella cartella `screenshots/` con questo formato:

```
screenshots/
├── 20251120_143052_1min.png    ← Grafico 1 minuto
├── 20251120_143052_15min.png   ← Grafico 15 minuti
└── 20251120_143052_60min.png   ← Grafico 1 ora
```

Il formato del nome è: `YYYYMMDD_HHMMSS_timeframe.png`

## Output del bot

Il bot stampa i segnali di trading in questo formato:

```
======================================================================
📊 SEGNALE DI TRADING - 2025-11-20 14:30:52
======================================================================

🔔 Operazione:     BUY
📦 Lotto:          0.05
🛑 Stop Loss:      2025.50
🎯 Take Profit:    2028.75

💡 Spiegazione:
   [Analisi tecnica dettagliata fornita da DeepSeek AI]

======================================================================
```

## Interrompere il bot

Premi `Ctrl+C` per interrompere il bot in modalità loop continuo.

## Risoluzione problemi comuni

### "API key not specified"
Imposta la chiave API:
```bash
export DEEPSEEK_API_KEY="sk-la-tua-chiave-api"
```

### "ChromeDriver not found"
Installa ChromeDriver:
```bash
sudo apt-get install chromium-chromedriver
```

### Screenshot vuoti o neri
Aumenta il tempo di attesa in `tradingview_scraper.py` (linea 95):
```python
time.sleep(10)  # Aumenta da 8 a 10 secondi
```

## Parametri disponibili

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `--symbol` | Simbolo CFD da analizzare | XAUUSD |
| `--broker` | Broker | EIGHTCAP |
| `--api-key` | Chiave API DeepSeek | (da env) |
| `--interval` | Intervallo in minuti | 10 |
| `--screenshots-dir` | Directory screenshot | screenshots |
| `--once` | Esecuzione singola | False |

## Note importanti

⚠️ **Disclaimer**: Questo software è fornito solo a scopo educativo. Il trading comporta rischi significativi di perdita. Non utilizzare per operazioni reali senza una validazione approfondita.

## Supporto

Per problemi o domande, consulta il file `README.md` per la documentazione completa.
