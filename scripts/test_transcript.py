#!/usr/bin/env python3
"""
Test script per scaricare trascrizioni YouTube usando youtube-transcript-api
Scarica la trascrizione del primo video con youtube_id nell'anagrafica
"""

import csv
import sys
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi as yt_api

# Paths
SCRIPT_DIR = Path(__file__).parent
CSV_FILE = SCRIPT_DIR.parent / "data" / "anagrafica_video.csv"
OUTPUT_FILE = SCRIPT_DIR.parent / "test_transcript_output.txt"

def main():
    print("=== Test YouTube Transcript Download ===")
    print(f"Reading: {CSV_FILE}")
    
    # Leggi primo video con youtube_id
    youtube_id = None
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('youtube_id'):
                youtube_id = row['youtube_id']
                print(f"Found video: {youtube_id}")
                break
    
    if not youtube_id:
        print("ERROR: No video with youtube_id found in anagrafica")
        sys.exit(1)
    
    # Scarica trascrizione
    print(f"Downloading transcript for: {youtube_id}")
    try:
        # Usa il metodo fetch() con fallback italiano -> inglese
        transcript = yt_api().fetch(youtube_id, languages=['it', 'en'])
        text = ' '.join([snippet.text for snippet in transcript])
        
        # Salva in root del repo
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# Transcript for video: {youtube_id}\n\n")
            f.write(text)
        
        print(f"✓ SUCCESS: Transcript saved to {OUTPUT_FILE}")
        print(f"  Size: {len(text)} characters")
        print(f"  Entries: {len(transcript)}")
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
