#!/bin/bash
#
# Script wrapper per build_anagrafica.py
# Uso: ./run_daily.sh
# Cron: 0 8 * * * /path/to/run_daily.sh

set -euo pipefail

# Directory progetto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# File lock per evitare esecuzioni concorrenti
LOCK_FILE="$SCRIPT_DIR/data/.anagrafica.lock"
LOG_DIR="$SCRIPT_DIR/data/logs"
LOG_FILE="$LOG_DIR/build_anagrafica_$(date +%Y-%m-%d).log"

# Funzione cleanup
cleanup() {
    rm -f "$LOCK_FILE"
}

# Rimuovi lock al termine
trap cleanup EXIT INT TERM

# Verifica lock
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Altra istanza in esecuzione (PID: $PID)" | tee -a "$LOG_FILE"
        exit 1
    else
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Lock file stale, rimuovo" | tee -a "$LOG_FILE"
        rm -f "$LOCK_FILE"
    fi
fi

# Crea lock
echo $$ > "$LOCK_FILE"

# Crea directory log se non esiste
mkdir -p "$LOG_DIR"

# Log inizio
echo "======================================================================" | tee -a "$LOG_FILE"
echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Avvio build anagrafica ARS" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"

# Esegui script Python
if [ -f ".venv/bin/python3" ]; then
    .venv/bin/python3 build_anagrafica.py 2>&1 | tee -a "$LOG_FILE"
    EXIT_CODE=${PIPESTATUS[0]}
else
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Errore: venv non trovato" | tee -a "$LOG_FILE"
    EXIT_CODE=1
fi

# Log fine
echo "======================================================================" | tee -a "$LOG_FILE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Completato con successo" | tee -a "$LOG_FILE"
else
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Completato con errori (exit code: $EXIT_CODE)" | tee -a "$LOG_FILE"
fi
echo "======================================================================" | tee -a "$LOG_FILE"

exit $EXIT_CODE
