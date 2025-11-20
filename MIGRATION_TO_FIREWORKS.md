# 🔄 Migrazione a Fireworks AI

## Cosa è cambiato?

Il trading bot ora usa **Fireworks AI** con **DeepSeek V3** invece dell'API DeepSeek diretta.

### Perché?

- ✅ **DeepSeek V3 via Fireworks** supporta immagini tramite "Document Inlining"
- ✅ **Formato compatibile OpenAI** - nessuna modifica al codice necessaria
- ✅ **Più stabile e veloce** - infrastruttura enterprise di Fireworks AI
- ✅ **Stesso modello DeepSeek V3** - stesse capacità di analisi

---

## 🔧 Come Migrare

### 1. Ottieni una API Key Fireworks AI

1. Vai su [https://fireworks.ai](https://fireworks.ai)
2. Registrati o fai login
3. Vai su Dashboard → API Keys
4. Crea una nuova API key
5. Copia la chiave (inizia con `fw_...`)

### 2. Aggiorna il file `.env`

**PRIMA:**
```bash
DEEPSEEK_API_KEY=sk-xxxxx
```

**DOPO:**
```bash
FIREWORKS_API_KEY=fw_xxxxx
```

### 3. Riavvia il container

```bash
docker compose down
docker compose up -d
```

---

## 📝 Modifiche Tecniche

### File Modificati

1. **deepseek_analyzer.py**
   - Base URL: `https://api.fireworks.ai/inference/v1/chat/completions`
   - Model: `accounts/fireworks/models/deepseek-v3`

2. **docker-compose.yaml**
   - Variabile: `FIREWORKS_API_KEY` invece di `DEEPSEEK_API_KEY`

3. **app.py, trading_bot.py, docker-entrypoint.sh**
   - Tutti aggiornati per usare `FIREWORKS_API_KEY`

### Formato Immagini

Il formato delle immagini **NON è cambiato** - Fireworks AI usa lo stesso formato OpenAI:

```python
{
    "type": "image_url",
    "image_url": {
        "url": "data:image/jpeg;base64,..."
    }
}
```

---

## ✅ Vantaggi

| Caratteristica | DeepSeek API | Fireworks AI + DeepSeek V3 |
|----------------|--------------|----------------------------|
| **Supporto Immagini** | ❌ Non disponibile | ✅ Document Inlining |
| **Velocità** | ⚡ Buona | ⚡⚡ Ottima |
| **Stabilità** | ✅ Buona | ✅✅ Enterprise-grade |
| **Formato API** | OpenAI-like | OpenAI compatibile |
| **Modello** | deepseek-chat | deepseek-v3 |

---

## 🆘 Troubleshooting

### Errore: "Invalid API key"

Verifica che la chiave inizi con `fw_` e sia valida su Fireworks AI.

### Errore: "Model not found"

Il modello è: `accounts/fireworks/models/deepseek-v3` (già configurato)

### Errore: "Image too large"

Fireworks AI ha limiti:
- Max 30 immagini per richiesta
- Max 10MB totale per immagini base64
- Max 5MB per immagine URL

---

## 📚 Documentazione

- [Fireworks AI Docs](https://docs.fireworks.ai/)
- [DeepSeek V3 + Document Inlining](https://fireworks.ai/blog/deepseekv3-document-inlining)
- [Vision Models Guide](https://docs.fireworks.ai/guides/querying-vision-language-models)
