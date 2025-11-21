# 📝 Come Modificare il Prompt del Trading Bot

## File Prompt

Il prompt utilizzato dall'AI per analizzare i grafici è contenuto nel file:

```
prompt.txt
```

## Come Modificare

1. **Apri il file `prompt.txt`** con un editor di testo
2. **Modifica il contenuto** secondo le tue esigenze
3. **Salva il file**
4. **Riavvia il bot** - Le modifiche saranno applicate al prossimo ciclo di analisi

## Struttura del Prompt

Il prompt è diviso in sezioni:

### 📊 FASE 1 - ANALISI TECNICA MULTI-TIMEFRAME
- Istruzioni per analizzare i 3 timeframe (1H, 15min, 1min)
- Identificazione trend, supporti, resistenze

### 🎯 FASE 2 - DECISIONE OPERATIVA
- Regole fondamentali (pro-trend, mai contro trend)
- Criteri di probabilità di successo

### 📐 FASE 3 - CALCOLO STOP LOSS E TAKE PROFIT
- Logica SL/TP per BUY e SELL
- Calcolo Risk/Reward ratio
- Esempi concreti

### 🚨 VALIDAZIONE FINALE
- Checklist di controllo prima di generare il segnale
- Validazioni obbligatorie

## Parametri Modificabili

### Range SL/TP
```
📏 DIMENSIONAMENTO SL/TP:
- Range consigliato per 5 minuti: 8-15 pips per SL, 12-25 pips per TP
```

Puoi modificare questi valori per adattarli alla tua strategia.

### Risk/Reward Ratio
```
⚠️ REGOLA AUREA: Distanza TP DEVE essere >= 1.5x Distanza SL
```

Cambia `1.5` con il valore desiderato (es: `2.0` per R/R 1:2).

### Criteri di Validazione
```
4. CALCOLA R/R RATIO:
   ✅ R/R DEVE essere >= 1.5
```

Modifica il valore minimo di R/R accettabile.

## Esempi di Modifiche

### Aumentare il R/R minimo a 1:2
```
⚠️ REGOLA AUREA: Distanza TP DEVE essere >= 2.0x Distanza SL
```

### Ridurre il range SL per operazioni più aggressive
```
- Range consigliato per 5 minuti: 5-10 pips per SL, 10-20 pips per TP
```

### Aggiungere nuove regole
Puoi aggiungere sezioni personalizzate, ad esempio:

```
🔥 REGOLE AGGIUNTIVE:
- Non operare durante news ad alto impatto
- Evita le prime 15 minuti dopo l'apertura del mercato
- Preferisci operazioni durante sessione europea/americana
```

## Note Importanti

⚠️ **Il formato JSON finale deve rimanere invariato**:
```json
{
    "operazione": "BUY",
    "lotto": 0.01,
    "stop_loss": 2653.50,
    "take_profit": 2656.00,
    "spiegazione": "..."
}
```

⚠️ **Non rimuovere la sezione di validazione finale** - È fondamentale per garantire segnali corretti.

⚠️ **Mantieni la logica SL/TP corretta**:
- BUY: SL < Prezzo < TP
- SELL: TP < Prezzo < SL

## Backup

Prima di modificare, fai una copia di backup:
```bash
cp prompt.txt prompt.txt.backup
```

## Ripristino Prompt Originale

Se vuoi tornare al prompt originale, il bot ha un fallback integrato nel codice Python. Elimina `prompt.txt` e il bot userà il prompt di default.

## Test

Dopo aver modificato il prompt, testa con:
```bash
python3 trading_bot.py --once
```

Questo eseguirà un singolo ciclo di analisi senza loop continuo.
