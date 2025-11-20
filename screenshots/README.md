# Trading Bot - Analisi automatica CFD con DeepSeek AI

Software Python per l'analisi automatica di grafici CFD tramite screenshot di TradingView e intelligenza artificiale DeepSeek.

## Caratteristiche

Il bot cattura automaticamente screenshot di grafici TradingView su tre timeframe diversi:
- **1 minuto**
- **15 minuti**
- **1 ora (60 minuti)**

Ogni 10 minuti (configurabile), il bot:
1. Cattura screenshot dei grafici di trading
2. Invia le immagini all'API DeepSeek per l'analisi
3. Riceve un segnale di trading con:
   - **Operazione**: Buy o Sell
   - **Lotto**: dimensione della posizione (basata su conto da 1000 USD)
   - **Stop Loss**: livello di stop loss
   - **Take Profit**: livello di take profit
   - **Spiegazione**: motivazioni tecniche della scelta

## Requisiti

- Python 3.11+
- Chrome/Chromium browser
- ChromeDriver
- Chiave API DeepSeek

### Dipendenze Python

```bash
sudo pip3 install selenium openai pillow
```

## Installazione

1. Clona o copia i file del progetto:
   - `trading_bot.py` - Programma principale
   - `tradingview_scraper.py` - Modulo per catturare screenshot
   - `deepseek_analyzer.py` - Modulo per analisi AI

2. Installa le dipendenze:
```bash
sudo pip3 install selenium openai pillow
```

3. Installa ChromeDriver (Ubuntu/Debian):
```bash
sudo apt-get install chromium-chromedriver
```

## Configurazione

### Chiave API DeepSeek

Imposta la chiave API come variabile d'ambiente:

```bash
export DEEPSEEK_API_KEY="la-tua-chiave-api"
```

Oppure passala come parametro al comando (vedi sotto).

### Indicatori Tecnici (Opzionale)

Il bot cattura i grafici così come appaiono su TradingView. Per avere gli indicatori EMA 9, MACD e RSI visibili negli screenshot, hai due opzioni:

**Opzione A - Configurazione manuale (consigliata):**
1. Apri TradingView e vai al simbolo desiderato (es. EIGHTCAP:XAUUSD)
2. Aggiungi manualmente gli indicatori:
   - Moving Average Exponential (EMA) con periodo 9
   - MACD (impostazioni standard)
   - RSI (impostazioni standard)
3. Salva il layout come "default" o crea un template
4. Il bot userà automaticamente questo layout

**Opzione B - Analisi senza indicatori:**
Il bot funziona anche senza indicatori visibili. DeepSeek AI è in grado di analizzare i grafici basandosi sulla price action (movimento dei prezzi) e può comunque fornire segnali di trading validi.

## Utilizzo

### Esecuzione base (loop continuo ogni 10 minuti)

```bash
python3 trading_bot.py --symbol XAUUSD --broker EIGHTCAP
```

### Esecuzione singola (una sola analisi)

```bash
python3 trading_bot.py --symbol XAUUSD --broker EIGHTCAP --once
```

### Parametri disponibili

