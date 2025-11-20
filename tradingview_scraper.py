"""
Modulo per catturare screenshot di TradingView con indicatori tecnici
Versione ottimizzata per Docker con Google Chrome
"""
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os


class TradingViewScraper:
    """Classe per catturare screenshot di grafici TradingView"""
    
    def __init__(self, symbol="XAUUSD", broker="EIGHTCAP"):
        """
        Inizializza lo scraper
        
        Args:
            symbol: Simbolo del CFD (es. XAUUSD)
            broker: Broker (es. EIGHTCAP)
        """
        self.symbol = symbol
        self.broker = broker
        self.driver = None
        
    def _init_driver(self):
        """Inizializza il driver Selenium con Chrome - Versione Docker"""
        chrome_options = Options()
        
        # Opzioni essenziali per Docker
        chrome_options.add_argument('--headless=new')  # Usa nuovo headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        
        # Dimensioni finestra
        chrome_options.add_argument('--window-size=1920,1200')
        
        # Ottimizzazioni per stabilità
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        
        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Usa il path di Google Chrome se disponibile, altrimenti chromium
        chrome_binary = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
        if os.path.exists(chrome_binary):
            chrome_options.binary_location = chrome_binary
        
        # Path del chromedriver
        chromedriver_path = os.environ.get('CHROMEDRIVER', '/usr/bin/chromedriver')
        
        try:
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"    ✓ Chrome inizializzato: {chrome_binary}")
        except Exception as e:
            print(f"    ❌ Errore inizializzazione Chrome: {e}")
            raise
        
    def _build_url_with_studies(self, timeframe):
        """
        Costruisce URL con indicatori pre-caricati tramite parametri studies
        
        Args:
            timeframe: Timeframe (1, 15, 60)
            
        Returns:
            URL completo
        """
        base_url = f"https://it.tradingview.com/chart/?symbol={self.broker}%3A{self.symbol}"
        
        # Parametri per gli indicatori
        studies_param = "STD%3BMoving_Average_Exponential%2CSTD%3BMACD%2CSTD%3BRelative_Strength_Index"
        
        url = f"{base_url}&interval={timeframe}&studies_overrides=%7B%7D&studies={studies_param}"
        
        return url
    
    def _wait_for_load_and_clean(self):
        """Attende caricamento e pulisce l'interfaccia"""
        # Attesa iniziale
        time.sleep(10)
        
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # Chiudi popup con Escape
            for _ in range(5):
                body.send_keys(Keys.ESCAPE)
                time.sleep(0.3)
            
            # Rimuovi dialog/modal con JavaScript
            js_cleanup = """
            // Rimuovi tutti i dialog
            document.querySelectorAll('[role="dialog"]').forEach(el => el.remove());
            
            // Rimuovi modal wrapper
            document.querySelectorAll('[class*="modal"]').forEach(el => {
                if (!el.querySelector('canvas')) el.remove();
            });
            
            // Rimuovi overlay/backdrop
            document.querySelectorAll('[class*="overlay"], [class*="backdrop"]').forEach(el => el.remove());
            """
            self.driver.execute_script(js_cleanup)
            time.sleep(1)
            
        except Exception as e:
            print(f"    Warning cleanup: {str(e)[:40]}")
    
    def capture_screenshot(self, timeframe, output_path):
        """
        Cattura screenshot del grafico
        
        Args:
            timeframe: Timeframe (1, 15, 60 minuti)
            output_path: Percorso dove salvare lo screenshot
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            # Inizializza driver se necessario
            if self.driver is None:
                self._init_driver()
            
            # Costruisci URL con indicatori
            url = self._build_url_with_studies(timeframe)
            
            # Carica pagina
            print(f"  Caricamento con indicatori pre-configurati...")
            self.driver.get(url)
            
            # Attendi caricamento e pulisci
            self._wait_for_load_and_clean()
            
            print(f"  ✓ Grafico caricato")
            
            # Cattura screenshot
            print(f"  📸 Cattura screenshot...")
            self.driver.save_screenshot(output_path)
            
            print(f"  ✅ Salvato: {output_path}")
            return True
            
        except Exception as e:
            print(f"  ❌ Errore: {e}")
            return False
    
    def capture_all_timeframes(self, output_dir="screenshots"):
        """
        Cattura screenshot di tutti i timeframe
        
        Args:
            output_dir: Directory dove salvare gli screenshot
            
        Returns:
            Dizionario con i percorsi degli screenshot {timeframe: path}
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        timeframes = {
            "1min": 1,
            "15min": 15,
            "60min": 60
        }
        
        screenshots = {}
        
        print("="*70)
        print(f"🚀 CATTURA SCREENSHOT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Simbolo: {self.broker}:{self.symbol}")
        print(f"   Indicatori: EMA 9, MACD, RSI (pre-caricati)")
        print("="*70)
        print()
        
        for i, (tf_name, tf_value) in enumerate(timeframes.items(), 1):
            print(f"[{i}/3] " + "━"*50)
            print(f"📊 Timeframe {tf_name}")
            
            output_path = os.path.join(output_dir, f"{timestamp}_{tf_name}.png")
            
            success = self.capture_screenshot(tf_value, output_path)
            screenshots[tf_name] = output_path if success else None
            
            print()
        
        # Riepilogo
        print("="*70)
        print("📸 RIEPILOGO SCREENSHOT:")
        print("="*70)
        
        success_count = sum(1 for path in screenshots.values() if path is not None)
        
        for tf_name, path in screenshots.items():
            status = "✅" if path else "❌"
            path_str = path if path else "ERRORE"
            print(f"   {status} {tf_name:5s} : {path_str}")
        
        print(f"\n   Successo: {success_count}/3")
        print("="*70)
        print()
        
        return screenshots
    
    def close(self):
        """Chiude il browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


if __name__ == "__main__":
    # Test del modulo
    scraper = TradingViewScraper(symbol="XAUUSD", broker="EIGHTCAP")
    
    try:
        screenshots = scraper.capture_all_timeframes()
        
        print("\nScreenshot catturati:")
        for tf, path in screenshots.items():
            if path:
                print(f"  ✅ {tf}: {path}")
            else:
                print(f"  ❌ {tf}: ERRORE")
    finally:
        scraper.close()
