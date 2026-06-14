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

# Modello LLM esplicito (override con env ODG_MODEL). Evita dipendenza dal default di llm cli.
MODEL="${ODG_MODEL:-gemini-2.5-flash}"

# Schema LLM per estrazione dati
SCHEMA='
titolo_disegno: il titolo esatto del disegno di legge come riportato, senza testo aggiuntivo,
numero_disegno: solo il primo numero del disegno. Per abbinati come 779-3-26-70-88/A restituisci SOLO 779. MAI rimuovere i trattini concatenando le cifre: 779-3-26-70-88 NON deve MAI diventare 7793267088,
legislatura: solo il numero romano della legislatura senza la parola Legislatura, esempio XVIII,
data_ora: data e ora della seduta in formato ISO 8601: YYYY-MM-DD HH:MM'

SYSTEM_PROMPT="Estrai SOLO i disegni di legge elencati nella sezione
\"DISCUSSIONE DEI DISEGNI DI LEGGE\" dell'ORDINE DEL GIORNO.

Regole RIGIDE:
- Considera solo l'elenco puntato/numerato immediatamente sotto quel titolo di sezione.
- Ogni voce dell'elenco è UN item. NON spezzare una voce in più item.
- NON includere frammenti di testo, righe di intestazione, date, numeri di pagina,
  allegati, comunicazioni, indice.
- Interrompi quando finisce l'elenco, o se compare una nuova sezione,
  \"ALLEGATO\", \"COMUNICAZIONI\", \"INDICE\", o \"DISEGNI DI LEGGE PRESENTATI ED INVIATI\".
- Ignora qualsiasi DDL citato in allegati o comunicazioni.
- numero_disegno: SOLO la parte numerica principale (primo numero). Per abbinati
  come '779-3-26-70-88/A' estrai 779. Per stralci come '1030/A Stralcio I/A' estrai 1030.
- DIVIETO ASSOLUTO: MAI rimuovere i trattini concatenando le cifre.
  '779-3-26-70-88' NON deve MAI diventare '7793267088'. Restituisci esclusivamente '779'.
- legislatura: solo il numero romano (es. XVIII), MAI \"XVIII Legislatura\".
- Se la sezione non è presente, restituisci zero item."

# Funzione per estrarre URL distinti da CSV
get_distinct_odg_urls() {
    # Salta header, estrai campo odg_url (colonna 4), rimuovi vuoti, distinct
    tail -n +2 "$CSV_FILE" | cut -d',' -f4 | grep -v '^$' | sort -u
}

