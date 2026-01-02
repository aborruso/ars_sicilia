#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_FILE="$SCRIPT_DIR/../data/anagrafica_video.csv"
OUTPUT_DIR="$SCRIPT_DIR/../data/trascrizioni"

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

	yt-dlp --write-auto-subs --sub-lang it --sub-format srt --skip-download --output "$OUTPUT_DIR/%(id)s.%(ext)s" "https://youtu.be/${youtube_id}" --no-update

	if [ -f "$srt_file" ]; then
		grep -E '^[0-9]+$' -v "$srt_file" | grep -E '^[0-9]' -v | grep -E '^$' -v | sed 's/^-->.*$//g' | sed 's/^[[:space:]]*//g' | sed '/^$/d' >"$txt_file"
		echo "  Created: $srt_file, $txt_file"
	else
		echo "  Warning: no subtitles found for $youtube_id"
		echo "$youtube_id" >>"$OUTPUT_DIR/no_transcript.txt"
	fi

done < <(tail -n +2 "$CSV_FILE")

echo "Done!"
