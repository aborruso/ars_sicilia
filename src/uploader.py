"""Upload video su YouTube con OAuth2."""

import os
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube'  # Gestione completa canale (include playlist)
]


def authenticate(secrets_file: str, token_file: str):
    """
    Autenticazione OAuth2 YouTube.

    Al primo avvio apre browser per autenticazione interattiva.
    Successivamente usa refresh token salvato.

    Args:
        secrets_file: Path al file credenziali OAuth2 da Google Cloud Console
        token_file: Path dove salvare/caricare token

    Returns:
        YouTube API client

    Raises:
        FileNotFoundError: Se secrets_file non esiste
        Exception: Se autenticazione fallisce
    """
    creds = None

    # Verifica che secrets file esista
    if not Path(secrets_file).exists():
        raise FileNotFoundError(
            f"File credenziali non trovato: {secrets_file}\n"
            "Scaricalo da Google Cloud Console e salvalo come config/youtube_secrets.json"
        )

    # Carica token esistente se presente
    if Path(token_file).exists():
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            print("Token OAuth2 caricato")
        except Exception as e:
            print(f"Errore caricamento token: {e}")
            creds = None

    # Se token non valido o scaduto, refresha o crea nuovo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Refresh token OAuth2...")
                creds.refresh(Request())
                print("Token refreshato")
            except Exception as e:
                print(f"Errore refresh token: {e}")
                creds = None

        # Se ancora non valido, avvia flow interattivo
        if not creds:
            print("Avvio autenticazione OAuth2 interattiva...")
            print("Si aprirà il browser per autorizzare l'applicazione.")

            flow = InstalledAppFlow.from_client_secrets_file(secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
            print("Autenticazione completata")

        # Salva token per prossime esecuzioni
        Path(token_file).parent.mkdir(parents=True, exist_ok=True)
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
        print(f"Token salvato: {token_file}")

    # Crea client YouTube API
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube


def upload_video(youtube, file_path: str, metadata: dict, playlist_id: Optional[str] = None) -> Optional[str]:
    """
    Upload video su YouTube e aggiunta a playlist (opzionale).

    Args:
        youtube: YouTube API client
        file_path: Path al file video
        metadata: Dict con metadati video
        playlist_id: ID playlist YouTube (opzionale)

    Returns:
        ID video YouTube o None se fallito

    Raises:
        FileNotFoundError: Se file non esiste
        HttpError: Se upload fallisce
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File video non trovato: {file_path}")

    print(f"  Upload video su YouTube...")

    # Costruisci body richiesta
    body = {
        'snippet': {
            'title': metadata['title'],
            'description': metadata['description'],
            'tags': metadata.get('tags', []),
            'categoryId': metadata.get('category', '25'),
            'defaultLanguage': metadata.get('defaultLanguage', 'it')
        },
        'status': {
            'privacyStatus': metadata.get('privacy', 'public')
        }
    }

    # Aggiungi recordingDate se presente
    if metadata.get('recordingDate'):
        body['recordingDetails'] = {
            'recordingDate': metadata['recordingDate']
        }

    # Prepara file per upload
    media = MediaFileUpload(
        file_path,
        chunksize=-1,  # Upload in un solo chunk
        resumable=True,
        mimetype='video/*'
    )

    try:
        # Crea richiesta upload
        parts = ['snippet', 'status']
        if 'recordingDetails' in body:
            parts.append('recordingDetails')

        request = youtube.videos().insert(
            part=','.join(parts),
            body=body,
            media_body=media
        )

        # Esegui upload
        print(f"  Upload in corso...")
        response = request.execute()

        video_id = response.get('id')
        if video_id:
            print(f"  ✓ Video caricato: https://youtube.com/watch?v={video_id}")

            # Aggiungi a playlist se specificato
            if playlist_id:
                add_video_to_playlist(youtube, video_id, playlist_id)

            return video_id
        else:
            print(f"  ✗ Upload fallito: nessun ID restituito")
            return None

    except HttpError as e:
        print(f"  ✗ Errore HTTP upload: {e}")
        raise
    except Exception as e:
        print(f"  ✗ Errore upload: {e}")
        raise


def get_channel_info(youtube) -> Optional[dict]:
    """
    Ottiene informazioni sul canale YouTube autenticato.

    Args:
        youtube: YouTube API client

    Returns:
        Dict con info canale o None
    """
    try:
        request = youtube.channels().list(
            part='snippet,contentDetails,statistics',
            mine=True
        )
        response = request.execute()

        if response.get('items'):
            channel = response['items'][0]
            return {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'customUrl': channel['snippet'].get('customUrl'),
                'videoCount': channel['statistics'].get('videoCount', 0)
            }

        return None

    except Exception as e:
        print(f"Errore get_channel_info: {e}")
        return None


def create_playlist(youtube, year: str, title: str = None, description: str = None) -> Optional[str]:
    """
    Crea nuova playlist YouTube per anno.

    Args:
        youtube: YouTube API client
        year: Anno (es. "2025")
        title: Titolo playlist (default: "ARS {anno} - Sedute Assemblea")
        description: Descrizione (default auto-generata)

    Returns:
        Playlist ID o None se fallito
    """
    if not title:
        title = f"ARS {year} - Sedute Assemblea"

    if not description:
        description = f"Sedute Assemblea Regionale Siciliana - Anno {year}\n\nVideo pubblicati automaticamente."

    try:
        request = youtube.playlists().insert(
            part='snippet,status',
            body={
                'snippet': {
                    'title': title,
                    'description': description,
                    'defaultLanguage': 'it'
                },
                'status': {
                    'privacyStatus': 'public'
                }
            }
        )
        response = request.execute()

        playlist_id = response.get('id')
        if playlist_id:
            print(f"  ✓ Playlist creata: {title}")
            print(f"  ID: {playlist_id}")
            print(f"  URL: https://www.youtube.com/playlist?list={playlist_id}")
            return playlist_id
        else:
            print(f"  ✗ Creazione playlist fallita: nessun ID restituito")
            return None

    except HttpError as e:
        print(f"  ✗ Errore HTTP creazione playlist: {e}")
        return None
    except Exception as e:
        print(f"  ✗ Errore creazione playlist: {e}")
        return None


def add_video_to_playlist(youtube, video_id: str, playlist_id: str) -> bool:
    """
    Aggiunge video a playlist YouTube.

    Args:
        youtube: YouTube API client
        video_id: ID video YouTube
        playlist_id: ID playlist YouTube

    Returns:
        True se successo, False altrimenti
    """
    try:
        request = youtube.playlistItems().insert(
            part='snippet',
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        )
        response = request.execute()
        print(f"  ✓ Video aggiunto a playlist: {playlist_id}")
        return True

    except HttpError as e:
        print(f"  ✗ Errore aggiunta a playlist: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Errore aggiunta a playlist: {e}")
        return False


def get_or_create_playlist_for_year(youtube, config: dict, year: str, auto_create: bool = True) -> Optional[str]:
    """
    Ottiene playlist ID per anno dalla configurazione o la crea automaticamente.

    Args:
        youtube: YouTube API client
        config: Dict configurazione
        year: Anno (es. "2025")
        auto_create: Se True, crea playlist se non esiste (default: True)

    Returns:
        Playlist ID o None se non configurato/creato
    """
    playlists = config.get('youtube', {}).get('playlists', {})
    playlist_id = playlists.get(year)

    if playlist_id:
        return playlist_id

    # Playlist non configurata
    if not auto_create:
        print(f"  ⚠ Playlist per anno {year} non configurata")
        return None

    # Crea playlist automaticamente
    print(f"  📋 Playlist anno {year} non trovata, creazione automatica...")
    playlist_id = create_playlist(youtube, year)

    if playlist_id:
        # Salva ID in config per riutilizzo (solo in memoria, non su file)
        if 'youtube' not in config:
            config['youtube'] = {}
        if 'playlists' not in config['youtube']:
            config['youtube']['playlists'] = {}
        config['youtube']['playlists'][year] = playlist_id

        print(f"  ℹ️  Aggiungi questo ID a config/config.yaml per riutilizzo:")
        print(f"     playlists:")
        print(f"       \"{year}\": \"{playlist_id}\"")

    return playlist_id


def get_playlist_id_for_year(config: dict, year: str) -> Optional[str]:
    """
    Ottiene playlist ID per anno dalla configurazione (deprecato, usa get_or_create_playlist_for_year).

    Args:
        config: Dict configurazione
        year: Anno (es. "2025")

    Returns:
        Playlist ID o None se non configurato
    """
    playlists = config.get('youtube', {}).get('playlists', {})
    playlist_id = playlists.get(year)

    if not playlist_id:
        print(f"  ⚠ Playlist per anno {year} non configurata")
        return None

    return playlist_id


def check_quota_usage(youtube) -> Optional[dict]:
    """
    Verifica quota API YouTube utilizzata (approssimata).

    NOTA: La quota esatta non è disponibile via API.
    Questa funzione fornisce solo una stima basata su upload recenti.

    Args:
        youtube: YouTube API client

    Returns:
        Dict con stima quota o None
    """
    # YouTube API non espone quota usage direttamente
    # Questa è solo una stima
    return {
        'daily_limit': 10000,
        'upload_cost': 1600,
        'playlist_cost': 50,
        'total_cost_per_video': 1650,
        'max_daily_uploads': 6,
        'note': 'Quota esatta disponibile solo su Google Cloud Console'
    }
