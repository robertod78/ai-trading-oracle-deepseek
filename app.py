"""
Trading Bot - Flask Web Application
Interfaccia web per visualizzare i log in tempo reale
"""
from flask import Flask, render_template, Response, jsonify
from datetime import datetime
import threading
import queue
import time
import os
from trading_bot import TradingBot

app = Flask(__name__)

# Coda per i log
log_queue = queue.Queue()
bot_instance = None
bot_thread = None

class LogCapture:
    """Cattura i log e li mette nella coda"""
    def __init__(self):
        self.logs = []
    
    def write(self, message):
        if message.strip():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
            self.logs.append(log_entry)
            log_queue.put(log_entry)
    
    def flush(self):
        pass

# Inizializza il log capture
log_capture = LogCapture()

def run_bot():
    """Esegue il bot in un thread separato"""
    global bot_instance
    
    # Parametri dal environment
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    symbol = os.getenv("SYMBOL", "XAUUSD")
    broker = os.getenv("BROKER", "EIGHTCAP")
    interval = int(os.getenv("INTERVAL", "10"))
    screenshots_dir = os.getenv("SCREENSHOTS_DIR", "/app/screenshots")
    
    if not api_key:
        log_capture.write("❌ ERRORE: DEEPSEEK_API_KEY non configurata!")
        return
    
    log_capture.write(f"🚀 Avvio Trading Bot")
    log_capture.write(f"   Simbolo: {symbol}")
    log_capture.write(f"   Broker: {broker}")
    log_capture.write(f"   Intervallo: {interval} minuti")
    log_capture.write("")
    
    bot_instance = TradingBot(
        api_key=api_key,
        symbol=symbol,
        broker=broker,
        screenshots_dir=screenshots_dir
    )
    
    cycle = 0
    while True:
        cycle += 1
        
        log_capture.write("=" * 70)
        log_capture.write(f"🔄 CICLO #{cycle}")
        log_capture.write("=" * 70)
        log_capture.write("")
        
        try:
            # Esegui ciclo di analisi
            bot_instance.run_cycle()
            
        except Exception as e:
            log_capture.write(f"❌ Errore nel ciclo: {e}")
        
        log_capture.write("")
        next_time = datetime.now()
        next_time = next_time.replace(second=0, microsecond=0)
        from datetime import timedelta
        next_time += timedelta(minutes=interval)
        
        log_capture.write(f"⏳ Prossima analisi alle {next_time.strftime('%H:%M:%S')} ({interval} minuti)")
        log_capture.write(f"   Premi Ctrl+C per terminare")
        log_capture.write("")
        
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
        'status': 'running' if bot_thread and bot_thread.is_alive() else 'stopped',
        'symbol': os.getenv('SYMBOL', 'XAUUSD'),
        'broker': os.getenv('BROKER', 'EIGHTCAP'),
        'interval': os.getenv('INTERVAL', '10'),
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
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

if __name__ == '__main__':
    # Avvia il bot in background
    start_bot_thread()
    
    # Avvia Flask
    app.run(host='0.0.0.0', port=5555, debug=False)
