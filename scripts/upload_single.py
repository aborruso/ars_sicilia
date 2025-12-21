#!/usr/bin/env python3
"""
Test upload singolo video con aggiornamento anagrafica.

Carica il primo video dall'anagrafica senza youtube_id.
Se upload successo, aggiorna anagrafica per evitare duplicati.

Usage:
    python3 upload_single.py              # Upload primo video
    python3 upload_single.py --dry-run    # Mostra cosa farebbe senza uploadare
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))


import csv
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

from src import scraper, downloader, uploader
from src.metadata import build_youtube_metadata
from src.utils import extract_year


def load_config(config_path: str = './config/config.yaml') -> dict:
    """Carica configurazione."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_first_unuploaded_video(anagrafica_path: str) -> Optional[dict]:
    """
    Trova primo video senza youtube_id in anagrafica.
    
    Args:
        anagrafica_path: Path al CSV anagrafica
        
    Returns:
        Dict con dati video o None
    """
    try:
        with open(anagrafica_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Salta video già uploadati
                if row.get('youtube_id'):
                    continue
                    
                # Verifica che abbia dati essenziali
                if row.get('id_video') and row.get('ora_video'):
                    return row
                    
        return None
        
    except Exception as e:
        print(f"✗ Errore lettura anagrafica: {e}")
        return None


def update_anagrafica_youtube_id(
    anagrafica_path: str,
    id_video: str,
    youtube_id: str,
    numero_seduta: str | None = None,
    data_seduta: str | None = None
) -> bool:
    """
    Aggiorna youtube_id per video in anagrafica.
    
    Args:
        anagrafica_path: Path al CSV anagrafica
        id_video: ID video ARS
        youtube_id: ID video YouTube
        
    Returns:
        True se aggiornato
    """
    try:
        # Leggi anagrafica
        rows = []
        with open(anagrafica_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            for row in reader:
                # Aggiorna youtube_id se match
                match = row['id_video'] == id_video
                if numero_seduta and data_seduta:
                    match = (
                        match
                        and row.get('numero_seduta') == numero_seduta
                        and row.get('data_seduta') == data_seduta
                    )
                if match:
                    row['youtube_id'] = youtube_id
                    row['last_check'] = datetime.now().isoformat()
                rows.append(row)
        
        # Riscrivi anagrafica
        with open(anagrafica_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        return True
        
    except Exception as e:
        print(f"✗ Errore aggiornamento anagrafica: {e}")
        return False


def main():
    """Test upload singolo video."""
    # Parse argomenti
    parser = argparse.ArgumentParser(
        description='Test upload singolo video con aggiornamento anagrafica'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mostra cosa farebbe senza uploadare realmente'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Conferma automatica (salta prompt di conferma)'
    )
    args = parser.parse_args()

    mode = "DRY-RUN" if args.dry_run else "UPLOAD REALE"
    print("\n" + "="*70)
    print(f"TEST UPLOAD SINGOLO VIDEO ({mode})")
    print("="*70 + "\n")

    # Carica config
    config = load_config()
    anagrafica_path = config['logging']['anagrafica_file']

    # Trova primo video non uploadato
    print(f"📋 Ricerca primo video non uploadato in {anagrafica_path}...")
    video_row = get_first_unuploaded_video(anagrafica_path)

    if not video_row:
        print("✓ Nessun video da uploadare (tutti già su YouTube)")
        return 0

    print(f"\n✓ Video trovato:")
    print(f"  Seduta: {video_row['numero_seduta']}")
    print(f"  Data seduta: {video_row['data_seduta']}")
    print(f"  Data video: {video_row['data_video']}")
    print(f"  Ora: {video_row['ora_video']}")
    print(f"  ID video ARS: {video_row['id_video']}")
    print(f"  URL pagina: {video_row['video_page_url']}")

    # Conferma utente (skip in dry-run o con --yes)
    if not args.dry_run and not args.yes:
        print(f"\n⚠️  ATTENZIONE: Questo video verrà caricato su YouTube!")
        response = input("Continuare? [y/N]: ")
        if response.lower() != 'y':
            print("Operazione annullata.")
            return 0
    elif not args.dry_run and args.yes:
        print(f"\n✓ Conferma automatica attiva (--yes)")
    
    # Prepara info seduta e video
    seduta_info = {
        'numero_seduta': video_row['numero_seduta'],
        'data_seduta': video_row['data_seduta'],
        'url_pagina': video_row['url_pagina'],
        'odg_url': video_row.get('odg_url'),
        'resoconto_url': video_row.get('resoconto_url')
    }
    
    video_info = {
        'id_video': video_row['id_video'],
        'ora_video': video_row['ora_video'],
        'data_video': video_row['data_video'],
        'video_page_url': video_row['video_page_url']
    }
    
    # Autenticazione YouTube (skip in dry-run)
    youtube = None
    if not args.dry_run:
        print(f"\n🔐 Autenticazione YouTube...")
        try:
            youtube = uploader.authenticate(
                config['youtube']['credentials_file'],
                config['youtube']['token_file']
            )

            # Ottieni info canale
            channel_info = uploader.get_channel_info(youtube)
            if channel_info:
                print(f"  ✓ Canale: {channel_info['title']}")

        except Exception as e:
            print(f"  ✗ Errore autenticazione: {e}")
            return 1
    else:
        print(f"\n🔐 [DRY-RUN] Autenticazione YouTube saltata")

    # Download video (skip in dry-run)
    video_path = None
    if not args.dry_run:
        print(f"\n⬇️  Download video...")
        temp_dir = Path(config['download']['temp_dir'])
        temp_dir.mkdir(parents=True, exist_ok=True)

        video_filename = f"ars_{video_row['numero_seduta']}_{video_row['id_video']}.mp4"
        video_path = temp_dir / video_filename

        try:
            success = downloader.download_video(
                video_row['video_page_url'],
                str(video_path),
                retries=config['download'].get('max_retries', 3),
                max_height=config['download'].get('max_height')
            )

            if not success or not video_path.exists():
                print(f"  ✗ Download fallito")
                return 1

            print(f"  ✓ Video scaricato: {video_path}")
            print(f"  Dimensione: {video_path.stat().st_size / (1024*1024):.1f} MB")

        except Exception as e:
            print(f"  ✗ Errore download: {e}")
            return 1
    else:
        print(f"\n⬇️  [DRY-RUN] Download video saltato")
    
    # Costruisci metadati
    print(f"\n📝 Costruzione metadati...")
    metadata = build_youtube_metadata(seduta_info, video_info, config)

    print(f"  Titolo: {metadata['title']}")
    print(f"  Tags: {len(metadata['tags'])} tag")
    print(f"  Recording date: {metadata.get('recordingDate', 'N/A')}")
    print(f"  License: {metadata.get('license', 'N/A')}")
    print(f"  Audio language: {metadata.get('defaultAudioLanguage', 'N/A')}")

    if args.dry_run:
        print(f"\n  📄 DESCRIZIONE COMPLETA:")
        print("  " + "-"*66)
        for line in metadata['description'].split('\n'):
            print(f"  {line}")
        print("  " + "-"*66)
        print(f"\n  🏷️  TAGS:")
        print(f"  {', '.join(metadata['tags'])}")
    
    # Determina playlist (crea automaticamente se non esiste)
    playlist_id = None
    if video_row['data_video']:
        year = extract_year(video_row['data_video'])
        if year:
            if args.dry_run:
                # In dry-run non creare playlist, usa quella configurata
                playlist_id = uploader.get_playlist_id_for_year(config, year)
            else:
                # In upload reale, crea se non esiste
                playlist_id = uploader.get_or_create_playlist_for_year(youtube, config, year)

            if playlist_id:
                print(f"  Playlist anno {year}: {playlist_id}")
    
    # Upload video (skip in dry-run)
    youtube_id = None
    if not args.dry_run:
        print(f"\n⬆️  Upload su YouTube...")
        try:
            youtube_id = uploader.upload_video(
                youtube,
                str(video_path),
                metadata,
                playlist_id=playlist_id
            )

            if not youtube_id:
                print(f"  ✗ Upload fallito")
                return 1

            print(f"\n✅ UPLOAD COMPLETATO!")
            print(f"  YouTube ID: {youtube_id}")
            print(f"  URL: https://youtube.com/watch?v={youtube_id}")

        except Exception as e:
            print(f"  ✗ Errore upload: {e}")
            return 1

        finally:
            # Cleanup video temporaneo
            if config['download'].get('cleanup_after_upload', True):
                if video_path and video_path.exists():
                    video_path.unlink()
                    print(f"\n🗑️  File temporaneo eliminato: {video_path.name}")

        # Aggiorna anagrafica
        print(f"\n💾 Aggiornamento anagrafica...")
        if update_anagrafica_youtube_id(
            anagrafica_path,
            video_row['id_video'],
            youtube_id,
            numero_seduta=video_row.get('numero_seduta'),
            data_seduta=video_row.get('data_seduta')
        ):
            print(f"  ✓ Anagrafica aggiornata: {anagrafica_path}")
            print(f"  Campo youtube_id impostato per video {video_row['id_video']}")
        else:
            print(f"  ✗ Errore aggiornamento anagrafica")
            print(f"  ⚠️  Video uploadato ma non registrato in anagrafica!")
            print(f"  Aggiorna manualmente: id_video={video_row['id_video']}, youtube_id={youtube_id}")
            return 1

    else:
        print(f"\n⬆️  [DRY-RUN] Upload su YouTube saltato")
        print(f"  Playlist target: {playlist_id or 'Nessuna playlist configurata'}")
        print(f"\n💾 [DRY-RUN] Aggiornamento anagrafica saltato")
        print(f"  Verrebbe impostato youtube_id per video {video_row['id_video']}")

    print(f"\n" + "="*70)
    if args.dry_run:
        print("DRY-RUN COMPLETATO - Nessuna modifica effettuata")
    else:
        print("TEST COMPLETATO CON SUCCESSO!")
    print("="*70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
