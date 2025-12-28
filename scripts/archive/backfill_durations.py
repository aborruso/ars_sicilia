#!/usr/bin/env python3
"""
Backfill script per popolare duration_minutes nei video YouTube già uploadati.

Usa YouTube Data API v3 per recuperare la durata di video già presenti su YouTube.
"""
import csv
import re
import sys
from pathlib import Path

# Aggiungi src al path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src import uploader


def parse_iso_duration(iso_str: str) -> int:
    """
    Converte durata ISO 8601 (es. PT1H23M45S) in minuti arrotondati.

    Args:
        iso_str: Durata formato ISO 8601 (es. PT1H23M45S, PT45M, PT30S)

    Returns:
        Durata in minuti (arrotondata)

    Examples:
        PT45S -> 1 minuto
        PT1H23M45S -> 84 minuti
        PT2H -> 120 minuti
    """
    # Pattern: PT[hours]H[minutes]M[seconds]S (ogni parte opzionale)
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_str)
    if not match:
        raise ValueError(f"Formato ISO 8601 invalido: {iso_str}")

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    # Converti tutto in minuti e arrotonda
    total_minutes = hours * 60 + minutes + seconds / 60
    return round(total_minutes)


def get_youtube_durations(youtube_client, video_ids: list[str]) -> dict[str, int]:
    """
    Recupera durate da YouTube Data API v3 (batch di max 50 video).

    Args:
        youtube_client: Client YouTube autenticato
        video_ids: Lista ID video YouTube

    Returns:
        Dict {video_id: duration_minutes}
    """
    if not video_ids:
        return {}

    durations = {}

    try:
        # YouTube API: max 50 IDs per chiamata
        request = youtube_client.videos().list(
            part='contentDetails',
            id=','.join(video_ids),
            maxResults=50
        )

        response = request.execute()

        for item in response.get('items', []):
            video_id = item['id']
            iso_duration = item['contentDetails']['duration']

            try:
                duration_mins = parse_iso_duration(iso_duration)
                durations[video_id] = duration_mins
            except ValueError as e:
                print(f"  ⚠ Errore parsing durata {video_id}: {e}")

        return durations

    except Exception as e:
        print(f"  ✗ Errore YouTube API: {e}")
        return {}


def backfill_anagrafica_durations(anagrafica_path: str, config: dict) -> int:
    """
    Popola duration_minutes per video con youtube_id ma senza durata.

    Args:
        anagrafica_path: Path al CSV anagrafica
        config: Dict configurazione (per credenziali YouTube)

    Returns:
        Numero video aggiornati
    """
    print(f"Backfill durate da YouTube API\n")
    print(f"Anagrafica: {anagrafica_path}\n")

    # Autenticazione YouTube
    print("Autenticazione YouTube...")
    try:
        youtube = uploader.authenticate(
            config['youtube']['credentials_file'],
            config['youtube']['token_file']
        )
        print("✓ Autenticato\n")
    except Exception as e:
        print(f"✗ Errore autenticazione: {e}")
        return 0

    # Leggi anagrafica
    path = Path(anagrafica_path)
    if not path.exists():
        print(f"✗ Anagrafica non trovata: {anagrafica_path}")
        return 0

    rows = []
    video_ids_to_fetch = []
    row_indices_by_id = {}

    with open(anagrafica_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for i, row in enumerate(reader):
            rows.append(row)

            # Filtra: youtube_id non vuoto E duration_minutes vuoto
            youtube_id = (row.get('youtube_id') or '').strip()
            duration = (row.get('duration_minutes') or '').strip()

            if youtube_id and not duration:
                video_ids_to_fetch.append(youtube_id)
                row_indices_by_id[youtube_id] = i

    total = len(video_ids_to_fetch)
    if total == 0:
        print("✓ Nessun video da aggiornare (tutti hanno già duration_minutes)")
        return 0

    print(f"Video da aggiornare: {total}")
    print(f"Batch size: 50 (limite YouTube API)\n")

    # Fetch durate in batch da 50
    updated_count = 0

    for batch_start in range(0, total, 50):
        batch_ids = video_ids_to_fetch[batch_start:batch_start + 50]
        batch_num = batch_start // 50 + 1
        total_batches = (total + 49) // 50

        print(f"Batch {batch_num}/{total_batches}: {len(batch_ids)} video...")

        durations = get_youtube_durations(youtube, batch_ids)

        # Aggiorna rows
        for video_id, duration_mins in durations.items():
            row_index = row_indices_by_id[video_id]
            rows[row_index]['duration_minutes'] = str(duration_mins)
            updated_count += 1
            print(f"  ✓ {video_id}: {duration_mins} minuti")

        # Video non trovati
        not_found = set(batch_ids) - set(durations.keys())
        if not_found:
            print(f"  ⚠ Video non trovati su YouTube ({len(not_found)}): {', '.join(list(not_found)[:3])}")

    # Riscrivi anagrafica
    if updated_count > 0:
        print(f"\nAggiornamento anagrafica...")
        with open(anagrafica_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"✓ Anagrafica aggiornata")

    print(f"\n{'='*70}")
    print(f"Riepilogo:")
    print(f"  Video da aggiornare:  {total}")
    print(f"  Video aggiornati:     {updated_count}")
    print(f"  Video non trovati:    {total - updated_count}")
    print(f"{'='*70}\n")

    return updated_count


def main():
    """Entry point."""
    import yaml

    # Carica config
    config_path = './config/config.yaml'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"✗ Errore caricamento config: {e}")
        sys.exit(1)

    # Path anagrafica
    anagrafica_path = config.get('logging', {}).get('anagrafica_file', './data/anagrafica_video.csv')

    # Backup anagrafica
    backup_path = Path(anagrafica_path).with_suffix('.csv.backup')
    try:
        import shutil
        shutil.copy(anagrafica_path, backup_path)
        print(f"✓ Backup creato: {backup_path}\n")
    except Exception as e:
        print(f"⚠ Impossibile creare backup: {e}\n")

    # Esegui backfill
    try:
        backfill_anagrafica_durations(anagrafica_path, config)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrotto dall'utente\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Errore: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
