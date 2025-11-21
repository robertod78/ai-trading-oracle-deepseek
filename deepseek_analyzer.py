#!/usr/bin/env python3
"""
DeepSeek Analyzer - Analisi grafici tramite Fireworks AI (Qwen3-VL 235B Instruct)
"""
import base64
import json
import os
import time
import urllib.request
import urllib.error
from typing import Dict, Optional


class DeepSeekAnalyzer:
    """Analizzatore di grafici CFD tramite Fireworks AI"""
    
    def __init__(self, api_key: str):
        """
        Inizializza l'analizzatore
        
        Args:
            api_key: Chiave API Fireworks AI
        """
        self.api_key = api_key
        self.api_url = "https://api.fireworks.ai/inference/v1/chat/completions"
        self.conversation_history = []
    
    def _encode_image(self, image_path: str) -> str:
        """
        Codifica un'immagine in base64
        
        Args:
            image_path: Percorso dell'immagine
            
        Returns:
            Stringa base64 dell'immagine
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _create_analysis_prompt(self) -> str:
        """
        Carica il prompt per l'analisi dei grafici dal file prompt.txt
        
        Returns:
            Prompt formattato
        """
        # Percorso del file prompt (nella stessa directory dello script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_file = os.path.join(script_dir, "prompt.txt")
        
        # Leggi il prompt dal file
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt = f.read()
            return prompt
        except FileNotFoundError:
            print(f"⚠️  File prompt.txt non trovato in {script_dir}")
            print("   Uso prompt di default...")
            # Fallback al prompt di default se il file non esiste
            prompt = """Sei un trader professionista esperto di scalping su XAUUSD (Gold).
Analizza i tre grafici forniti (1 minuto, 15 minuti, 1 ora) e genera un segnale di trading PROFITTEVOLE.

📊 FASE 1 - ANALISI TECNICA MULTI-TIMEFRAME:

1. **Grafico 1 ORA** - Contesto generale:
   - Identifica il trend principale (rialzista/ribassista/laterale)
   - Individua supporti e resistenze chiave
   - Valuta la forza del trend (forte/debole)

2. **Grafico 15 MINUTI** - Trend intermedio:
   - Conferma o diverge dal trend 1H?
   - Ci sono pattern di inversione o continuazione?
   - Dove sono i supporti/resistenze più vicini?

3. **Grafico 1 MINUTO** - Timing di entrata (DECISIVO):
   - Questo timeframe DETERMINA la direzione dell'operazione
   - Trend 1min RIALZISTA → SOLO BUY
   - Trend 1min RIBASSISTA → SOLO SELL
   - Identifica il punto di entrata ottimale
   - Valuta momentum immediato (EMA 9/20, MACD, RSI)

🎯 FASE 2 - DECISIONE OPERATIVA:

REGOLE FONDAMENTALI:
✅ Opera SOLO nella direzione del trend 1 minuto
✅ MAI contro trend
✅ Usa 15min e 1H solo per CONFERMA, non per direzione
✅ Entra solo se hai ALTA PROBABILITÀ di successo (>70%)

📐 FASE 3 - CALCOLO STOP LOSS E TAKE PROFIT:

⚠️ ATTENZIONE: XAUUSD si quota con 2 decimali (es: 2654.32)
1 pip = 0.10 (es: da 2654.30 a 2654.40 = 1 pip)
10 pips = 1.00 (es: da 2654.00 a 2655.00 = 10 pips)

🔴 LOGICA STOP LOSS:
- **BUY**: Stop Loss SOTTO il prezzo di entrata (protegge da discesa)
  Esempio: Prezzo entrata 2654.50 → SL 2653.50 (10 pips sotto)
  
- **SELL**: Stop Loss SOPRA il prezzo di entrata (protegge da salita)
  Esempio: Prezzo entrata 2654.50 → SL 2655.50 (10 pips sopra)

🟢 LOGICA TAKE PROFIT:
- **BUY**: Take Profit SOPRA il prezzo di entrata (guadagno da salita)
  Esempio: Prezzo entrata 2654.50 → TP 2656.00 (15 pips sopra)
  
