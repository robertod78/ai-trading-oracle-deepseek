#!/usr/bin/env python3
"""
Trading Bot - Analisi automatica di grafici CFD tramite DeepSeek AI

Cattura screenshot di TradingView ogni 10 minuti e analizza i grafici
per generare segnali di trading.
"""
import os
import sys
import time
import argparse
from datetime import datetime
from tradingview_scraper import TradingViewScraper
from deepseek_analyzer import DeepSeekAnalyzer


def print_signal(signal: dict):
    """
    Stampa il segnale di trading in modo formattato
    
    Args:
        signal: Dizionario con il segnale di trading
    """
    print("\n" + "="*70)
    print(f"📊 SEGNALE DI TRADING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print(f"\n🔔 Operazione:     {signal['operazione'].upper()}")
    print(f"📦 Lotto:          {signal['lotto']}")
    print(f"🛑 Stop Loss:      {signal['stop_loss']}")
    print(f"🎯 Take Profit:    {signal['take_profit']}")
    print(f"\n💡 Spiegazione:")
    print(f"   {signal['spiegazione']}")
    print("\n" + "="*70 + "\n")


def run_analysis_cycle(symbol: str, broker: str, deepseek_api_key: str, 
                       screenshots_dir: str = "screenshots"):
    """
    Esegue un ciclo completo di analisi
    
    Args:
        symbol: Simbolo CFD (es. XAUUSD)
        broker: Broker (es. EIGHTCAP)
        deepseek_api_key: Chiave API DeepSeek
        screenshots_dir: Directory per salvare gli screenshot
    
    Returns:
        True se successo, False altrimenti
    """
    print(f"\n🚀 Avvio ciclo di analisi - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Simbolo: {symbol}")
    print(f"   Broker: {broker}")
    
    # Inizializza scraper
    scraper = TradingViewScraper(symbol=symbol, broker=broker)
    
    try:
        # Cattura screenshot ed estrai prezzo corrente
        print("\n📸 Cattura screenshot in corso...")
        screenshots, current_price = scraper.capture_all_timeframes(output_dir=screenshots_dir)
        
        # Verifica che tutti gli screenshot siano stati catturati
        missing = [tf for tf, path in screenshots.items() if path is None]
        if missing:
            print(f"⚠️  Attenzione: screenshot mancanti per timeframe: {', '.join(missing)}")
        
        available_screenshots = {tf: path for tf, path in screenshots.items() if path is not None}
        
        if not available_screenshots:
            print("❌ Nessuno screenshot disponibile per l'analisi")
            return False
        
        print(f"✅ Screenshot catturati: {len(available_screenshots)}/3")
        for tf, path in available_screenshots.items():
            print(f"   - {tf}: {path}")
        
        # Mostra ultimo prezzo conosciuto
        if current_price:
            print(f"\n💰 Ultimo prezzo conosciuto: {current_price}")
        
        # Analizza con DeepSeek
        print("\n🤖 Analisi AI in corso...")
        analyzer = DeepSeekAnalyzer(api_key=deepseek_api_key)
        signal = analyzer.analyze_charts(available_screenshots, current_price=current_price, symbol=symbol)
        
        if signal:
            print("✅ Segnale ricevuto con successo")
            print_signal(signal)
            return True
        else:
            print("❌ Errore nell'analisi: nessun segnale ricevuto")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il ciclo di analisi: {e}")
        return False
    finally:
        scraper.close()


def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(
        description="Trading Bot - Analisi automatica CFD con DeepSeek AI"
    )
    parser.add_argument(
        "--symbol",
        type=str,
        default="XAUUSD",
        help="Simbolo CFD da analizzare (default: XAUUSD)"
    )
    parser.add_argument(
        "--broker",
        type=str,
        default="EIGHTCAP",
        help="Broker (default: EIGHTCAP)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Chiave API Fireworks AI (se non specificata, usa variabile d'ambiente FIREWORKS_API_KEY)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Intervallo in minuti tra le analisi (default: 10)"
    )
    parser.add_argument(
        "--screenshots-dir",
        type=str,
        default="screenshots",
        help="Directory per salvare gli screenshot (default: screenshots)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Esegui una sola analisi e termina (senza loop)"
    )
    
    args = parser.parse_args()
    
    # Ottieni API key
    api_key = args.api_key or os.getenv("FIREWORKS_API_KEY")
    if not api_key:
        print("❌ Errore: Chiave API Fireworks AI non specificata")
        print("   Usa --api-key oppure imposta la variabile d'ambiente FIREWORKS_API_KEY")
        sys.exit(1)
    
    print("="*70)
    print("🤖 TRADING BOT - Analisi automatica CFD con DeepSeek AI")
    print("="*70)
    print(f"\nConfigurazione:")
    print(f"  - Simbolo: {args.symbol}")
    print(f"  - Broker: {args.broker}")
    print(f"  - Intervallo: {args.interval} minuti")
    print(f"  - Directory screenshot: {args.screenshots_dir}")
    print(f"  - Modalità: {'Singola esecuzione' if args.once else 'Loop continuo'}")
    print()
    
    # Crea directory screenshot se non esiste
    os.makedirs(args.screenshots_dir, exist_ok=True)
    
    if args.once:
        # Esegui una sola volta
        run_analysis_cycle(
            symbol=args.symbol,
            broker=args.broker,
            deepseek_api_key=api_key,
            screenshots_dir=args.screenshots_dir
        )
    else:
        # Loop continuo
        print(f"🔄 Avvio loop continuo (ogni {args.interval} minuti)")
        print("   Premi Ctrl+C per terminare\n")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n{'='*70}")
                print(f"🔄 CICLO #{cycle_count}")
                print(f"{'='*70}")
                
                success = run_analysis_cycle(
                    symbol=args.symbol,
                    broker=args.broker,
                    deepseek_api_key=api_key,
                    screenshots_dir=args.screenshots_dir
                )
                
                if success:
                    print(f"✅ Ciclo #{cycle_count} completato con successo")
                else:
                    print(f"⚠️  Ciclo #{cycle_count} completato con errori")
                
                # Attendi intervallo
                next_run = datetime.now().timestamp() + (args.interval * 60)
                next_run_str = datetime.fromtimestamp(next_run).strftime('%H:%M:%S')
                
                print(f"\n⏳ Prossima analisi alle {next_run_str} ({args.interval} minuti)")
                print("   Premi Ctrl+C per terminare")
                
                time.sleep(args.interval * 60)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Bot interrotto dall'utente")
            print(f"   Cicli completati: {cycle_count}")
            print("\n👋 Arrivederci!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
