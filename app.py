"""
Trading Bot - Flask Web Application
Interfaccia web per visualizzare i log in tempo reale
"""
from flask import Flask, render_template, Response, jsonify
from datetime import datetime, timedelta
import threading
import queue
import time
import os
import sys
from io import StringIO

# Import delle funzioni del trading bot
from tradingview_scraper import TradingViewScraper
from deepseek_analyzer import DeepSeekAnalyzer

app = Flask(__name__)

# Coda per i log
log_queue = queue.Queue()
bot_thread = None
bot_running = False
current_price_global = None  # Ultimo prezzo conosciuto

class LogCapture:
    """Cattura i log e li mette nella coda"""
    def __init__(self):
        self.logs = []
        self.original_stdout = sys.stdout
    
    def write(self, message):
        if message.strip():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message.strip()}"
            self.logs.append(log_entry)
            log_queue.put(log_entry)
            # Scrivi anche su stdout originale
            self.original_stdout.write(message)
    
    def flush(self):
        self.original_stdout.flush()

# Inizializza il log capture
log_capture = LogCapture()

def log_message(message):
    """Helper per loggare messaggi"""
    print(message)

def print_signal(signal: dict):
    """Stampa il segnale di trading in modo formattato"""
    log_message("\n" + "="*70)
    log_message(f"📊 SEGNALE DI TRADING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("="*70)
    log_message(f"\n🔔 Operazione:     {signal['operazione'].upper()}")
    log_message(f"📦 Lotto:          {signal['lotto']}")
    log_message(f"🛑 Stop Loss:      {signal['stop_loss']}")
    log_message(f"🎯 Take Profit:    {signal['take_profit']}")
    log_message(f"\n💡 Spiegazione:")
    log_message(f"   {signal['spiegazione']}")
    log_message("\n" + "="*70 + "\n")

def run_analysis_cycle(symbol: str, broker: str, deepseek_api_key: str, 
                       screenshots_dir: str = "screenshots"):
    """Esegue un ciclo completo di analisi"""
    log_message(f"\n🚀 Avvio ciclo di analisi - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"   Simbolo: {symbol}")
    log_message(f"   Broker: {broker}")
    
    # Inizializza scraper
    scraper = TradingViewScraper(symbol=symbol, broker=broker)
    
    try:
        # Cattura screenshot ed estrai prezzo corrente
        log_message("\n📸 Cattura screenshot in corso...")
        screenshots, current_price = scraper.capture_all_timeframes(output_dir=screenshots_dir)
        
        # Verifica che tutti gli screenshot siano stati catturati
        missing = [tf for tf, path in screenshots.items() if path is None]
        if missing:
            log_message(f"⚠️  Attenzione: screenshot mancanti per timeframe: {', '.join(missing)}")
        
        available_screenshots = {tf: path for tf, path in screenshots.items() if path is not None}
        
        if not available_screenshots:
            log_message("❌ Nessuno screenshot disponibile per l'analisi")
            return False
        
        log_message(f"✅ Screenshot catturati: {len(available_screenshots)}/3")
        for tf, path in available_screenshots.items():
            log_message(f"   - {tf}: {path}")
        
        # Mostra ultimo prezzo conosciuto
        if current_price:
            global current_price_global
            current_price_global = current_price
            log_message(f"\n💰 Ultimo prezzo conosciuto: {current_price}")
        
        # Analizza con DeepSeek
        log_message("\n🤖 Analisi AI in corso...")
        analyzer = DeepSeekAnalyzer(api_key=deepseek_api_key)
        signal = analyzer.analyze_charts(available_screenshots, current_price=current_price, symbol=symbol)
        
        if signal:
            log_message("✅ Segnale ricevuto con successo")
            print_signal(signal)
            return True
        else:
            log_message("❌ Errore nell'analisi: nessun segnale ricevuto")
            return False
            
    except Exception as e:
        log_message(f"❌ Errore durante il ciclo di analisi: {e}")
        return False
    finally:
        scraper.close()

def run_bot():
    """Esegue il bot in un thread separato"""
    global bot_running
    
    # Parametri dal environment
    api_key = os.getenv("FIREWORKS_API_KEY", "")
    symbol = os.getenv("SYMBOL", "XAUUSD")
    broker = os.getenv("BROKER", "EIGHTCAP")
    interval = int(os.getenv("INTERVAL", "10"))
    screenshots_dir = os.getenv("SCREENSHOTS_DIR", "/app/screenshots")
    
    if not api_key:
        log_message("❌ ERRORE: FIREWORKS_API_KEY non configurata!")
        return
    
    log_message("="*70)
    log_message("🤖 TRADING BOT - Analisi automatica CFD con DeepSeek AI")
    log_message("="*70)
    log_message(f"\nConfigurazione:")
    log_message(f"  - Simbolo: {symbol}")
    log_message(f"  - Broker: {broker}")
    log_message(f"  - Intervallo: {interval} minuti")
    log_message(f"  - Directory screenshots: {screenshots_dir}")
    log_message("")
    
    bot_running = True
    cycle = 0
    
    while bot_running:
        cycle += 1
        
        log_message("="*70)
        log_message(f"🔄 CICLO #{cycle}")
        log_message("="*70)
        log_message("")
        
        try:
            # Esegui ciclo di analisi
            success = run_analysis_cycle(symbol, broker, api_key, screenshots_dir)
            
            if success:
                log_message("✅ Ciclo completato con successo")
            else:
                log_message("⚠️  Ciclo #%d completato con errori" % cycle)
            
        except Exception as e:
            log_message(f"❌ Errore nel ciclo: {e}")
        
        log_message("")
        next_time = datetime.now()
        next_time = next_time.replace(second=0, microsecond=0)
        next_time += timedelta(minutes=interval)
        
        log_message(f"⏳ Prossima analisi alle {next_time.strftime('%H:%M:%S')} ({interval} minuti)")
        log_message(f"   Premi Ctrl+C per terminare")
        log_message("")
        
        # Attendi intervallo
        time.sleep(interval * 60)

@app.route('/')
def index():
    """Pagina principale con interfaccia web"""
    return render_template('index.html')

@app.route('/logs')
def stream_logs():
    """Stream dei log in tempo reale (Server-Sent Events)"""
    def generate():
        while True:
            try:
                # Ottieni log dalla coda (con timeout)
                log_entry = log_queue.get(timeout=1)
                yield f"data: {log_entry}\n\n"
            except queue.Empty:
                # Invia heartbeat per mantenere la connessione
                yield f"data: \n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/status')
def status():
    """API per ottenere lo stato del bot"""
    return jsonify({
        'status': 'running' if bot_running else 'stopped',
        'symbol': os.getenv('SYMBOL', 'XAUUSD'),
        'broker': os.getenv('BROKER', 'EIGHTCAP'),
        'interval': os.getenv('INTERVAL', '10'),
        'current_price': current_price_global,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/logs/history')
def logs_history():
    """API per ottenere la cronologia dei log"""
    return jsonify({
        'logs': log_capture.logs[-100:]  # Ultimi 100 log
    })

def start_bot_thread():
    """Avvia il bot in un thread separato"""
    global bot_thread
    
    # Reindirizza stdout al log capture
    sys.stdout = log_capture
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

# Avvia il bot quando l'app viene caricata
start_bot_thread()

if __name__ == '__main__':
    # Avvia Flask
    app.run(host='0.0.0.0', port=5555, debug=False)
