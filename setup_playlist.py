#!/usr/bin/env python3
"""
Setup playlist annuale e aggiunta video esistenti.

Crea playlist per anno specificato e aggiunge video dall'anagrafica.
"""

import sys
import yaml
import csv
from pathlib import Path

from src import uploader
from src.utils import extract_year


def main():
    print("\n" + "="*70)
    print("SETUP PLAYLIST ANNUALE")
    print("="*70 + "\n")

    # Carica config
    with open('./config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Autenticazione YouTube
    print("🔐 Autenticazione YouTube...")
    print("  ℹ️  Si aprirà il browser per autorizzare i nuovi permessi")
    print("  ℹ️  Accetta la richiesta di gestione completa del canale\n")
    
    try:
        youtube = uploader.authenticate(
            config['youtube']['credentials_file'],
            config['youtube']['token_file']
        )
        
        # Ottieni info canale
        channel_info = uploader.get_channel_info(youtube)
        if channel_info:
            print(f"  ✓ Canale: {channel_info['title']}\n")
        
    except Exception as e:
        print(f"  ✗ Errore autenticazione: {e}")
        return 1

    # Crea playlist 2025
    print("📋 Creazione playlist ARS 2025...")
    playlist_id = uploader.create_playlist(
        youtube,
        year="2025",
        title="ARS 2025 - Sedute Assemblea",
        description="Sedute Assemblea Regionale Siciliana - Anno 2025\n\nVideo pubblicati automaticamente dal sistema di archiviazione ARS."
    )
    
    if not playlist_id:
        print("  ✗ Creazione playlist fallita")
        return 1

    # Trova video 2025 da anagrafica
    print(f"\n📄 Ricerca video anno 2025 in anagrafica...")
    anagrafica_path = config['logging']['anagrafica_file']
    videos_2025 = []
    
    try:
        with open(anagrafica_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('youtube_id') and row.get('data_video'):
                    year = extract_year(row['data_video'])
                    if year == "2025":
                        videos_2025.append({
                            'youtube_id': row['youtube_id'],
                            'numero_seduta': row['numero_seduta'],
                            'data_video': row['data_video'],
                            'ora_video': row['ora_video']
                        })
    except Exception as e:
        print(f"  ✗ Errore lettura anagrafica: {e}")
        return 1

    if not videos_2025:
        print("  ℹ️  Nessun video 2025 trovato in anagrafica")
        print("\n" + "="*70)
        print("PLAYLIST CREATA!")
        print(f"Aggiungi questo ID a config/config.yaml:")
        print(f"  playlists:")
        print(f"    \"2025\": \"{playlist_id}\"")
        print("="*70)
        return 0

    print(f"  ✓ Trovati {len(videos_2025)} video anno 2025\n")

    # Aggiungi video a playlist
    print(f"➕ Aggiunta video a playlist...")
    success_count = 0
    
    for video in videos_2025:
        print(f"  - Seduta {video['numero_seduta']} ({video['data_video']} {video['ora_video']}): ", end='')
        
        if uploader.add_video_to_playlist(youtube, video['youtube_id'], playlist_id):
            success_count += 1
            print("✓")
        else:
            print("✗")

    print(f"\n✅ Completato: {success_count}/{len(videos_2025)} video aggiunti\n")

    # Istruzioni finali
    print("="*70)
    print("PLAYLIST CREATA E CONFIGURATA!")
    print(f"\nPlaylist URL: https://www.youtube.com/playlist?list={playlist_id}")
    print(f"\nAggiungi questo ID a config/config.yaml:")
    print(f"  playlists:")
    print(f"    \"2025\": \"{playlist_id}\"")
    print("="*70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
