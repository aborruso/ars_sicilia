#!/usr/bin/env python3
"""Completa autenticazione OAuth2 con URL di redirect."""

import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly'
]


def complete_auth(redirect_url: str):
    """Completa autenticazione con URL di redirect."""
    secrets_file = "config/youtube_secrets.json"
    token_file = "config/token.json"

    print("Completamento autenticazione OAuth2...")

    # Crea flow
    flow = InstalledAppFlow.from_client_secrets_file(
        secrets_file,
        SCOPES,
        redirect_uri='http://localhost:8080/'
    )

    # Fetch token da URL di redirect
    flow.fetch_token(authorization_response=redirect_url)
    creds = flow.credentials

    # Salva token
    Path(token_file).parent.mkdir(parents=True, exist_ok=True)
    with open(token_file, 'w') as f:
        f.write(creds.to_json())
    print(f"✓ Token salvato: {token_file}\n")

    # Test connessione
    youtube = build('youtube', 'v3', credentials=creds)
    print("Verifica canale...")

    request = youtube.channels().list(
        part='snippet,statistics',
        mine=True
    )
    response = request.execute()

    if response.get('items'):
        channel = response['items'][0]
        print("\n" + "="*60)
        print("CANALE YOUTUBE AUTENTICATO")
        print("="*60)
        print(f"ID:          {channel['id']}")
        print(f"Nome:        {channel['snippet']['title']}")
        print(f"Video:       {channel['statistics'].get('videoCount', 0)}")
        print("="*60)
        print("\n✓ Autenticazione completata!")
        print("Ora puoi usare gli script di upload per le sedute ARS.")
        return 0
    else:
        print("❌ Nessun canale trovato")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 complete_auth.py 'http://localhost:8080/?...'")
        sys.exit(1)

    try:
        exit(complete_auth(sys.argv[1]))
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
