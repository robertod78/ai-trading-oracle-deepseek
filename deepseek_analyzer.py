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
L'operazione DEVE essere SEMPRE PRO-TREND basandoti sul timeframe 1 minuto:
- Se il trend a 1 minuto è RIALZISTA (prezzo sopra EMA, MACD positivo) → SOLO BUY
- Se il trend a 1 minuto è RIBASSISTA (prezzo sotto EMA, MACD negativo) → SOLO SELL
- MAI operare contro il trend del timeframe 1 minuto

⚠️ FORMATO RISPOSTA OBBLIGATORIO:
Devi rispondere SOLO ed ESCLUSIVAMENTE con un oggetto JSON valido.
NO markdown, NO ```json, NO testo prima o dopo, NO emoji nel JSON.
SOLO il JSON puro con questa struttura esatta:

{
    "operazione": "BUY",
    "lotto": 0.01,
    "stop_loss": 2650.50,
    "take_profit": 2655.75,
    "spiegazione": "Testo dettagliato qui"
}

Criteri OBBLIGATORI per operazioni a 5 minuti:
- Stop Loss e Take Profit: DECIDI TU i livelli ottimali basandoti su:
  * Supporti e resistenze visibili
  * Volatilità attuale del mercato
  * Struttura del trend
  * NON ci sono vincoli di pips - usa il tuo giudizio
- Risk/Reward ratio: MINIMO 1:1.5 (preferibile 1:2)
  Esempio: se SL = 10 pips, allora TP = 15 pips minimo (R/R 1:1.5)
- Timeframe 1 minuto: DETERMINA IL TREND - opera SOLO nella direzione del trend
- Timeframe 15 e 60 minuti: CONFERMANO il trend generale
- MAI contro trend: se 1min è rialzista → SOLO BUY, se ribassista → SOLO SELL

🚨 IMPORTANTE: La tua risposta DEVE iniziare con { e finire con }
NO testo prima del JSON, NO testo dopo il JSON, NO code blocks.
SOLO JSON PURO E VALIDO."""

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