- **SELL**: Take Profit SOTTO il prezzo di entrata (guadagno da discesa)
  Esempio: Prezzo entrata 2654.50 → TP 2653.00 (15 pips sotto)

📏 DIMENSIONAMENTO SL/TP:
- Range consigliato per 5 minuti: 8-15 pips per SL, 12-25 pips per TP
- Posiziona SL OLTRE il supporto/resistenza più vicino (non esattamente sopra)
- Posiziona TP PRIMA del supporto/resistenza successivo (non esattamente sotto)

🧮 CALCOLO RISK/REWARD RATIO (FONDAMENTALE):

Formula R/R = (Distanza TP) / (Distanza SL)

**Per BUY:**
- Distanza SL = Prezzo Entrata - Stop Loss (quanto RISCHI)
- Distanza TP = Take Profit - Prezzo Entrata (quanto GUADAGNI)
- R/R = (TP - Prezzo) / (Prezzo - SL)

**Per SELL:**
- Distanza SL = Stop Loss - Prezzo Entrata (quanto RISCHI)
- Distanza TP = Prezzo Entrata - Take Profit (quanto GUADAGNI)
- R/R = (Prezzo - TP) / (SL - Prezzo)

⚠️ REGOLA AUREA: Distanza TP DEVE essere >= 1.5x Distanza SL

Esempio CORRETTO (SELL):
- Prezzo: 4068.5
- SL: 4070.5 → Distanza SL = 4070.5 - 4068.5 = 2.0 (rischio 20 pips)
- TP: 4065.5 → Distanza TP = 4068.5 - 4065.5 = 3.0 (guadagno 30 pips)
- R/R = 3.0 / 2.0 = 1.5 ✅

Esempio SBAGLIATO (SELL):
- Prezzo: 4068.5
- SL: 4070.5 → Distanza SL = 2.0 (rischio 20 pips)
- TP: 4067.0 → Distanza TP = 1.5 (guadagno 15 pips) ❌
- R/R = 1.5 / 2.0 = 0.75 ❌ INACCETTABILE!

DEVI SEMPRE: Guadagno >= 1.5x Rischio

💡 ESEMPI CONCRETI:

Esempio 1 - BUY:
Prezzo corrente: 2654.50
Trend 1min: RIALZISTA
Supporto vicino: 2653.80
Resistenza vicina: 2656.20
→ SL: 2653.50 (sotto supporto, 10 pips)
→ TP: 2656.00 (prima resistenza, 15 pips)
→ R/R: 1:1.5 ✅

Esempio 2 - SELL:
Prezzo corrente: 2654.50
Trend 1min: RIBASSISTA
Resistenza vicina: 2655.20
Supporto vicino: 2652.80
→ SL: 2655.50 (sopra resistenza)
→ TP: 2652.50 (prima supporto)
CALCOLO R/R:
  Distanza SL = 2655.50 - 2654.50 = 1.00 (10 pips RISCHIO)
  Distanza TP = 2654.50 - 2652.50 = 2.00 (20 pips GUADAGNO)
  R/R = 2.00 / 1.00 = 2.0 → 1:2 ✅ OTTIMO!

⚠️ FORMATO RISPOSTA OBBLIGATORIO:
Rispondi SOLO con JSON puro, senza testo aggiuntivo, markdown o emoji.
La risposta DEVE iniziare con { e finire con }

{
    "operazione": "BUY",
    "lotto": 0.01,
    "stop_loss": 2653.50,
    "take_profit": 2656.00,
    "spiegazione": "Trend 1min rialzista confermato da 15min. EMA 9 sopra EMA 20, MACD positivo. Supporto a 2653.80, resistenza a 2656.20. SL sotto supporto (10 pips), TP prima resistenza (15 pips). R/R 1:1.5"
}

🚨 VALIDAZIONE FINALE (controlla SEMPRE PRIMA DI RISPONDERE):

1. Direzione corretta? 
   ✅ BUY solo se trend 1min RIALZISTA
   ✅ SELL solo se trend 1min RIBASSISTA