- `--symbol`: Simbolo CFD da analizzare (default: XAUUSD)
- `--broker`: Broker (default: EIGHTCAP)
- `--api-key`: Chiave API DeepSeek (alternativa alla variabile d'ambiente)
- `--interval`: Intervallo in minuti tra le analisi (default: 10)
- `--screenshots-dir`: Directory per salvare gli screenshot (default: screenshots)
- `--once`: Esegui una sola analisi e termina

### Esempi

**Analisi di EUR/USD ogni 5 minuti:**
```bash
python3 trading_bot.py --symbol EURUSD --broker OANDA --interval 5
```

**Analisi singola con chiave API specificata:**
```bash
python3 trading_bot.py --symbol BTCUSD --api-key "sk-xxxxx" --once
```

**Salvare screenshot in directory personalizzata:**
```bash
python3 trading_bot.py --symbol XAUUSD --screenshots-dir /percorso/custom/screenshots
```

## Screenshot

Gli screenshot vengono salvati nella directory specificata (default: `screenshots/`) con il formato:

```
YYYYMMDD_HHMMSS_1min.png
YYYYMMDD_HHMMSS_15min.png
YYYYMMDD_HHMMSS_60min.png
```

Esempio:
- `20251120_143052_1min.png` - Grafico 1 minuto catturato il 20/11/2025 alle 14:30:52
- `20251120_143052_15min.png` - Grafico 15 minuti
- `20251120_143052_60min.png` - Grafico 1 ora

Questo permette di:
- Vedere cronologicamente tutti gli screenshot catturati
- Identificare facilmente data, ora e timeframe
- Conservare uno storico completo delle analisi

## Output

Il bot stampa i segnali di trading ricevuti:

```
======================================================================
📊 SEGNALE DI TRADING - 2025-11-20 14:30:52
======================================================================

🔔 Operazione:     BUY
📦 Lotto:          0.05
🛑 Stop Loss:      2025.50
🎯 Take Profit:    2028.75

💡 Spiegazione:
   Il grafico mostra un trend rialzista confermato su tutti i timeframe.
   L'analisi multi-timeframe indica momentum positivo con supporto forte
   a livelli chiave. Operazione a basso rischio con R/R favorevole.

======================================================================
```

## Interruzione

Per interrompere il bot in modalità loop continuo, premi `Ctrl+C`.

## Note importanti

⚠️ **Disclaimer**: Questo software è fornito solo a scopo educativo e di ricerca. Il trading di CFD comporta rischi significativi di perdita del capitale. Non utilizzare questo bot per operazioni reali senza:
- Una comprensione completa dei rischi del trading
- Una validazione approfondita delle strategie
- Un'adeguata gestione del rischio
- Capitale che puoi permetterti di perdere

⚠️ **Limitazioni tecniche**: 
- TradingView potrebbe limitare l'accesso automatizzato
- Gli indicatori potrebbero non essere sempre visibili negli screenshot
- L'AI fornisce suggerimenti, non garanzie di profitto
- I segnali devono essere sempre valutati criticamente

## Struttura del progetto

```
trading_ai_bot/
├── trading_bot.py              # Programma principale
├── tradingview_scraper.py      # Modulo screenshot TradingView
├── deepseek_analyzer.py        # Modulo analisi DeepSeek AI
├── README.md                   # Questo file
├── GUIDA_RAPIDA.md            # Guida rapida
├── .env.example               # Template configurazione
├── start.sh                   # Script di avvio rapido
└── screenshots/               # Directory screenshot (creata automaticamente)
    ├── 20251120_143052_1min.png
    ├── 20251120_143052_15min.png
    └── 20251120_143052_60min.png
```

## Troubleshooting

### Errore "ChromeDriver not found"
Installa ChromeDriver:
```bash
sudo apt-get install chromium-chromedriver
```

### Errore "API key not specified"
Imposta la variabile d'ambiente:
```bash
export DEEPSEEK_API_KEY="la-tua-chiave-api"
```

### Screenshot vuoti o neri
Aumenta il tempo di attesa nel file `tradingview_scraper.py`:
```python
time.sleep(12)  # Aumenta da 10 a 12 secondi
```

### Gli indicatori non sono visibili
Vedi la sezione "Indicatori Tecnici" sopra per le opzioni di configurazione.

### Errore di autenticazione TradingView
TradingView potrebbe richiedere login per alcuni simboli. Considera di:
- Usare simboli pubblicamente accessibili
- Configurare un account TradingView
- Aumentare i tempi di attesa per permettere caricamenti più lenti

## Licenza

Questo progetto è distribuito senza licenza specifica. Usalo a tuo rischio e pericolo.

## Supporto

Per problemi o domande, consulta la `GUIDA_RAPIDA.md` per istruzioni rapide.