# Funzione per controllare se un PDF è già stato processato (col prompt corrente).
# Fonte di verità: PROCESSED_LOG. Per rielaborare tutto, svuotare il log.
is_pdf_processed() {
    local pdf_url="$1"
    [[ -f "$PROCESSED_LOG" ]] && grep -qFx "$pdf_url" "$PROCESSED_LOG"
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

    # Estrai testo dal PDF
    local text
    text=$(markitdown "$pdf_url" 2>/dev/null) || { echo "  ERRORE: markitdown fallito" >&2; return 1; }
    if [[ -z "$text" ]]; then echo "  ERRORE: testo vuoto" >&2; return 1; fi

    # Estrai dati con llm, con retry e backoff sui rate limit (free tier ~10 RPM, 429)
    local json_output="" attempt
    for attempt in 1 2 3; do
        json_output=$(printf '%s' "$text" | llm -m "$MODEL" --schema-multi "$SCHEMA" --system "$SYSTEM_PROMPT" 2>/dev/null) && break
        echo "  Tentativo $attempt fallito (rate limit?), attendo $((attempt * 15))s..." >&2
        sleep $((attempt * 15))
        json_output=""
    done
    if [[ -z "$json_output" ]]; then echo "  ERRORE: llm fallito dopo i retry" >&2; return 1; fi

    # Parse JSON e aggiungi campi pdf_url e url_disegno
    echo "$json_output" | jq -c --arg pdf_url "$pdf_url" '
        if .items then
            .items[] |
            . as $item |
            ($item.numero_disegno // "" | tostring | match("[0-9]+")? | .string) as $clean_num |
            (($item.legislatura // "") | ascii_upcase | ((match("[IVXLC]+")? | .string) // "")) as $leg |
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
                legislatura: $leg,
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

    # Throttle per rispettare il limite RPM del free tier (~10 RPM)
    sleep "${ODG_SLEEP:-7}"
}

# Main
main() {
    local reprocess=0
    local pdf_url_arg=""
    local output_dir_arg=""
    local limit="${ODG_LIMIT:-0}"   # max PDF da processare per lancio (0 = illimitato)

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --reprocess)
                reprocess=1
                shift
                ;;
            --limit)
                limit="${2:-0}"
                shift 2
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
    if [[ "$reprocess" -eq 1 ]]; then
        : > "$PROCESSED_LOG"
        # Rigenerazione totale: backup e ricostruzione da zero (evita append su dati vecchi).
        if [[ -s "$OUTPUT_JSONL" ]]; then
            cp "$OUTPUT_JSONL" "$OUTPUT_JSONL.bak"
            echo "Backup creato: $OUTPUT_JSONL.bak" >&2
        fi
        : > "$OUTPUT_JSONL"
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
            # In modalità incrementale, rimuovi eventuali record preesistenti di questo PDF
            # prima di ri-aggiungerli (idempotenza, evita duplicati su ri-elaborazione).
            if [[ "$reprocess" -eq 0 && -s "$OUTPUT_JSONL" ]]; then
                # Rimozione robusta per chiave (jq parsa il JSON, indipendente dal formato/spazi)
                if jq -c --arg u "$pdf_url" 'select(.pdf_url != $u)' "$OUTPUT_JSONL" > "$OUTPUT_JSONL.flt" 2>/dev/null; then
                    mv "$OUTPUT_JSONL.flt" "$OUTPUT_JSONL"
                else
                    rm -f "$OUTPUT_JSONL.flt"
                fi
            fi
            if ! process_pdf "$pdf_url"; then
                echo "  → ERRORE su $pdf_url (continuo)" >&2
            fi
            if ! grep -qFx "$pdf_url" "$PROCESSED_LOG"; then
                echo "$pdf_url" >> "$PROCESSED_LOG"
            fi
            echo "  → Processed" >&2
            ((processed++)) || true

            if [[ "$limit" -gt 0 && "$processed" -ge "$limit" ]]; then
                echo "" >&2
                echo "Raggiunto limite di $limit PDF per questo lancio." >&2
                break
            fi
        fi

        echo "" >&2
    done <<< "$pdf_urls"

    echo "=== Summary ===" >&2
    echo "Total PDFs: $total" >&2
    echo "Processed: $processed" >&2
    echo "Skipped: $skipped" >&2
    echo "" >&2

    # Normalizzazione difensiva, scarto spazzatura e dedup
    if [[ -f "$OUTPUT_JSONL" && -s "$OUTPUT_JSONL" ]]; then
        # numero_disegno: solo il primo gruppo di cifre; legislatura: solo il romano
        mlr -I --jsonl put '$numero_disegno = regextract_or_else($numero_disegno, "[0-9]+", "")' "$OUTPUT_JSONL"
        mlr -I --jsonl put '$legislatura = regextract_or_else($legislatura, "[IVXLC]+", "")' "$OUTPUT_JSONL"
        # scarta record senza numero o con titolo mancante/troppo corto (frammenti/spazzatura)
        mlr -I --jsonl filter '$numero_disegno != "" && is_present($titolo_disegno) && strlen($titolo_disegno) > 5' "$OUTPUT_JSONL"
        # dedup per (pdf_url, numero_disegno, titolo_disegno): tiene il primo di ogni gruppo
        mlr -I --jsonl head -n 1 -g pdf_url,numero_disegno,titolo_disegno "$OUTPUT_JSONL"
        echo "Normalizzato e deduplicato. Record finali: $(wc -l < "$OUTPUT_JSONL")" >&2

        # Sanity check: PDF processati ma con 0 record nell'output finale
        local empty_pdfs
        empty_pdfs=$(comm -23 \
            <(sort -u "$PROCESSED_LOG") \
            <(jq -r '.pdf_url' "$OUTPUT_JSONL" | sort -u) 2>/dev/null || true)
        if [[ -n "$empty_pdfs" ]]; then
            echo "ATTENZIONE: PDF senza disegni estratti (verificare):" >&2
            echo "$empty_pdfs" | sed 's/^/  - /' >&2
        fi
    fi

    echo "Output saved to: $OUTPUT_JSONL" >&2
}

main "$@"
