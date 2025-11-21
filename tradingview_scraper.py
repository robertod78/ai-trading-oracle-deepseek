"""
Modulo per catturare screenshot di TradingView con indicatori tecnici
Versione Playwright - Molto più stabile e semplice in Docker
"""
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import os


class TradingViewScraper:
    """Classe per catturare screenshot di grafici TradingView usando Playwright"""
    
    def __init__(self, symbol="XAUUSD", broker="EIGHTCAP"):
        """
        Inizializza lo scraper
        
        Args:
            symbol: Simbolo del CFD (es. XAUUSD)
            broker: Broker (es. EIGHTCAP)
        """
        self.symbol = symbol
        self.broker = broker
        self.playwright = None
        self.browser = None
        self.page = None
        
    def _init_browser(self):
        """Inizializza Playwright e il browser"""
        self.playwright = sync_playwright().start()
        
        # Playwright gestisce automaticamente il browser!
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
            ]
        )
        
        # Crea un nuovo contesto browser con viewport specifico
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1200},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = context.new_page()
        print(f"    ✓ Browser Playwright inizializzato")
        
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
        # Attesa iniziale per caricamento
        time.sleep(10)
        
        try:
            # Chiudi popup con Escape
            for _ in range(5):
                self.page.keyboard.press('Escape')
                time.sleep(0.3)
            
            # Rimuovi dialog/modal con JavaScript
            self.page.evaluate("""
                // Rimuovi tutti i dialog
                document.querySelectorAll('[role="dialog"]').forEach(el => el.remove());
                
                // Rimuovi modal wrapper
                document.querySelectorAll('[class*="modal"]').forEach(el => {
                    if (!el.querySelector('canvas')) el.remove();
                });
                
                // Rimuovi overlay/backdrop
                document.querySelectorAll('[class*="overlay"], [class*="backdrop"]').forEach(el => el.remove());
            """)
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
            # Inizializza browser se necessario
            if self.page is None:
                self._init_browser()
            
            # Costruisci URL con indicatori
            url = self._build_url_with_studies(timeframe)
            
            # Carica pagina
            print(f"  Caricamento con indicatori pre-configurati...")
            self.page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Attendi caricamento e pulisci
            self._wait_for_load_and_clean()
            
            print(f"  ✓ Grafico caricato")
            
            # Cattura screenshot - Playwright lo fa in modo molto più affidabile!
            print(f"  📸 Cattura screenshot...")
            self.page.screenshot(path=output_path, full_page=False)
            
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
            "60min": 60,
            "15min": 15,
            "1min": 1
        }
        
        screenshots = {}
        
        print("="*70)
        print(f"🚀 CATTURA SCREENSHOT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Simbolo: {self.broker}:{self.symbol}")
        print(f"   Indicatori: EMA 9, MACD, RSI (pre-caricati)")
        print(f"   Engine: Playwright (stabile e affidabile)")
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
        """Chiude il browser e Playwright"""
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        
        if self.playwright:
            try:
                self.playwright.stop()
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
