#!/bin/bash
# Quick Start Script per Trading Bot Docker

set -e

echo "=========================================="
echo "🐳 Trading Bot - Docker Quick Start"
echo "=========================================="
echo ""

# Verifica Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non trovato!"
    echo ""
    echo "Installa Docker con:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    exit 1
fi

# Verifica Docker Compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose non trovato!"
    echo ""
    echo "Installa Docker Compose plugin con:"
    echo "  sudo apt-get install docker-compose-plugin"
    exit 1
fi

echo "✅ Docker installato: $(docker --version)"
echo "✅ Docker Compose installato: $(docker compose version)"
echo ""

# Verifica file .env
if [ ! -f .env ]; then
    echo "⚠️  File .env non trovato!"
    echo ""
    echo "Creazione .env da template..."
    
    if [ -f .env.template ]; then
        cp .env.template .env
        echo "✅ File .env creato"
        echo ""
        echo "⚠️  IMPORTANTE: Modifica .env e inserisci la tua DEEPSEEK_API_KEY!"
        echo ""
        echo "Apri il file con:"
        echo "  nano .env"
        echo ""
        read -p "Premi INVIO dopo aver configurato .env..."
    else
        echo "❌ Template .env.template non trovato!"
        exit 1
    fi
fi

# Verifica che DEEPSEEK_API_KEY sia impostata
source .env
if [ -z "$DEEPSEEK_API_KEY" ] || [ "$DEEPSEEK_API_KEY" = "sk-your-deepseek-api-key-here" ]; then
    echo "❌ DEEPSEEK_API_KEY non configurata in .env!"
    echo ""
    echo "Modifica .env e inserisci la tua chiave API:"
    echo "  nano .env"
    exit 1
fi

echo "✅ Configurazione .env trovata"
echo ""

# Crea directory screenshots se non esiste
mkdir -p screenshots
echo "✅ Directory screenshots pronta"
echo ""

# Menu
echo "Seleziona modalità di avvio:"
echo ""
echo "  1) Build e avvio in background (loop continuo)"
echo "  2) Build e avvio in foreground (vedi log in tempo reale)"
echo "  3) Solo build (senza avvio)"
echo "  4) Esecuzione singola (analisi una volta sola)"
echo "  5) Visualizza log di container già avviato"
echo "  6) Stop del container"
echo ""
read -p "Scelta [1-6]: " choice

case $choice in
    1)
        echo ""
        echo "🔨 Build dell'immagine..."
        docker compose build
        echo ""
        echo "🚀 Avvio in background..."
        docker compose up -d
        echo ""
        echo "✅ Bot avviato!"
        echo ""
        echo "Comandi utili:"
        echo "  - Visualizza log: docker compose logs -f"
        echo "  - Stop bot: docker compose down"
        echo "  - Riavvia: docker compose restart"
        ;;
    2)
        echo ""
        echo "🔨 Build dell'immagine..."
        docker compose build
        echo ""
        echo "🚀 Avvio in foreground (Ctrl+C per fermare)..."
        docker compose up
        ;;
    3)
        echo ""
        echo "🔨 Build dell'immagine..."
        docker compose build
        echo ""
        echo "✅ Build completato!"
        echo ""
        echo "Avvia con: docker compose up -d"
        ;;
    4)
        echo ""
        echo "🔨 Build dell'immagine..."
        docker compose build
        echo ""
        echo "🚀 Esecuzione singola..."
        docker compose run --rm -e RUN_ONCE=true trading-bot
        ;;
    5)
        echo ""
        echo "📋 Log del container (Ctrl+C per uscire)..."
        docker compose logs -f
        ;;
    6)
        echo ""
        echo "🛑 Stop del container..."
        docker compose down
        echo ""
        echo "✅ Container fermato!"
        ;;
    *)
        echo ""
        echo "❌ Scelta non valida!"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ Operazione completata!"
echo "=========================================="
