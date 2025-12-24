#!/bin/bash

set -euo pipefail

# Script per generare digest automatici dai video YouTube delle sedute ARS
# Usage: ./scripts/generate_digests.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CSV_FILE="$PROJECT_DIR/data/anagrafica_video.csv"
DIGEST_DIR="$PROJECT_DIR/data/digest"
TEMPLATE_FILE="$PROJECT_DIR/config/digest.yaml"
SCHEMA_FILE="$PROJECT_DIR/config/digest-schema.json"
# LOG_DIR="$PROJECT_DIR/data/logs"
# LOG_FILE="$LOG_DIR/digest_$(date +%Y%m%d_%H%M%S).log"

MODEL="gemini-2.5-flash"
SLEEP_SECONDS=5

# Crea directory se non esistono
mkdir -p "$DIGEST_DIR"
# mkdir -p "$LOG_DIR"

# Funzione log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Trap per cleanup
cleanup() {
    rm -f "$DIGEST_DIR"/.tmp_transcript_*.txt
}
trap cleanup EXIT

log "=== Inizio generazione digest ==="
log "CSV: $CSV_FILE"
log "Output: $DIGEST_DIR"
log "Modello: $MODEL"
log ""

# Contatori
total=0
skipped=0
generated=0
failed=0

# Estrai youtube_id non vuoti usando mlr
while read -r youtube_id; do

    total=$((total + 1))

    OUTPUT_FILE="$DIGEST_DIR/${youtube_id}.json"

    # Skip se file esiste già
    if [ -f "$OUTPUT_FILE" ]; then
        log "SKIP: $youtube_id (già esistente)"
        skipped=$((skipped + 1))
        continue
    fi

    log "PROCESSO: $youtube_id"

    # Scarica trascrizione
    TRANSCRIPT_FILE="$DIGEST_DIR/.tmp_transcript_${youtube_id}.txt"

    if ! qv "https://youtu.be/$youtube_id" --text-only > "$TRANSCRIPT_FILE" 2>&1; then
        log "  ERRORE: Impossibile scaricare trascrizione"
        rm -f "$TRANSCRIPT_FILE"
        failed=$((failed + 1))
        continue
    fi

    # Verifica trascrizione non vuota
    if [ ! -s "$TRANSCRIPT_FILE" ]; then
        log "  ERRORE: Trascrizione vuota"
        rm -f "$TRANSCRIPT_FILE"
        failed=$((failed + 1))
        continue
    fi

    TRANSCRIPT_SIZE=$(wc -c < "$TRANSCRIPT_FILE")
    log "  Trascrizione: $TRANSCRIPT_SIZE bytes"

    # Genera digest
    if cat "$TRANSCRIPT_FILE" | llm -m "$MODEL" -t "$TEMPLATE_FILE" --schema "$SCHEMA_FILE" > "$OUTPUT_FILE" 2>&1; then
        DIGEST_SIZE=$(stat -c%s "$OUTPUT_FILE")
        log "  OK: Digest generato ($DIGEST_SIZE bytes)"
        generated=$((generated + 1))

        # Rimuovi file temporaneo
        rm -f "$TRANSCRIPT_FILE"

        # Pausa tra chiamate
        log "  Pausa $SLEEP_SECONDS secondi..."
        sleep $SLEEP_SECONDS
    else
        log "  ERRORE: Generazione digest fallita"
        rm -f "$OUTPUT_FILE" "$TRANSCRIPT_FILE"
        failed=$((failed + 1))
    fi

done < <(mlr --c2n cut -f youtube_id then filter '$youtube_id=~".+"' "$CSV_FILE")

log ""
log "=== Completato ==="
log "Totale video: $total"
log "Skipped (già esistenti): $skipped"
log "Generati: $generated"
log "Falliti: $failed"
# log "Log: $LOG_FILE"
