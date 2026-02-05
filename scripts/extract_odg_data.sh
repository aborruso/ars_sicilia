#!/bin/bash

################################################################################
# extract_odg_data.sh
#
# Estrae dati strutturati sui disegni di legge dai PDF degli ordini del giorno
# (OdG) delle sedute ARS.
#
# USAGE:
#   ./scripts/extract_odg_data.sh [--reprocess]
#
# INPUT:
#   - data/anagrafica_video.csv (campo odg_url)
#
# OUTPUT:
#   - data/disegni_legge.jsonl (formato JSONL incrementale)
#   - data/logs/odg_pdfs_processed.txt (lista PDF già processati)
#
# DEBUG OPTIONS:
#   --pdf-url <url>     processa solo un PDF specifico
#   --output-dir <dir>  cartella di output (relativa al repo root o assoluta)
#
# DEPENDENCIES:
#   - markitdown (pip install markitdown)
#   - llm CLI (pip install llm)
#
# BEHAVIOR:
#   - Legge URL PDF distinti dal campo odg_url
#   - Salta PDF già elaborati (lista in data/logs/odg_pdfs_processed.txt), a meno di --reprocess
#   - Usa markitdown + llm per estrarre dati strutturati
#   - Genera url_disegno (link ICARO) da legislatura + numero_disegno
#   - Append risultati a data/disegni_legge.jsonl
################################################################################

set -euo pipefail

# Percorsi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CSV_FILE="$PROJECT_DIR/data/anagrafica_video.csv"
OUTPUT_DIR="$PROJECT_DIR/data"
OUTPUT_JSONL="$OUTPUT_DIR/disegni_legge.jsonl"
PROCESSED_LOG="$OUTPUT_DIR/logs/odg_pdfs_processed.txt"

# Schema LLM per estrazione dati
SCHEMA='
titolo_disegno: il titolo del disegno di legge,
numero_disegno: il numero del disegno di legge, solo la parte numerica,
legislatura: il numero romano della legislatura,
data_ora: data e ora della seduta in formato ISO 8601: YYYY-MM-DD HH:MM'

SYSTEM_PROMPT="Estrai SOLO i disegni di legge elencati nella sezione
\"DISCUSSIONE DEI DISEGNI DI LEGGE\" dell'ORDINE DEL GIORNO.

Regole:
- Considera solo l'elenco numerato immediatamente sotto quel titolo.
- Interrompi quando finisce l'elenco, o se compare una nuova sezione,
  \"ALLEGATO\", \"COMUNICAZIONI\", \"INDICE\", o \"DISEGNI DI LEGGE PRESENTATI ED INVIATI\".
- Ignora qualsiasi DDL citato in allegati o comunicazioni.
- Se la sezione non è presente, restituisci zero item."

# Funzione per estrarre URL distinti da CSV
get_distinct_odg_urls() {
    # Salta header, estrai campo odg_url (colonna 4), rimuovi vuoti, distinct
    tail -n +2 "$CSV_FILE" | cut -d',' -f4 | grep -v '^$' | sort -u
}

# Funzione per controllare se un PDF è già stato processato
is_pdf_processed() {
    local pdf_url="$1"
    if [[ -f "$PROCESSED_LOG" ]]; then
        grep -qFx "$pdf_url" "$PROCESSED_LOG"
        return
    fi
    if [[ ! -f "$OUTPUT_JSONL" ]]; then
        return 1  # File non esiste, PDF non processato
    fi
    grep -qF "\"pdf_url\":\"$pdf_url\"" "$OUTPUT_JSONL"
}

# Funzione per convertire legislatura romana in numero
roman_to_arabic() {
    local roman="$1"
    case "$roman" in
        XVIII) echo "18" ;;
        XVII) echo "17" ;;
        XVI) echo "16" ;;
        XV) echo "15" ;;
        XIV) echo "14" ;;
        XIII) echo "13" ;;
        XII) echo "12" ;;
        XI) echo "11" ;;
        X) echo "10" ;;
        IX) echo "9" ;;
        VIII) echo "8" ;;
        VII) echo "7" ;;
        VI) echo "6" ;;
        V) echo "5" ;;
        IV) echo "4" ;;
        III) echo "3" ;;
        II) echo "2" ;;
        I) echo "1" ;;
        *) echo "" ;;
    esac
}

# Funzione per generare URL ICARO
generate_icaro_url() {
    local legislatura_romana="$1"
    local numero_disegno="$2"

    local legislatura_num
    legislatura_num=$(roman_to_arabic "$legislatura_romana")

    if [[ -z "$legislatura_num" || -z "$numero_disegno" ]]; then
        echo ""
        return
    fi

    echo "https://dati.ars.sicilia.it/icaro/default.jsp?icaDB=221&icaQuery=(${legislatura_num}.LEGISL+E+${numero_disegno}.NUMDDL)"
}

