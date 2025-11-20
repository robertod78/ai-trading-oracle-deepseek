#!/bin/bash
set -e

echo "=========================================="
echo "🤖 Trading Bot - Docker Container"
echo "=========================================="
echo ""

# Verifica che la chiave API sia impostata
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ ERRORE: DEEPSEEK_API_KEY non impostata!"
    echo ""
    echo "Imposta la variabile d'ambiente nel file .env o docker-compose.yaml"
    exit 1
fi

echo "✅ Configurazione:"
echo "   - Simbolo: $SYMBOL"
echo "   - Broker: $BROKER"
echo "   - Intervallo: $INTERVAL minuti"
echo "   - Directory screenshots: $SCREENSHOTS_DIR"
echo "   - Modalità: $([ "$RUN_ONCE" = "true" ] && echo "Singola esecuzione" || echo "Loop continuo")"
echo ""

# Costruisci il comando
CMD="python3 trading_bot.py --symbol $SYMBOL --broker $BROKER --interval $INTERVAL --screenshots-dir $SCREENSHOTS_DIR"

# Aggiungi flag --once se richiesto
if [ "$RUN_ONCE" = "true" ]; then
    CMD="$CMD --once"
fi

echo "🚀 Avvio trading bot..."
echo ""

# Esegui il bot
exec $CMD
