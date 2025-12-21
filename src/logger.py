"""Gestione log CSV upload."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional


def init_log_file(log_path: str) -> bool:
    """
    Crea file CSV log se non esiste.

    Args:
        log_path: Path al file log CSV

    Returns:
        True se creato o già esistente
    """
    try:
        path = Path(log_path)

        # Crea directory se non esiste
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            with open(log_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'id_video',
                    'numero_seduta',
                    'data_seduta',
                    'data_video',
                    'ora_video',
                    'video_id_youtube',
                    'upload_timestamp',
                    'status',
                    'error_message'
                ])
            print(f"Log file creato: {log_path}")

        return True

    except Exception as e:
        print(f"Errore creazione log file: {e}")
        return False


def is_video_uploaded(log_path: str, id_video: str) -> bool:
    """
    Verifica se video è già stato uploadato.

    Args:
        log_path: Path al file log CSV
        id_video: ID video ARS

    Returns:
        True se video già uploadato con successo
    """
    try:
        path = Path(log_path)
        if not path.exists():
            return False

        with open(log_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id_video'] == id_video and row['status'] == 'success':
                    return True

        return False

    except Exception as e:
        print(f"Errore verifica video uploadato: {e}")
        return False


def log_upload(
    log_path: str,
    video_info: dict,
    youtube_id: str,
    status: str,
    error: str = ''
) -> bool:
    """
    Aggiunge entry al log.

    Args:
        log_path: Path al file log CSV
        video_info: Dict con info video
        youtube_id: ID video YouTube (vuoto se upload fallito)
        status: 'success' | 'failed' | 'pending'
        error: Messaggio errore (se status='failed')

    Returns:
        True se log scritto con successo
    """
    try:
        # Assicurati che log esista
        init_log_file(log_path)

        with open(log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                video_info.get('id_video', ''),
                video_info.get('numero_seduta', ''),
                video_info.get('data_seduta', ''),
                video_info.get('data_video', ''),
                video_info.get('ora_video', ''),
                youtube_id,
                datetime.now().isoformat(),
                status,
                error
            ])

        return True

    except Exception as e:
        print(f"Errore scrittura log: {e}")
        return False


def get_failed_uploads(log_path: str) -> list:
    """
    Ottiene lista upload falliti.

    Args:
        log_path: Path al file log CSV

    Returns:
        Lista dict con entry fallite
    """
    try:
        path = Path(log_path)
        if not path.exists():
            return []

        failed = []
        with open(log_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['status'] == 'failed':
                    failed.append(row)

        return failed

    except Exception as e:
        print(f"Errore lettura failed uploads: {e}")
        return []


def update_index(index_path: str, seduta_info: dict, videos_uploaded: list) -> bool:
    """
    Aggiorna indice pubblico CSV.

    Formato: numero_seduta, data_seduta, url_pagina, video_count

    Args:
        index_path: Path al file indice CSV
        seduta_info: Dict con info seduta
        videos_uploaded: Lista video uploadati

    Returns:
        True se aggiornato con successo
    """
    try:
        path = Path(index_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Leggi indice esistente
        sedute = {}
        if path.exists():
            with open(index_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sedute[row['numero_seduta']] = row

        # Aggiorna con nuova seduta
        numero = seduta_info['numero_seduta']
        sedute[numero] = {
            'numero_seduta': numero,
            'data_seduta': seduta_info['data_seduta'],
            'url_pagina': seduta_info['url_pagina'],
            'video_count': len(videos_uploaded)
        }

        # Scrivi indice aggiornato
        with open(index_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'numero_seduta', 'data_seduta', 'url_pagina', 'video_count'
            ])
            writer.writeheader()

            # Ordina per data decrescente
            sorted_sedute = sorted(
                sedute.values(),
                key=lambda x: x['data_seduta'] or '',
                reverse=True
            )
            writer.writerows(sorted_sedute)

        print(f"Indice aggiornato: {index_path}")
        return True

    except Exception as e:
        print(f"Errore aggiornamento indice: {e}")
        return False


def get_upload_stats(log_path: str) -> dict:
    """
    Ottiene statistiche upload.

    Args:
        log_path: Path al file log CSV

    Returns:
        Dict con statistiche
    """
    try:
        path = Path(log_path)
        if not path.exists():
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'pending': 0
            }

        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'pending': 0
        }

        with open(log_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats['total'] += 1
                status = row.get('status', '').lower()
                if status in stats:
                    stats[status] += 1

        return stats

    except Exception as e:
        print(f"Errore calcolo statistiche: {e}")
        return {
            'total': 0,
            'success': 0,
            'failed': 0,
            'pending': 0
        }
