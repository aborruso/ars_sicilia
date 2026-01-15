#!/usr/bin/env python3
"""
Interroga la playlist YouTube per recuperare gli ultimi video.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import yaml
from src import uploader

REPO_ROOT = Path(__file__).resolve().parents[2]

def get_playlist_videos(youtube, playlist_id: str, max_results: int = 10):
    """Recupera gli ultimi video dalla playlist."""
    try:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=max_results
        )
        response = request.execute()

        videos = []
        for item in response.get('items', []):
            video_id = item['contentDetails']['videoId']
            title = item['snippet']['title']
            published_at = item['snippet']['publishedAt']
            position = item['snippet']['position']

            videos.append({
                'video_id': video_id,
                'title': title,
                'published_at': published_at,
                'position': position,
                'url': f"https://youtube.com/watch?v={video_id}"
            })

        return videos
    except Exception as e:
        print(f"Errore recupero video: {e}")
        return []


def main():
    print("\n" + "="*70)
    print("CHECK PLAYLIST YOUTUBE")
    print("="*70 + "\n")

    # Carica config
    config_path = REPO_ROOT / 'config' / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

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

    # Recupera playlist ID per 2025
    playlist_id = config.get('youtube', {}).get('playlists', {}).get('2025')
    if not playlist_id:
        print("  ✗ Playlist ID 2025 non trovato in config")
        return 1

    print(f"📋 Playlist 2025: {playlist_id}")
    print(f"   URL: https://www.youtube.com/playlist?list={playlist_id}\n")

    # Recupera ultimi video
    print("📹 Ultimi video nella playlist:\n")
    videos = get_playlist_videos(youtube, playlist_id, max_results=10)

    if not videos:
        print("  Nessun video trovato")
        return 0

    # Mostra ultimi video
    print(f"{'Pos':<4} {'Video ID':<15} {'Titolo':<50} {'Data pubblicazione'}")
    print("-" * 100)

    for video in reversed(videos[-5:]):  # Ultimi 5 in ordine cronologico
        pos = video['position'] + 1
        vid_id = video['video_id']
        title = video['title'][:47] + "..." if len(video['title']) > 50 else video['title']
        pub_date = video['published_at'][:10]

        print(f"{pos:<4} {vid_id:<15} {title:<50} {pub_date}")
        print(f"     {video['url']}")

    print("\n" + "="*70)
    return 0


if __name__ == '__main__':
    sys.exit(main())
