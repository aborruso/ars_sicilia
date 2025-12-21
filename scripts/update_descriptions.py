#!/usr/bin/env python3
"""
Aggiorna le descrizioni YouTube per i video senza token seduta.

Legge data/anagrafica_video.csv, ricostruisce la descrizione con token e link
nuovo, e aggiorna solo i video che non lo contengono.

Usage:
  python3 update_descriptions.py --dry-run
  python3 update_descriptions.py --limit 5
  python3 update_descriptions.py --update-license
  python3 update_descriptions.py --update-recording-date
  python3 update_descriptions.py --update-audio-language
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))


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


def update_video_description(
    youtube,
    video_id: str,
    new_description: str,
    current: dict,
    recording_date: str | None,
    license_value: str | None,
    audio_language: str | None
) -> bool:
    """Aggiorna descrizione mantenendo titolo, tag, categoria, privacy (e licenza/lingua audio se richieste)."""
    try:
        snippet = current.get('snippet', {})
        status = current.get('status', {})

        status_body = {
            'privacyStatus': status.get('privacyStatus', 'public')
        }
        if license_value:
            status_body['license'] = license_value

        snippet_body = {
            'title': snippet.get('title', ''),
            'description': new_description,
            'tags': snippet.get('tags', []),
            'categoryId': snippet.get('categoryId', '25'),
            'defaultLanguage': snippet.get('defaultLanguage', 'it')
        }
        if audio_language:
            snippet_body['defaultAudioLanguage'] = audio_language

        body = {
            'id': video_id,
            'snippet': snippet_body,
            'status': status_body
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
    parser.add_argument('--update-titles', action='store_true', help='Aggiorna anche i titoli con il nuovo formato')
    parser.add_argument('--update-license', action='store_true', help='Aggiorna la licenza YouTube secondo config')
    parser.add_argument('--update-recording-date', action='store_true', help='Aggiorna recordingDate secondo anagrafica')
    parser.add_argument('--update-audio-language', action='store_true', help='Aggiorna defaultAudioLanguage secondo config')
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
        new_title = None
        if args.update_titles:
            from src.metadata import build_title
            new_title = build_title(seduta_info, video_info)

        desired_license = None
        if args.update_license:
            desired_license = config.get('youtube', {}).get('license', 'creativeCommon')
        desired_audio_language = None
        if args.update_audio_language:
            desired_audio_language = config.get('youtube', {}).get('audio_language', 'it-IT')
        recording_date = build_recording_date(
            video_info,
            timezone=config.get('youtube', {}).get('timezone', 'Europe/Rome')
        )

        if args.dry_run:
            extra = f", license={desired_license}" if desired_license else ""
            if args.update_recording_date:
                extra += f", recordingDate={recording_date}"
            if desired_audio_language:
                extra += f", audioLanguage={desired_audio_language}"
            print(f"[DRY] {youtube_id}: aggiungere token {token}{extra}")
            print("  " + "-" * 66)
            for line in new_description.split('\n'):
                print(f"  {line}")
            print("  " + "-" * 66)
            updated += 1
            if args.limit and updated >= args.limit:
                break
            continue

        current = get_video_snippet(youtube, youtube_id)
        if not current:
            skipped += 1
            continue

        current_desc = current.get('snippet', {}).get('description', '')
        current_title = current.get('snippet', {}).get('title', '')
        current_license = current.get('status', {}).get('license')
        current_audio_language = current.get('snippet', {}).get('defaultAudioLanguage')
        current_recording_date = current.get('recordingDetails', {}).get('recordingDate')

        needs_update = False
        if token not in current_desc or current_desc != new_description:
            needs_update = True
        if new_title and current_title != new_title:
            needs_update = True
        if desired_license and current_license != desired_license:
            needs_update = True
        if args.update_recording_date and recording_date and current_recording_date != recording_date:
            needs_update = True
        if desired_audio_language and current_audio_language != desired_audio_language:
            needs_update = True

        if not needs_update:
            skipped += 1
            continue

        print(f"Aggiorno {youtube_id}...")
        if new_title:
            current['snippet']['title'] = new_title
        ok = update_video_description(
            youtube,
            youtube_id,
            new_description,
            current,
            recording_date if args.update_recording_date else None,
            desired_license,
            desired_audio_language
        )
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
