#!/usr/bin/env python3
"""
Aggiorna le descrizioni YouTube per i video senza token seduta.

Legge data/anagrafica_video.csv, ricostruisce la descrizione con token e link
nuovo, e aggiorna solo i video che non lo contengono.

Usage:
  python3 update_descriptions.py --dry-run
  python3 update_descriptions.py --limit 5
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from src import uploader
from src.metadata import build_description, build_seduta_token, build_recording_date


def load_config(config_path: str = './config/config.yaml') -> dict:
    """Carica configurazione."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_anagrafica(anagrafica_path: str) -> List[dict]:
    """Carica tutte le righe dell'anagrafica."""
    with open(anagrafica_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def group_by_youtube_id(rows: List[dict]) -> Dict[str, dict]:
    """
    Ritorna la prima occorrenza per youtube_id (sufficiente per ricostruire seduta/video).
    """
    grouped = {}
    for row in rows:
        yt = row.get('youtube_id', '').strip()
        if not yt:
            continue
        if yt not in grouped:
            grouped[yt] = row
    return grouped


def get_video_snippet(youtube, video_id: str) -> Optional[dict]:
    """Recupera snippet/status correnti del video."""
    try:
        response = youtube.videos().list(
            part='snippet,status,recordingDetails',
            id=video_id
        ).execute()
        items = response.get('items', [])
        return items[0] if items else None
    except Exception as e:
        print(f"  ✗ Errore fetch video {video_id}: {e}")
        return None


def update_video_description(youtube, video_id: str, new_description: str, current: dict, recording_date: str | None) -> bool:
    """Aggiorna descrizione mantenendo titolo, tag, categoria, privacy."""
    try:
        snippet = current.get('snippet', {})
        status = current.get('status', {})

        body = {
            'id': video_id,
            'snippet': {
                'title': snippet.get('title', ''),
                'description': new_description,
                'tags': snippet.get('tags', []),
                'categoryId': snippet.get('categoryId', '25'),
                'defaultLanguage': snippet.get('defaultLanguage', 'it')
            },
            'status': {
                'privacyStatus': status.get('privacyStatus', 'public')
            }
        }

        if recording_date:
            body['recordingDetails'] = {
                'recordingDate': recording_date
            }

        youtube.videos().update(
            part='snippet,status' + (',recordingDetails' if recording_date else ''),
            body=body
        ).execute()

        return True

    except Exception as e:
        print(f"  ✗ Errore update video {video_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Aggiorna descrizioni YouTube con token seduta')
    parser.add_argument('--dry-run', action='store_true', help='Mostra cosa farebbe senza aggiornare')
    parser.add_argument('--limit', type=int, default=0, help='Limita numero di update (0 = no limit)')
    args = parser.parse_args()

    config = load_config()
    anagrafica_path = config['logging']['anagrafica_file']

    if not Path(anagrafica_path).exists():
        print(f"✗ Anagrafica non trovata: {anagrafica_path}")
        return 1

    rows = load_anagrafica(anagrafica_path)
    grouped = group_by_youtube_id(rows)

    if not grouped:
        print("✓ Nessun youtube_id trovato in anagrafica")
        return 0

    youtube = None
    if not args.dry_run:
        print("🔐 Autenticazione YouTube...")
        youtube = uploader.authenticate(
            config['youtube']['credentials_file'],
            config['youtube']['token_file']
        )

    updated = 0
    skipped = 0

    for youtube_id, row in grouped.items():
        seduta_info = {
            'numero_seduta': row.get('numero_seduta'),
            'data_seduta': row.get('data_seduta'),
            'url_pagina': row.get('url_pagina'),
            'odg_url': row.get('odg_url'),
            'resoconto_url': row.get('resoconto_url')
        }
        video_info = {
            'id_video': row.get('id_video'),
            'ora_video': row.get('ora_video'),
            'data_video': row.get('data_video')
        }

        token = build_seduta_token(seduta_info)
        if not token:
            print(f"  ⚠ Token non generabile per {youtube_id}, skip")
            skipped += 1
            continue

        new_description = build_description(seduta_info, video_info, config)

        if args.dry_run:
            print(f"[DRY] {youtube_id}: aggiungere token {token}")
            updated += 1
            if args.limit and updated >= args.limit:
                break
            continue

        current = get_video_snippet(youtube, youtube_id)
        if not current:
            skipped += 1
            continue

        current_desc = current.get('snippet', {}).get('description', '')
        if token in current_desc and current_desc == new_description:
            skipped += 1
            continue

        recording_date = build_recording_date(video_info, timezone=config.get('youtube', {}).get('timezone', 'Europe/Rome'))

        print(f"Aggiorno {youtube_id}...")
        ok = update_video_description(youtube, youtube_id, new_description, current, recording_date)
        if ok:
            updated += 1
        else:
            skipped += 1

        if args.limit and updated >= args.limit:
            break

    print(f"\nRiepilogo: aggiornati={updated}, skip={skipped}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
