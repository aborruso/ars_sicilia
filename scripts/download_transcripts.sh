#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CSV_FILE="${CSV_FILE:-$REPO_ROOT/data/anagrafica_video.csv}"
OUTPUT_DIR="${OUTPUT_DIR:-$REPO_ROOT/data/trascrizioni}"
API_HELPER="$REPO_ROOT/scripts/download_caption_api.py"
if [ -x "$REPO_ROOT/.venv/bin/python3" ]; then
	PYTHON_BIN="${PYTHON_BIN:-$REPO_ROOT/.venv/bin/python3}"
else
	PYTHON_BIN="${PYTHON_BIN:-python3}"
fi

# Numero massimo di trascrizioni nuove da scaricare per run (0 = illimitato).
MAX_DOWNLOADS="${MAX_DOWNLOADS:-0}"
downloaded=0

mkdir -p "$OUTPUT_DIR"

while IFS= read -r line; do
	youtube_id=$(echo "$line" | cut -d',' -f14)

	if [ -z "$youtube_id" ] || [ "$youtube_id" = "youtube_id" ]; then
		continue
	fi

	echo "Processing: $youtube_id"

	srt_file="$OUTPUT_DIR/${youtube_id}.it.srt"
	txt_file="$OUTPUT_DIR/${youtube_id}.it.txt"

	if [ -f "$srt_file" ] && [ -f "$txt_file" ]; then
		echo "  Skipping: files already exist"
		continue
	fi

	if "$PYTHON_BIN" "$API_HELPER" --youtube-id "$youtube_id" --output-file "$srt_file" --lang it; then
		:
	else
		rc=$?
		if [ "$rc" -eq 2 ]; then
			echo "  Warning: no subtitles found for $youtube_id"
			echo "$youtube_id" >>"$OUTPUT_DIR/no_transcript.txt"
			continue
		fi
		if [ "$rc" -eq 3 ]; then
			echo "  Warning: video not found (404), skipping $youtube_id"
			echo "$youtube_id" >>"$OUTPUT_DIR/no_transcript.txt"
			continue
		fi
		echo "  Error: API transcript download failed for $youtube_id"
		exit "$rc"
	fi

	if [ -f "$srt_file" ]; then
		grep -E '^[0-9]+$' -v "$srt_file" | grep -E '^[0-9]' -v | grep -E '^$' -v | sed 's/^-->.*$//g' | sed 's/^[[:space:]]*//g' | sed '/^$/d' >"$txt_file"
		echo "  Created: $srt_file, $txt_file"
		downloaded=$((downloaded + 1))
		if [ "$MAX_DOWNLOADS" -gt 0 ] && [ "$downloaded" -ge "$MAX_DOWNLOADS" ]; then
			echo "Raggiunto limite download ($MAX_DOWNLOADS), stop."
			break
		fi
	fi

done < <(tail -n +2 "$CSV_FILE")

if [ -f "$OUTPUT_DIR/no_transcript.txt" ]; then
	sort -u "$OUTPUT_DIR/no_transcript.txt" -o "$OUTPUT_DIR/no_transcript.txt"
fi

echo "Done!"
