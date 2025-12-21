#!/usr/bin/env python3
"""Genera URL di autorizzazione OAuth2."""

from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly'
]


def main():
    """Genera URL di autorizzazione."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

    secrets_file = "config/youtube_secrets.json"

    print("\n" + "="*60)
    print("AUTENTICAZIONE YOUTUBE OAUTH2")
    print("="*60)

    flow = InstalledAppFlow.from_client_secrets_file(
        secrets_file,
        SCOPES,
        redirect_uri='http://localhost:8080/'
    )

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

    print("\nApri questo URL nel browser:\n")
    print(auth_url)
    print("\n" + "="*60)
    print("\nDopo l'autorizzazione, copia l'URL completo di redirect")
    print("(quello che inizia con http://localhost:8080/?...)")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
