#!/usr/bin/env python3
"""
Sincronizza ID YouTube dall'API alla anagrafica locale.

Interroga la playlist YouTube e aggiorna l'anagrafica con gli ID YouTube
mancanti basandosi sul titolo del video.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import csv
import re
import yaml
from datetime import datetime
from src import uploader

REPO_ROOT = Path(__file__).resolve().parents[2]

def parse_video_title(title: str) -> tuple:
    """Estrae numero seduta e data dal titolo YouTube."""
    # Formato: "Lavori d'aula: seduta n. 220 (16 Dicembre 2025) - 15:57"
    match = re.search(r'seduta n\. (\d+).*?(\d{2}:\d{2})', title)
    if match:
        numero_seduta = match.group(1)
        ora_video = match.group(2)
        return (numero_seduta, ora_video)
    return (None, None)


def main():
    print("\n" + "="*70)
    print("SYNC YOUTUBE IDS")
    print("="*70 + "\n")

    # Carica config
    config_path = REPO_ROOT / 'config' / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    anagrafica_path = config['logging']['anagrafica_file']

    # Autenticazione
    print("🔐 Autenticazione YouTube...")
    try:
        youtube = uploader.authenticate(
            config['youtube']['credentials_file'],
            config['youtube']['token_file']
        )
        print("  ✓ Autenticato\n")
    except Exception as e:
        print(f"  ✗ Errore: {e}")
        return 1

    # Recupera playlist ID
    playlist_id = config.get('youtube', {}).get('playlists', {}).get('2025')
    if not playlist_id:
        print("  ✗ Playlist ID 2025 non trovato")
        return 1

    # Recupera video da playlist
    print(f"📋 Recupero video da playlist {playlist_id}...")
    try:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()

        youtube_videos = {}
        for item in response.get('items', []):
            video_id = item['contentDetails']['videoId']
            title = item['snippet']['title']
            numero_seduta, ora_video = parse_video_title(title)

            if numero_seduta and ora_video:
                key = f"{numero_seduta}_{ora_video}"
                youtube_videos[key] = video_id

        print(f"  ✓ Trovati {len(youtube_videos)} video con metadata validi\n")

    except Exception as e:
        print(f"  ✗ Errore: {e}")
        return 1

    # Leggi anagrafica
    print(f"📄 Aggiornamento anagrafica {anagrafica_path}...")
    rows = []
    updated_count = 0

    with open(anagrafica_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])

        for row in reader:
            # Se già ha youtube_id, skip
            if row.get('youtube_id'):
                rows.append(row)
                continue

            # Cerca match in playlist
            numero_seduta = row.get('numero_seduta', '')
            ora_video = row.get('ora_video', '')
            key = f"{numero_seduta}_{ora_video}"

            if key in youtube_videos:
                youtube_id = youtube_videos[key]
                row['youtube_id'] = youtube_id
                row['last_check'] = datetime.now().isoformat()
                row['status'] = 'success'
                print(f"  ✓ Video {row['id_video']}: {youtube_id}")
                updated_count += 1

            rows.append(row)

    # Riscrivi anagrafica
    with open(anagrafica_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Completato: {updated_count} record aggiornati")
    print("="*70 + "\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
