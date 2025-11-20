#!/bin/bash

echo "=========================================="
echo "🤖 Trading Bot - Docker Container"
echo "=========================================="
echo ""
echo "✅ Configurazione:"
echo "   - Simbolo: ${SYMBOL}"
echo "   - Broker: ${BROKER}"
echo "   - Intervallo: ${INTERVAL} minuti"
echo "   - Directory screenshots: ${SCREENSHOTS_DIR}"
echo "   - Web Interface: http://localhost:5555"
echo ""

# Verifica che la chiave API sia configurata
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  ATTENZIONE: DEEPSEEK_API_KEY non configurata!"
    echo "   Il bot non potrà effettuare analisi AI."
    echo ""
fi

echo "🚀 Avvio Flask app con Gunicorn (auto-reload attivo)..."
echo ""

# Avvia l'applicazione Flask con Gunicorn e auto-reload
exec gunicorn app:app \
    --bind 0.0.0.0:5555 \
    --reload \
    --workers 1 \
    --threads 2 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
