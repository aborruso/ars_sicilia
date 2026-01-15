#!/usr/bin/env python3
"""
ARS YouTube Uploader - Script principale.

Download video sedute ARS e upload su YouTube con metadati.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))


import sys
import yaml
from datetime import datetime
from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]

# Import moduli locali
from src import scraper, downloader, uploader, metadata, logger


def load_config(config_path: str = None) -> dict:
    """
    Carica configurazione da file YAML.

    Args:
        config_path: Path al file config

    Returns:
        Dict configurazione
    """
    if not config_path:
        config_path = str(REPO_ROOT / 'config' / 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def extract_seduta_date_from_href(href: str) -> str | None:
    """
    Estrae data seduta da URL tipo .../seduta-numero-219-del-10122025.

    Returns:
        Data in formato YYYY-MM-DD o None
    """
    match = re.search(r'seduta-numero-.*-del-(\d{8})', href)
    if not match:
        return None
    try:
        raw = match.group(1)
        return datetime.strptime(raw, "%d%m%Y").date().isoformat()
    except Exception:
        return None


def process_seduta(seduta_url: str, config: dict, youtube_client) -> dict:
    """
    Processa una singola seduta: scraping, download, upload.

    Args:
        seduta_url: URL pagina seduta
        config: Dict configurazione
        youtube_client: Client YouTube API

    Returns:
        Dict con risultati processing
    """
    print(f"\n{'='*70}")
    print(f"Processando seduta: {seduta_url}")
    print(f"{'='*70}\n")

    # 1. Scraping
    print("[1/4] Scraping pagina seduta...")
    try:
        scraping_cfg = config.get('scraping', {})
        html = scraper.get_seduta_page(
            seduta_url,
            scraping_cfg.get('user_agent', 'ARS-YouTube-Bot/1.0'),
            timeout=scraping_cfg.get('timeout', 30),
            retries=scraping_cfg.get('retries', 3),
            backoff_factor=scraping_cfg.get('backoff_factor', 0.5)
        )
        seduta_info = scraper.extract_seduta_info(html, seduta_url)

        print(f"  Seduta n. {seduta_info['numero_seduta']}")
        print(f"  Data: {seduta_info['data_seduta']}")
        print(f"  Video trovati: {len(seduta_info['videos'])}")

        if seduta_info.get('odg_url'):
            print(f"  OdG: {seduta_info['odg_url']}")
        if seduta_info.get('resoconto_url'):
            print(f"  Resoconto: {seduta_info['resoconto_url']}")

    except Exception as e:
        print(f"  ✗ Errore scraping: {e}")
        return {'status': 'failed', 'error': str(e)}

    if not seduta_info['videos']:
        print("  ℹ Nessun video trovato per questa seduta")
        return {'status': 'no_videos'}

    # 2. Process ogni video
    results = {
        'seduta': seduta_info['numero_seduta'],
        'total_videos': len(seduta_info['videos']),
        'uploaded': 0,
        'skipped': 0,
        'failed': 0
    }

    for i, video in enumerate(seduta_info['videos'], 1):
        print(f"\n[2/4] Video {i}/{len(seduta_info['videos'])}: {video['ora_video']}")

        video_id = video['id_video']
        log_file = config['logging']['log_file']

        # Check se già uploadato (priorità: anagrafica)
        anagrafica_path = config.get('logging', {}).get('anagrafica_file')
        if anagrafica_path and logger.is_video_uploaded_in_anagrafica(
            anagrafica_path,
            video_id,
            numero_seduta=seduta_info.get('numero_seduta'),
            data_seduta=seduta_info.get('data_seduta')
        ):
            print(f"  ⊙ Video già uploadato (anagrafica, ID {video_id}), skip")
            results['skipped'] += 1
            continue
        if logger.is_video_uploaded(
            log_file,
            video_id,
            numero_seduta=seduta_info.get('numero_seduta'),
            data_seduta=seduta_info.get('data_seduta')
        ):
            print(f"  ⊙ Video già uploadato (log, ID {video_id}), skip")
            results['skipped'] += 1
            continue

        # 3. Download
        print("[3/4] Download video...")

        # Determina URL stream (usa video_page_url con yt-dlp)
        video_url = video.get('stream_url') or video.get('video_page_url')
        if not video_url:
            print(f"  ✗ URL video non disponibile")
            logger.log_upload(log_file, video, '', 'failed', 'URL video mancante')
            if anagrafica_path:
                logger.update_anagrafica_failure(
                    anagrafica_path,
                    video_id,
                    'URL video mancante',
                    numero_seduta=seduta_info.get('numero_seduta'),
                    data_seduta=seduta_info.get('data_seduta')
                )
            results['failed'] += 1
            continue

        output_file = f"{config['download']['temp_dir']}/{video_id}.mp4"

        success, duration_mins = downloader.download_video(
            video_url,
            output_file,
            retries=config['download']['max_retries'],
            max_height=config['download'].get('max_height')
        )

        if not success:
            logger.log_upload(log_file, video, '', 'failed', 'Download fallito')
            if anagrafica_path:
                logger.update_anagrafica_failure(
                    anagrafica_path,
                    video_id,
                    'Download fallito',
                    numero_seduta=seduta_info.get('numero_seduta'),
                    data_seduta=seduta_info.get('data_seduta')
                )
            results['failed'] += 1
            continue

        # 4. Upload YouTube
        print("[4/4] Upload su YouTube...")

        try:
            # Build metadati
            meta = metadata.build_youtube_metadata(seduta_info, video, config)

            print(f"  Titolo: {meta['title']}")

            # Upload
            youtube_id = uploader.upload_video(youtube_client, output_file, meta)

            if youtube_id:
                # Log success
                logger.log_upload(log_file, video, youtube_id, 'success')
                if anagrafica_path:
                    logger.update_anagrafica_youtube_id(
                        anagrafica_path,
                        video_id,
                        youtube_id,
                        numero_seduta=seduta_info.get('numero_seduta'),
                        data_seduta=seduta_info.get('data_seduta'),
                        duration_minutes=duration_mins
                    )
                results['uploaded'] += 1
            else:
                logger.log_upload(log_file, video, '', 'failed', 'Upload fallito (no ID)')
                if anagrafica_path:
                    logger.update_anagrafica_failure(
                        anagrafica_path,
                        video_id,
                        'Upload fallito (no ID)',
                        numero_seduta=seduta_info.get('numero_seduta'),
                        data_seduta=seduta_info.get('data_seduta')
                    )
                results['failed'] += 1

        except Exception as e:
            print(f"  ✗ Errore upload: {e}")
            logger.log_upload(log_file, video, '', 'failed', str(e))
            if anagrafica_path:
                logger.update_anagrafica_failure(
                    anagrafica_path,
                    video_id,
                    f"Upload fallito: {e}",
                    numero_seduta=seduta_info.get('numero_seduta'),
                    data_seduta=seduta_info.get('data_seduta')
                )
            results['failed'] += 1

        finally:
            # Cleanup video
            if config['download']['cleanup_after_upload']:
                downloader.cleanup_video(output_file)

    # Aggiorna indice
    logger.update_index(
        config['logging']['index_file'],
        seduta_info,
        seduta_info['videos']
    )

    # Riepilogo
    print(f"\n{'='*70}")
    print(f"Riepilogo seduta {seduta_info['numero_seduta']}:")
    print(f"  Video totali:    {results['total_videos']}")
    print(f"  Uploadati:       {results['uploaded']}")
    print(f"  Già presenti:    {results['skipped']}")
    print(f"  Falliti:         {results['failed']}")
    print(f"{'='*70}\n")

    return results


def main():
    """Main entry point."""
    print("ARS YouTube Uploader\n")

    # Carica config
    try:
        config = load_config()
    except Exception as e:
        print(f"✗ Errore caricamento config: {e}")
        sys.exit(1)

    # Init log
    logger.init_log_file(config['logging']['log_file'])

    # Autenticazione YouTube
    print("Autenticazione YouTube...")
    try:
        youtube = uploader.authenticate(
            config['youtube']['credentials_file'],
            config['youtube']['token_file']
        )

        # Verifica canale
        channel = uploader.get_channel_info(youtube)
        if channel:
            print(f"✓ Canale: {channel['title']}")
            print(f"  Video: {channel['videoCount']}\n")
        else:
            print("⚠ Impossibile ottenere info canale\n")

    except FileNotFoundError as e:
        print(f"\n✗ {e}")
        print("\nPer configurare YouTube API:")
        print("1. Vai su https://console.cloud.google.com/")
        print("2. Crea progetto e abilita YouTube Data API v3")
        print("3. Scarica credenziali OAuth2 in config/youtube_secrets.json")
        print("\nVedi README.md per istruzioni dettagliate.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Errore autenticazione: {e}")
        sys.exit(1)

    # Determina seduta da processare
    if len(sys.argv) > 1:
        seduta_url = sys.argv[1]
    else:
        # Default: ultima seduta disponibile
        seduta_url = "https://www.ars.sicilia.it/agenda/lavori-aula"

        print("URL seduta non specificato, cerco ultima seduta...")
        try:
            scraping_cfg = config.get('scraping', {})
            html = scraper.get_seduta_page(
                seduta_url,
                scraping_cfg.get('user_agent', 'ARS-YouTube-Bot/1.0'),
                timeout=scraping_cfg.get('timeout', 30),
                retries=scraping_cfg.get('retries', 3),
                backoff_factor=scraping_cfg.get('backoff_factor', 0.5)
            )

            # Trova link all'ultima seduta
            # Seleziona la seduta più recente in base alla data nell'URL
            candidates = []
            for link in html.find_all('a', href=True):
                href = link['href']
                if 'seduta-numero-' in href:
                    full_url = href if href.startswith('http') else f"https://www.ars.sicilia.it{href}"
                    seduta_date = extract_seduta_date_from_href(href)
                    candidates.append((seduta_date, full_url))

            if candidates:
                dated = [c for c in candidates if c[0]]
                if dated:
                    seduta_url = max(dated, key=lambda x: x[0])[1]
                else:
                    seduta_url = candidates[0][1]

            if seduta_url == "https://www.ars.sicilia.it/agenda/lavori-aula":
                print("✗ Impossibile trovare URL seduta")
                sys.exit(1)

        except Exception as e:
            print(f"✗ Errore ricerca ultima seduta: {e}")
            sys.exit(1)

    # Processa seduta
    try:
        results = process_seduta(seduta_url, config, youtube)

        # Statistiche finali
        stats = logger.get_upload_stats(config['logging']['log_file'])
        print(f"\nStatistiche totali:")
        print(f"  Upload riusciti:  {stats['success']}")
        print(f"  Upload falliti:   {stats['failed']}")
        print(f"  Totale video:     {stats['total']}")

        print("\n✓ Completato\n")

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
