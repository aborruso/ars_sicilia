"""Downloader video HLS usando yt-dlp."""

import subprocess
import time
from pathlib import Path
from typing import Optional


def download_video(
    video_url: str,
    output_path: str,
    retries: int = 3,
    max_height: int | None = None
) -> bool:
    """
    Download video HLS usando yt-dlp.

    Args:
        video_url: URL video (m3u8 o pagina video ARS)
        output_path: Path dove salvare il video MP4
        retries: Numero di tentativi

    Returns:
        True se download riuscito, False altrimenti
    """
    for attempt in range(retries):
        try:
            print(f"  Download tentativo {attempt + 1}/{retries}...")

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            format_selector = 'best'
            if max_height:
                format_selector = (
                    f'bestvideo[height<={max_height}]+bestaudio/'
                    f'best[height<={max_height}]/best'
                )

            cmd = [
                'yt-dlp',
                '-f', format_selector,
                '--no-playlist',
                '--progress',  # Mostra barra progresso
                '--newline',   # Una linea per update
                '-o', output_path,
                video_url
            ]

            # Non catturare output per mostrare progresso in tempo reale
            result = subprocess.run(
                cmd,
                timeout=3600  # 1 ora max per video
            )

            if result.returncode == 0:
                # Verifica che il file esista
                if Path(output_path).exists():
                    file_size = Path(output_path).stat().st_size
                    print(f"  ✓ Download completato: {file_size / 1024 / 1024:.1f} MB")
                    return True
                else:
                    print(f"  ✗ Errore: file non trovato dopo download")
                    return False
            else:
                print(f"  ✗ Download fallito (exit code {result.returncode})")

                # Se ultimo tentativo fallito
                if attempt == retries - 1:
                    return False

                # Backoff esponenziale
                wait_time = 2 ** attempt
                print(f"  Attendo {wait_time}s prima di riprovare...")
                time.sleep(wait_time)

        except subprocess.TimeoutExpired:
            print(f"  Timeout download (>1h)")
            return False
        except Exception as e:
            print(f"  Errore download: {e}")
            if attempt == retries - 1:
                return False
            time.sleep(2 ** attempt)

    return False


def get_video_stream_url(video_page_url: str) -> Optional[str]:
    """
    Estrae URL stream m3u8 da pagina video ARS.

    Args:
        video_page_url: URL pagina video (es. https://...

/video/2484769)

    Returns:
        URL stream m3u8 o None
    """
    try:
        # Usa yt-dlp per estrarre URL stream senza scaricare
        cmd = [
            'yt-dlp',
            '--get-url',
            '-f', 'best',
            video_page_url
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            stream_url = result.stdout.strip()
            return stream_url if stream_url else None
        else:
            print(f"  Errore estrazione URL: {result.stderr}")
            return None

    except Exception as e:
        print(f"  Errore get_video_stream_url: {e}")
        return None


def cleanup_video(file_path: str) -> bool:
    """
    Elimina file video.

    Args:
        file_path: Path al file video

    Returns:
        True se eliminato con successo
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            print(f"  File eliminato: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"  Errore eliminazione file: {e}")
        return False


def get_video_duration(file_path: str) -> Optional[float]:
    """
    Ottiene durata video in secondi.

    Args:
        file_path: Path al file video

    Returns:
        Durata in secondi o None
    """
    try:
        # Usa ffprobe se disponibile
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return float(result.stdout.strip())

    except Exception as e:
        print(f"  Errore get_video_duration: {e}")

    return None


def cleanup_old_videos(directory: str, max_age_hours: int = 24) -> int:
    """
    Elimina video più vecchi di max_age_hours.

    Args:
        directory: Directory contenente video
        max_age_hours: Età massima in ore

    Returns:
        Numero di file eliminati
    """
    import os
    from datetime import datetime, timedelta

    try:
        path = Path(directory)
        if not path.exists():
            return 0

        threshold = datetime.now() - timedelta(hours=max_age_hours)
        count = 0

        for file in path.glob('*.mp4'):
            if file.is_file():
                file_time = datetime.fromtimestamp(file.stat().st_mtime)
                if file_time < threshold:
                    file.unlink()
                    count += 1
                    print(f"  Eliminato vecchio video: {file.name}")

        return count

    except Exception as e:
        print(f"  Errore cleanup_old_videos: {e}")
        return 0
