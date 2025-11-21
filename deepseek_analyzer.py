"""
Modulo per analizzare grafici tramite DeepSeek API
"""
import base64
import json
from typing import Dict, List, Optional
import urllib.request
import urllib.parse


class DeepSeekAnalyzer:
    """Classe per analizzare grafici di trading tramite Fireworks AI + DeepSeek V3"""
    
    def __init__(self, api_key: str):
        """
        Inizializza l'analyzer
        
        Args:
            api_key: Chiave API di Fireworks AI
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
        Crea il prompt per l'analisi tecnica
        
        Returns:
            Prompt formattato
        """
        prompt = """Analizza i tre grafici di trading forniti (1 minuto, 15 minuti, 1 ora).

📊 FASE 1 - CALCOLO INDICATORI:
Prima di analizzare, DEVI calcolare mentalmente i seguenti indicatori tecnici basandoti sui dati di prezzo visibili nei grafici:

1. **EMA 9 e EMA 20 (Exponential Moving Average)**:
   - Calcola EMA 9 e EMA 20 per identificare trend di breve e medio termine
   - Identifica se il prezzo è sopra o sotto entrambe le EMA
   - Verifica crossover tra EMA 9 e EMA 20 (segnale di cambio trend)
   - Determina la direzione del trend (EMA in salita/discesa)

2. **MACD (Moving Average Convergence Divergence)**:
   - Calcola MACD line (EMA 12 - EMA 26)
   - Calcola Signal line (EMA 9 del MACD)
   - Identifica crossover, divergenze e posizione rispetto allo zero

3. **RSI (Relative Strength Index a 14 periodi)**:
   - Calcola RSI basandoti sui movimenti di prezzo recenti
   - Identifica zone di ipercomprato (>70), ipervenduto (<30) o neutre
   - Cerca divergenze con il prezzo

📈 FASE 2 - ANALISI TECNICA:
Dopo aver calcolato gli indicatori, analizza:
- Price action (supporti, resistenze, pattern)
- Convergenza/divergenza tra indicatori sui 3 timeframe
- Momentum immediato sul grafico 1 minuto
- Conferma trend dal timeframe 15 minuti
- Contesto generale dal timeframe 1 ora
- Volatilità e spread attuali

⚠️ IMPORTANTE: Devi fornire un segnale di trading che si chiuderà ENTRO UN MASSIMO DI 5 MINUTI.
L'operazione deve essere veloce e precisa con range contenuto (10-15 pips totali).

Rispondi ESCLUSIVAMENTE in formato JSON con questa struttura esatta:
{
    "operazione": "BUY" o "SELL",
    "lotto": numero decimale (considerando un conto di 1000 USD),
    "stop_loss": prezzo in formato decimale,
    "take_profit": prezzo in formato decimale,
    "spiegazione": "Spiegazione dettagliata che DEVE includere: 1) Valori calcolati di EMA 9, EMA 20, MACD e RSI sui 3 timeframe, 2) Analisi price action, 3) Motivi della scelta operativa"
}

Criteri OBBLIGATORI per operazioni a 5 minuti:
- Stop Loss: MASSIMO 5-6 pips per XAUUSD (range stretto per scalping veloce)
- Take Profit: MINIMO 10-12 pips (Risk/Reward ratio 1:2)
  Esempio: se SL = 5 pips, allora TP = 10 pips (R/R 1:2)
- Range totale: 15-18 pips massimo (operazione ultra-veloce)
- Focus su timeframe 15 minuti per trend principale, confermato da 60 minuti
- Timeframe 1 minuto per timing preciso dell'entrata e momentum immediato

Rispondi SOLO con il JSON, senza testo aggiuntivo."""

        return prompt
    
    def analyze_charts(self, screenshots: Dict[str, str], current_price: Optional[float] = None, account_size: float = 1000.0) -> Optional[Dict]:
        """
        Analizza i grafici e restituisce un segnale di trading
        
        Args:
            screenshots: Dizionario con i percorsi degli screenshot {timeframe: path}
            current_price: Prezzo corrente del simbolo (opzionale)
            account_size: Dimensione del conto in USD
            
        Returns:
            Dizionario con il segnale di trading o None se errore
        """
        try:
            # Prepara il contenuto del messaggio - FORMATO OPENAI COMPATIBILE
            prompt_text = self._create_analysis_prompt()
            
            # Aggiungi prezzo corrente se disponibile
            if current_price is not None:
                prompt_text += f"\n\n⚠️ PREZZO CORRENTE (ultimo valore conosciuto): {current_price:.2f}\n"
                prompt_text += "Usa QUESTO prezzo per calcolare Stop Loss e Take Profit precisi.\n"
            
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
            
            # Chiamata API
            print("Invio richiesta a Fireworks AI (Qwen3-VL 235B)...")
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode('utf-8'))
            
            assistant_message = response_data["choices"][0]["message"]["content"]
            
            # Aggiungi risposta alla cronologia
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Mantieni solo gli ultimi 10 messaggi
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            # Parse JSON dalla risposta
            json_text = assistant_message.strip()
            
            # Rimuovi eventuali markdown code blocks
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            elif json_text.startswith("```"):
                json_text = json_text[3:]
            
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            json_text = json_text.strip()
            
            signal = json.loads(json_text)
            
            # Valida i campi richiesti
            required_fields = ["operazione", "lotto", "stop_loss", "take_profit", "spiegazione"]
            for field in required_fields:
                if field not in signal:
                    print(f"Campo mancante nella risposta: {field}")
                    return None
            
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
    
    # Test con screenshot fittizi
    test_screenshots = {
        "1min": "screenshots/XAUUSD_1min.png",
        "15min": "screenshots/XAUUSD_15min.png",
        "60min": "screenshots/XAUUSD_60min.png"
    }
    
    signal = analyzer.analyze_charts(test_screenshots)
    
    if signal:
        print("\nSegnale di trading ricevuto:")
        print(json.dumps(signal, indent=2, ensure_ascii=False))
    else:
        print("Nessun segnale ricevuto o errore nell'analisi")
