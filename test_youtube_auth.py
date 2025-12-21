#!/usr/bin/env python3
"""Test autenticazione YouTube OAuth2."""

from pathlib import Path
from src.uploader import authenticate, get_channel_info, check_quota_usage


def main():
    """Test credenziali YouTube."""
    secrets_file = "config/youtube_secrets.json"
    token_file = "config/token.json"

    print("Test autenticazione YouTube\n" + "="*50)

    # Verifica che il file secrets esista
    if not Path(secrets_file).exists():
        print(f"❌ File credenziali non trovato: {secrets_file}")
        return 1

    print(f"✓ File credenziali trovato: {secrets_file}\n")

    try:
        # Autenticazione
        print("Autenticazione in corso...")
        youtube = authenticate(secrets_file, token_file)
        print("✓ Autenticazione riuscita!\n")

        # Info canale
        print("Recupero informazioni canale...")
        channel_info = get_channel_info(youtube)

        if channel_info:
            print("✓ Informazioni canale:\n")
            print(f"  ID:          {channel_info['id']}")
            print(f"  Nome:        {channel_info['title']}")
            print(f"  URL custom:  {channel_info.get('customUrl', 'N/A')}")
            print(f"  Video:       {channel_info.get('videoCount', 0)}")
            print(f"  Descrizione: {channel_info['description'][:100]}...")
        else:
            print("❌ Impossibile recuperare informazioni canale")
            return 1

        # Quota info
        print("\n" + "="*50)
        quota = check_quota_usage(youtube)
        print("Informazioni quota YouTube API:\n")
        print(f"  Limite giornaliero:     {quota['daily_limit']} punti")
        print(f"  Costo per upload:       {quota['upload_cost']} punti")
        print(f"  Max upload giornalieri: {quota['max_daily_uploads']}")
        print(f"  Nota: {quota['note']}")

        print("\n" + "="*50)
        print("✓ Test completato con successo!")
        print("\nPuoi procedere con gli upload dei video delle sedute ARS.")

        return 0

    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Errore: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
