#!/usr/bin/env python3
"""Test autenticazione YouTube OAuth2 con flow manuale."""

from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def authenticate_manual(secrets_file: str, token_file: str):
    """Autenticazione OAuth2 con URL manuale (per WSL)."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

    creds = None

    if not Path(secrets_file).exists():
        raise FileNotFoundError(f"File credenziali non trovato: {secrets_file}")

    # Carica token esistente
    if Path(token_file).exists():
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            print("✓ Token OAuth2 caricato")
        except Exception as e:
            print(f"⚠ Errore caricamento token: {e}")
            creds = None

    # Refresh o nuovo flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Refresh token OAuth2...")
                creds.refresh(Request())
                print("✓ Token refreshato")
            except Exception as e:
                print(f"⚠ Errore refresh: {e}")
                creds = None

        if not creds:
            print("\n" + "="*60)
            print("AUTENTICAZIONE OAUTH2 RICHIESTA")
            print("="*60)
            print("\nApri questo URL nel browser:\n")

            flow = InstalledAppFlow.from_client_secrets_file(
                secrets_file,
                SCOPES,
                redirect_uri='http://localhost:8080/'
            )

            # Ottieni URL di autorizzazione
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(auth_url)

            print("\nDopo aver autorizzato, copia qui l'URL completo di redirect")
            print("(quello che inizia con http://localhost:8080/?...): ")

            redirect_response = input().strip()

            # Completa il flow
            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials

            print("\n✓ Autenticazione completata")

        # Salva token
        Path(token_file).parent.mkdir(parents=True, exist_ok=True)
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
        print(f"✓ Token salvato: {token_file}")

    youtube = build('youtube', 'v3', credentials=creds)
    return youtube


def main():
    """Test credenziali."""
    secrets_file = "config/youtube_secrets.json"
    token_file = "config/token.json"

    print("Test autenticazione YouTube (flow manuale)")
    print("="*60 + "\n")

    try:
        # Autenticazione
        youtube = authenticate_manual(secrets_file, token_file)
        print("\n✓ Client YouTube API creato\n")

        # Info canale
        print("Recupero informazioni canale...")
        request = youtube.channels().list(
            part='snippet,statistics',
            mine=True
        )
        response = request.execute()

        if response.get('items'):
            channel = response['items'][0]
            print("\n" + "="*60)
            print("INFORMAZIONI CANALE")
            print("="*60)
            print(f"ID:          {channel['id']}")
            print(f"Nome:        {channel['snippet']['title']}")
            print(f"Descrizione: {channel['snippet']['description'][:100]}...")
            print(f"Video:       {channel['statistics'].get('videoCount', 0)}")
            print("="*60)

            print("\n✓ Test completato! Le credenziali funzionano.")
            print("Puoi procedere con gli upload dei video ARS.")

        else:
            print("❌ Nessun canale trovato")
            return 1

        return 0

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
