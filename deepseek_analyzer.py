"""
Modulo per analizzare grafici tramite DeepSeek API
"""
import base64
import json
from openai import OpenAI
from typing import Dict, List, Optional


class DeepSeekAnalyzer:
    """Classe per analizzare grafici di trading tramite DeepSeek API"""
    
    def __init__(self, api_key: str):
        """
        Inizializza l'analyzer
        
        Args:
            api_key: Chiave API di DeepSeek
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
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

1. **EMA 9 (Exponential Moving Average a 9 periodi)**:
   - Calcola la media mobile esponenziale degli ultimi 9 periodi
   - Identifica se il prezzo è sopra o sotto l'EMA 9
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
L'operazione deve essere a breve termine, con target e stop loss raggiungibili in 5 minuti o meno.

Rispondi ESCLUSIVAMENTE in formato JSON con questa struttura esatta:
{
    "operazione": "Buy" o "Sell",
    "lotto": numero decimale (considerando un conto di 1000 USD),
    "stop_loss": prezzo in formato decimale,
    "take_profit": prezzo in formato decimale,
    "spiegazione": "Spiegazione dettagliata che DEVE includere: 1) Valori calcolati di EMA 9, MACD e RSI sui 3 timeframe, 2) Analisi price action, 3) Motivi della scelta operativa"
}

Criteri OBBLIGATORI per operazioni a 5 minuti:
- Target di profitto realistico per 5 minuti (pochi pip/punti)
- Stop loss stretto ma ragionevole
- Risk/reward ratio minimo 1:1.5
- Focus principale sul timeframe 1 minuto per momentum immediato

Rispondi SOLO con il JSON, senza testo aggiuntivo."""

        return prompt
    
    def analyze_charts(self, screenshots: Dict[str, str], account_size: float = 1000.0) -> Optional[Dict]:
        """
        Analizza i grafici e restituisce un segnale di trading
        
        Args:
            screenshots: Dizionario con i percorsi degli screenshot {timeframe: path}
            account_size: Dimensione del conto in USD
            
        Returns:
            Dizionario con il segnale di trading o None se errore
        """
        try:
            # Prepara le immagini
            images_content = []
            
            for timeframe in ["1min", "15min", "60min"]:
                if timeframe in screenshots and screenshots[timeframe]:
                    image_base64 = self._encode_image(screenshots[timeframe])
                    images_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    })
            
            if not images_content:
                print("Nessuna immagine disponibile per l'analisi")
                return None
            
            # Crea il messaggio con le immagini
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self._create_analysis_prompt()
                    }
                ] + images_content
            }
            
            # Aggiungi alla cronologia
            self.conversation_history.append(user_message)
            
            # Chiamata API
            print("Invio richiesta a DeepSeek API...")
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Estrai la risposta
            assistant_message = response.choices[0].message.content
            
            # Aggiungi risposta alla cronologia
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Mantieni solo gli ultimi 10 messaggi per evitare context troppo lungo
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            # Parse JSON dalla risposta
            # Rimuovi eventuali markdown code blocks
            json_text = assistant_message.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
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
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")
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


