"""
Modulo per catturare screenshot di TradingView con indicatori tecnici
Usa parametri URL per pre-caricare gli indicatori
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
        """Inizializza il driver Selenium con Chrome"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1200')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service('/usr/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
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
        # Format: STD;indicator_name oppure PUB;script_id per script pubblici
        # EMA, MACD, RSI sono indicatori standard
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
            timeframe: Timeframe in minuti (1, 15, 60)
            output_path: Percorso dove salvare lo screenshot
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            if self.driver is None:
                self._init_driver()
            
            # Converti timeframe
            if timeframe == 1:
                tf_str = "1"
            elif timeframe == 15:
                tf_str = "15"
            elif timeframe == 60:
                tf_str = "60"
            else:
                tf_str = str(timeframe)
            
            url = self._build_url_with_studies(tf_str)
            print(f"\n📊 Timeframe {timeframe}min")
            print(f"  Caricamento con indicatori pre-configurati...")
            
            self.driver.get(url)
            
            # Attendi e pulisci
            self._wait_for_load_and_clean()
            
            print(f"  ✓ Grafico caricato")
            print(f"  📸 Cattura screenshot...")
            
            # Screenshot
            self.driver.save_screenshot(output_path)
            print(f"  ✅ Salvato: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Errore: {e}")
            return False
    
    def capture_all_timeframes(self, output_dir="screenshots"):
        """
        Cattura screenshot per tutti i timeframe richiesti
        
        Args:
            output_dir: Directory dove salvare gli screenshot
            
        Returns:
            Dizionario con i percorsi degli screenshot
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        timeframes = [1, 15, 60]
        screenshots = {}
        
        print("="*70)
        print(f"🚀 CATTURA SCREENSHOT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Simbolo: {self.broker}:{self.symbol}")
        print(f"   Indicatori: EMA 9, MACD, RSI (pre-caricati)")
        print("="*70)
        
        for i, tf in enumerate(timeframes, 1):
            print(f"\n[{i}/3] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            filename = f"{timestamp}_{tf}min.png"
            filepath = os.path.join(output_dir, filename)
            
            if self.capture_screenshot(tf, filepath):
                screenshots[f"{tf}min"] = filepath
            else:
                screenshots[f"{tf}min"] = None
            
            # Pausa tra screenshot
            if i < len(timeframes):
                time.sleep(2)
        
        print("\n" + "="*70)
        print("📸 RIEPILOGO SCREENSHOT:")
        print("="*70)
        success_count = 0
        for tf, path in screenshots.items():
            if path:
                print(f"   ✅ {tf:6s}: {path}")
                success_count += 1
            else:
                print(f"   ❌ {tf:6s}: ERRORE")
        print(f"\n   Successo: {success_count}/3")
        print("="*70 + "\n")
        
        return screenshots
    
    def close(self):
        """Chiude il driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


if __name__ == "__main__":
    # Test del modulo
    print("\n🧪 TEST MODULO TRADINGVIEW SCRAPER\n")
    
    scraper = TradingViewScraper(symbol="XAUUSD", broker="EIGHTCAP")
    
    try:
        screenshots = scraper.capture_all_timeframes()
    finally:
        scraper.close()
        print("\n✅ Test completato\n")
