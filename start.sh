#!/bin/bash
# Script di avvio rapido per Trading Bot

echo "=========================================="
echo "🤖 Trading Bot - Avvio rapido"
echo "=========================================="
echo ""

# Verifica se la chiave API è impostata
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  ATTENZIONE: Chiave API DeepSeek non trovata!"
    echo ""
    echo "Per usare il bot, devi impostare la chiave API:"
    echo ""
    echo "  export DEEPSEEK_API_KEY='la-tua-chiave-api'"
    echo ""
    echo "Oppure passala come parametro:"
    echo ""
    echo "  python3 trading_bot.py --api-key 'la-tua-chiave-api' --symbol XAUUSD"
    echo ""
    exit 1
fi

# Parametri di default
SYMBOL=${1:-XAUUSD}
BROKER=${2:-EIGHTCAP}
INTERVAL=${3:-10}

echo "Configurazione:"
echo "  Simbolo: $SYMBOL"
echo "  Broker: $BROKER"
echo "  Intervallo: $INTERVAL minuti"
echo ""
echo "Avvio bot..."
echo ""

# Avvia il bot
python3 trading_bot.py \
    --symbol "$SYMBOL" \
    --broker "$BROKER" \
    --interval "$INTERVAL"