# Funzione per processare un PDF
process_pdf() {
    local pdf_url="$1"

    echo "Processing: $pdf_url" >&2

    # Estrai dati con markitdown + llm
    local json_output
    json_output=$(markitdown "$pdf_url" | llm --schema-multi "$SCHEMA" --system "$SYSTEM_PROMPT" 2>/dev/null || echo '{"items":[]}')

    # Parse JSON e aggiungi campi pdf_url e url_disegno
    echo "$json_output" | jq -c --arg pdf_url "$pdf_url" '
        if .items then
            .items[] |
            . as $item |
            ($item.numero_disegno // "" | tostring | match("[0-9]+")? | .string) as $clean_num |
            ($item.legislatura // "") as $leg |
            ($clean_num // "") as $num |
            ($leg |
                if . == "XVIII" then "18"
                elif . == "XVII" then "17"
                elif . == "XVI" then "16"
                elif . == "XV" then "15"
                elif . == "XIV" then "14"
                elif . == "XIII" then "13"
                elif . == "XII" then "12"
                elif . == "XI" then "11"
                elif . == "X" then "10"
                elif . == "IX" then "9"
                elif . == "VIII" then "8"
                elif . == "VII" then "7"
                elif . == "VI" then "6"
                elif . == "V" then "5"
                elif . == "IV" then "4"
                elif . == "III" then "3"
                elif . == "II" then "2"
                elif . == "I" then "1"
                else "" end
            ) as $leg_num |
            $item + {
                numero_disegno: ($num // ""),
                pdf_url: $pdf_url,
                url_disegno: (
                    if ($leg_num | length) > 0 and ($num | length) > 0 then
                        "https://dati.ars.sicilia.it/icaro/default.jsp?icaDB=221&icaQuery=(" +
                        $leg_num + ".LEGISL+E+" + $num + ".NUMDDL)"
                    else
                        null
                    end
                )
            }
        else
            empty
        end
    ' >> "$OUTPUT_JSONL"
}

# Main
main() {
    local reprocess=0
    local pdf_url_arg=""
    local output_dir_arg=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --reprocess)
                reprocess=1
                shift
                ;;
            --pdf-url)
                pdf_url_arg="${2:-}"
                shift 2
                ;;
            --output-dir)
                output_dir_arg="${2:-}"
                shift 2
                ;;
            *)
                echo "Unknown option: $1" >&2
                exit 1
                ;;
        esac
    done

    if [[ -n "$output_dir_arg" ]]; then
        if [[ "$output_dir_arg" = /* ]]; then
            OUTPUT_DIR="$output_dir_arg"
        else
            OUTPUT_DIR="$PROJECT_DIR/$output_dir_arg"
        fi
        OUTPUT_JSONL="$OUTPUT_DIR/disegni_legge.jsonl"
        PROCESSED_LOG="$OUTPUT_DIR/logs/odg_pdfs_processed.txt"
    fi

    echo "=== Estrazione dati OdG PDF ===" >&2
    echo "Input: $CSV_FILE" >&2
    echo "Output: $OUTPUT_JSONL" >&2
    if [[ "$reprocess" -eq 1 ]]; then
        echo "Mode: reprocess all PDFs" >&2
    else
        echo "Mode: skip already processed PDFs" >&2
    fi
    echo "" >&2

    # Crea file output e log se non esistono
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$(dirname "$PROCESSED_LOG")"
    touch "$OUTPUT_JSONL"
    touch "$PROCESSED_LOG"
    if [[ "$reprocess" -eq 0 ]] && [[ ! -s "$PROCESSED_LOG" ]] && [[ -s "$OUTPUT_JSONL" ]]; then
        jq -r '.pdf_url' "$OUTPUT_JSONL" | sort -u > "$PROCESSED_LOG"
    fi
    if [[ "$reprocess" -eq 1 ]]; then
        : > "$PROCESSED_LOG"
    fi

    local pdf_urls
    if [[ -n "$pdf_url_arg" ]]; then
        pdf_urls="$pdf_url_arg"
    else
        pdf_urls=$(get_distinct_odg_urls)
    fi

    local total
    total=$(echo "$pdf_urls" | wc -l | tr -d ' ')

    echo "Trovati $total PDF OdG distinti" >&2
    echo "" >&2

    local count=0
    local skipped=0
    local processed=0

    while IFS= read -r pdf_url; do
        ((count++)) || true

        echo "[$count/$total] Checking: $pdf_url" >&2

        if [[ "$reprocess" -eq 0 ]] && is_pdf_processed "$pdf_url"; then
            echo "  → Skipped (already processed)" >&2
            ((skipped++)) || true
        else
            process_pdf "$pdf_url"
            if ! grep -qFx "$pdf_url" "$PROCESSED_LOG"; then
                echo "$pdf_url" >> "$PROCESSED_LOG"
            fi
            echo "  → Processed" >&2
            ((processed++)) || true
        fi

        echo "" >&2
    done <<< "$pdf_urls"

    echo "=== Summary ===" >&2
    echo "Total PDFs: $total" >&2
    echo "Processed: $processed" >&2
    echo "Skipped: $skipped" >&2
    echo "" >&2

    # Normalizza numero_disegno e rimuovi duplicati esatti
    if [[ -f "$OUTPUT_JSONL" && -s "$OUTPUT_JSONL" ]]; then
        mlr -I --jsonl put '$numero_disegno = regextract_or_else($numero_disegno, "[0-9]+", "")' "$OUTPUT_JSONL"
        mlr -I --jsonl filter '$numero_disegno != ""' "$OUTPUT_JSONL"
        mlr -I -S --jsonl uniq -a "$OUTPUT_JSONL"
        echo "Duplicates removed (if any)" >&2
    fi

    echo "Output saved to: $OUTPUT_JSONL" >&2
}

main "$@"