2. SL nella direzione giusta?
   ✅ BUY: SL < Prezzo Corrente
   ✅ SELL: SL > Prezzo Corrente

3. TP nella direzione giusta?
   ✅ BUY: TP > Prezzo Corrente
   ✅ SELL: TP < Prezzo Corrente

4. CALCOLA R/R RATIO:
   - Se BUY: R/R = (TP - Prezzo) / (Prezzo - SL)
   - Se SELL: R/R = (Prezzo - TP) / (SL - Prezzo)
   ✅ R/R DEVE essere >= 1.5
   ❌ Se R/R < 1.5 → AUMENTA TP o RIDUCI SL

5. Range realistico?
   ✅ SL: 8-15 pips
   ✅ TP: 12-30 pips

⚠️ SE ANCHE UNA SOLA VALIDAZIONE FALLISCE:
→ NON rispondere con quel segnale
→ RICOMINCIA il calcolo da zero
→ CORREGGI i valori fino a superare TUTTE le validazioni

Rispondi SOLO con il JSON, niente altro."""
            return prompt
    
    def analyze_charts(self, screenshots: Dict[str, str], current_price: Optional[float] = None, account_size: float = 1000.0, symbol: str = "XAUUSD") -> Optional[Dict]:
        """
        Analizza i grafici e restituisce un segnale di trading
        
        Args:
            screenshots: Dizionario con i percorsi degli screenshot {timeframe: path}
            current_price: Prezzo corrente del simbolo (opzionale)
            account_size: Dimensione del conto in USD
            symbol: Simbolo del CFD (es. XAUUSD)
            
        Returns:
            Dizionario con il segnale di trading o None se errore
        """
        try:
            # Prepara il contenuto del messaggio - FORMATO OPENAI COMPATIBILE
            prompt_text = self._create_analysis_prompt()
            
            # Aggiungi prezzo corrente se disponibile
            if current_price is not None:
                price_line = f"\n\nUltimo valore conosciuto di {symbol}: {current_price:.2f}\n"
                prompt_text += price_line
                print(f"   ✅ Prezzo accodato al prompt: {price_line.strip()}")
            
            content = [
                {
                    "type": "text",
                    "text": prompt_text
                }
            ]
            
            # Aggiungi le immagini nel FORMATO OPENAI (image_url)
            for timeframe in ["1min", "15min", "60min"]:
                if timeframe in screenshots and screenshots[timeframe]:
                    image_base64 = self._encode_image(screenshots[timeframe])
                    content.append({
                        "type": "image_url",  # FORMATO CORRETTO
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    })
            
            if len(content) == 1:  # Solo testo, nessuna immagine
                print("Nessuna immagine disponibile per l'analisi")
                return None
            
            # Crea il messaggio con le immagini
            user_message = {
                "role": "user",
                "content": content
            }
            
            # Aggiungi alla cronologia
            self.conversation_history.append(user_message)
            
            # Prepara la richiesta API con urllib
            payload = json.dumps({
                "model": "accounts/fireworks/models/qwen3-vl-235b-a22b-instruct",
                "messages": self.conversation_history,
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": False
            }).encode('utf-8')
            
            # Crea la richiesta
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            req = urllib.request.Request(
                self.api_url,
                data=payload,
                headers=headers,
                method='POST'
            )
            
            # Chiamata API con retry automatico
            max_retries = 3
            retry_delay = 2  # secondi
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        print(f"Tentativo {attempt + 1}/{max_retries}...")
                    else:
                        print("Invio richiesta a Fireworks AI (Qwen3-VL 235B)...")
                    
                    with urllib.request.urlopen(req, timeout=60) as response:
                        response_data = json.loads(response.read().decode('utf-8'))
                    
                    assistant_message = response_data["choices"][0]["message"]["content"]
                    break  # Successo, esci dal loop
                    
                except urllib.error.HTTPError as e:
                    if e.code == 503 and attempt < max_retries - 1:
                        # Service Unavailable - riprova
                        wait_time = retry_delay * (2 ** attempt)  # backoff esponenziale
                        print(f"⚠️  Servizio temporaneamente non disponibile (503)")
                        print(f"   Riprovo tra {wait_time} secondi...")
                        time.sleep(wait_time)
                    else:
                        # Altro errore HTTP o ultimo tentativo fallito
                        raise
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"⚠️  Errore: {e}")
                        print(f"   Riprovo tra {wait_time} secondi...")
                        time.sleep(wait_time)
                    else:
                        raise
            
            # Aggiungi risposta alla cronologia
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Mantieni solo gli ultimi 10 messaggi
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            # Parse JSON dalla risposta - gestione robusta
            json_text = assistant_message.strip()
            
            # Rimuovi eventuali markdown code blocks
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0]
            
            # Cerca il JSON nella risposta (trova { e } più esterni)
            start_idx = json_text.find('{')
            end_idx = json_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = json_text[start_idx:end_idx+1]
            
            json_text = json_text.strip()
            
            # Debug: mostra il JSON estratto
            print(f"JSON estratto per parsing: {json_text[:200]}...")
            
            signal = json.loads(json_text)
            
            # Valida i campi richiesti
            required_fields = ["operazione", "lotto", "stop_loss", "take_profit", "spiegazione"]
            for field in required_fields:
                if field not in signal:
                    print(f"Campo mancante nella risposta: {field}")
                    return None
            
            # VALIDAZIONE AGGIUNTIVA: controlla logica SL/TP
            if current_price:
                op = signal["operazione"].upper()
                sl = float(signal["stop_loss"])
                tp = float(signal["take_profit"])
                
                print(f"\n🔍 Validazione segnale:")
                print(f"   Operazione: {op}")
                print(f"   Prezzo corrente: {current_price:.2f}")
                print(f"   Stop Loss: {sl:.2f}")
                print(f"   Take Profit: {tp:.2f}")
                
                # Validazione logica BUY
                if op == "BUY":
                    if sl >= current_price:
                        print(f"   ❌ ERRORE: BUY con SL >= prezzo corrente (SL deve essere SOTTO)")
                        return None
                    if tp <= current_price:
                        print(f"   ❌ ERRORE: BUY con TP <= prezzo corrente (TP deve essere SOPRA)")
                        return None
                
                # Validazione logica SELL
                elif op == "SELL":
                    if sl <= current_price:
                        print(f"   ❌ ERRORE: SELL con SL <= prezzo corrente (SL deve essere SOPRA)")
                        return None
                    if tp >= current_price:
                        print(f"   ❌ ERRORE: SELL con TP >= prezzo corrente (TP deve essere SOTTO)")
                        return None
                
                # Calcola R/R ratio
                sl_distance = abs(current_price - sl)
                tp_distance = abs(tp - current_price)
                rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
                
                print(f"   SL distance: {sl_distance:.2f} pips")
                print(f"   TP distance: {tp_distance:.2f} pips")
                print(f"   R/R ratio: 1:{rr_ratio:.2f}")
                
                if rr_ratio < 1.5:
                    print(f"   ⚠️ WARNING: R/R ratio < 1:1.5 (non ottimale)")
                
                print(f"   ✅ Validazione superata")
            
            return signal
            
        except json.JSONDecodeError as e:
            print(f"Errore nel parsing JSON: {e}")
            print(f"Risposta ricevuta: {assistant_message}")
            return None
        except Exception as e:
            print(f"Errore durante l'analisi: {e}")
            return None
    
    def clear_history(self):
        """Pulisce la cronologia della conversazione"""
        self.conversation_history = []


if __name__ == "__main__":
    # Test del modulo
    import os
    
    api_key = os.getenv("FIREWORKS_API_KEY", "your-api-key-here")
    analyzer = DeepSeekAnalyzer(api_key)
    
    # Test con screenshot di esempio
    screenshots = {
        "1min": "screenshots/xauusd_1min.png",
        "15min": "screenshots/xauusd_15min.png",
        "60min": "screenshots/xauusd_60min.png"
    }
    
    signal = analyzer.analyze_charts(screenshots)
    
    if signal:
        print("\n✅ Segnale ricevuto:")
        print(json.dumps(signal, indent=2))
    else:
        print("\n❌ Nessun segnale ricevuto")
