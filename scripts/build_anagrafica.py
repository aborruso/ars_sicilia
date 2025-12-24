#!/usr/bin/env python3
"""
Build anagrafica filmati ARS.

Crawler incrementale che estrae metadati sedute ARS senza scaricare video.
Aggiorna CSV anagrafica con solo sedute nuove.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))


import csv
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Set

from src import scraper


def load_config(config_path: str = './config/config.yaml') -> dict:
    """Carica configurazione."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def init_anagrafica_csv(file_path: str) -> bool:
    """
    Crea file CSV anagrafica se non esiste.

    Args:
        file_path: Path al file CSV

    Returns:
        True se creato o già esistente
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        required_fields = [
            'numero_seduta',
            'data_seduta',
            'url_pagina',
            'odg_url',
            'resoconto_url',
            'resoconto_provvisorio_url',
            'resoconto_stenografico_url',
            'allegato_url',
            'id_video',
            'ora_video',
            'data_video',
            'stream_url',
            'video_page_url',
            'youtube_id',
            'last_check',
            'status',
            'failure_reason'
        ]

        if not path.exists():
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(required_fields)
            print(f"✓ Anagrafica creata: {file_path}")
            return True

        # File esistente: verifica schema e aggiungi colonne mancanti
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            missing = [f for f in required_fields if f not in fieldnames]
            if not missing:
                return True

            rows = []
            for row in reader:
                for key in missing:
                    row.setdefault(key, '')
                rows.append(row)

        # Riscrivi con header aggiornato
        new_fieldnames = fieldnames + missing
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=new_fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✓ Anagrafica aggiornata con nuove colonne: {', '.join(missing)}")

        return True

    except Exception as e:
        print(f"✗ Errore creazione anagrafica: {e}")
        return False


def load_existing_anagrafica(file_path: str) -> tuple[Set[str], Optional[str], dict]:
    """
    Carica anagrafica esistente con count video per seduta.

    Args:
        file_path: Path al file CSV

    Returns:
        Tuple (set numeri sedute processate, numero ultima seduta, dict{seduta: video_count})
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return set(), None, {}

        sedute_processate = set()
        ultima_seduta = None
        seduta_video_count = {}

        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                numero = row['numero_seduta']
                if numero:
                    sedute_processate.add(numero)
                    ultima_seduta = numero
                    # Conta video per seduta
                    seduta_video_count[numero] = seduta_video_count.get(numero, 0) + 1

        return sedute_processate, ultima_seduta, seduta_video_count

    except Exception as e:
        print(f"⚠ Errore lettura anagrafica: {e}")
        return set(), None, {}


def get_existing_youtube_ids(file_path: str, numero_seduta: str) -> dict:
    """
    Estrae youtube_id esistenti per una seduta usando chiave (data_video, ora_video).

    Args:
        file_path: Path al file CSV
        numero_seduta: Numero seduta

    Returns:
        Dict con chiave (data_video, ora_video) -> dict con youtube_id, status, failure_reason
    """
    existing_ids = {}
    try:
        path = Path(file_path)
        if not path.exists():
            return existing_ids

        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['numero_seduta'] == numero_seduta:
                    key = (row['data_video'], row['ora_video'])
                    existing_ids[key] = {
                        'youtube_id': row.get('youtube_id', ''),
                        'last_check': row.get('last_check', ''),
                        'status': row.get('status', ''),
                        'failure_reason': row.get('failure_reason', '')
                    }

    except Exception as e:
        print(f"⚠ Errore lettura youtube_id esistenti: {e}")

    return existing_ids


def remove_seduta_from_anagrafica(file_path: str, numero_seduta: str) -> bool:
    """
    Rimuove tutti i video di una seduta dall'anagrafica.

    Args:
        file_path: Path al file CSV
        numero_seduta: Numero seduta da rimuovere

    Returns:
        True se rimosso con successo
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False

        # Leggi tutte le righe tranne quelle della seduta da rimuovere
        rows_to_keep = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['numero_seduta'] != numero_seduta:
                    rows_to_keep.append(row)

        # Riscrivi file senza le righe rimosse
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_keep)

        return True

    except Exception as e:
        print(f"✗ Errore rimozione seduta: {e}")
        return False


def save_seduta_to_anagrafica(file_path: str, seduta_info: dict, existing_youtube_ids: dict = None) -> int:
    """
    Salva seduta in anagrafica CSV preservando youtube_id esistenti.

    Args:
        file_path: Path al file CSV
        seduta_info: Dict con info seduta (da scraper)
        existing_youtube_ids: Dict opzionale con youtube_id esistenti (chiave: (data_video, ora_video))

    Returns:
        Numero video salvati
    """
    try:
        timestamp = datetime.now().isoformat()
        video_count = 0
        if existing_youtube_ids is None:
            existing_youtube_ids = {}

        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            numero_seduta = seduta_info['numero_seduta']
            data_seduta = seduta_info['data_seduta']
            url_pagina = seduta_info['url_pagina']
            odg_url = seduta_info.get('odg_url', '')
            resoconto_url = seduta_info.get('resoconto_url', '')
            resoconto_provvisorio_url = seduta_info.get('resoconto_provvisorio_url', '')
            resoconto_stenografico_url = seduta_info.get('resoconto_stenografico_url', '')
            allegato_url = seduta_info.get('allegato_url', '')

            # Scrivi una riga per ogni video
            for video in seduta_info['videos']:
                data_video = video.get('data_video', data_seduta)
                ora_video = video['ora_video']

                # Recupera youtube_id esistente se presente (chiave: data_video + ora_video)
                key = (data_video, ora_video)
                existing = existing_youtube_ids.get(key, {})
                youtube_id = existing.get('youtube_id', '')
                status = existing.get('status', '')
                failure_reason = existing.get('failure_reason', '')
                # Preserva last_check se youtube_id esiste (non aggiornare timestamp per video già uploadati)
                last_check = existing.get('last_check', '') if youtube_id else timestamp

                writer.writerow([
                    numero_seduta,
                    data_seduta,
                    url_pagina,
                    odg_url,
                    resoconto_url,
                    resoconto_provvisorio_url,
                    resoconto_stenografico_url,
                    allegato_url,
                    video['id_video'],
                    ora_video,
                    data_video,
                    video.get('stream_url', ''),
                    video.get('video_page_url', ''),
                    youtube_id,  # Preservato da record esistente
                    last_check,  # Preservato per video uploadati, nuovo timestamp per video nuovi
                    status,
                    failure_reason
                ])
                video_count += 1

        return video_count

    except Exception as e:
        print(f"✗ Errore salvataggio seduta: {e}")
        return 0


def crawl_nuove_sedute(config: dict, sedute_processate: Set[str], seduta_video_count: dict, start_url: str) -> dict:
    """
    Crawla sedute nuove partendo dal 10 dicembre 2025 e andando verso il futuro.

    Args:
        config: Configurazione
        sedute_processate: Set numeri sedute già processate
        start_url: URL da cui partire

    Returns:
        Dict con statistiche
    """
    stats = {
        'sedute_nuove': 0,
        'sedute_skip': 0,
        'sedute_aggiornate': 0,
        'video_totali': 0,
        'errori': 0
    }

    current_url = start_url
    anagrafica_file = config['logging']['anagrafica_file']

    print(f"\n{'='*70}")
    print(f"Crawler sedute ARS")
    print(f"{'='*70}\n")

    while current_url:
        try:
            print(f"Analisi: {current_url}")

            # Scarica pagina
            scraping_cfg = config.get('scraping', {})
            html = scraper.get_seduta_page(
                current_url,
                scraping_cfg.get('user_agent', 'ARS-YouTube-Bot/1.0'),
                timeout=scraping_cfg.get('timeout', 30),
                retries=scraping_cfg.get('retries', 3),
                backoff_factor=scraping_cfg.get('backoff_factor', 0.5)
            )

            # Estrai info
            seduta_info = scraper.extract_seduta_info(html, current_url)
            numero_seduta = seduta_info['numero_seduta']
            video_count_new = len(seduta_info['videos'])
            start_date = config.get('scraping', {}).get('start_date')

            if start_date and seduta_info.get('data_seduta'):
                if seduta_info['data_seduta'] < start_date:
                    print(f"  ⊙ Seduta {numero_seduta} prima di start_date ({start_date}), skip")
                    current_url = scraper.get_next_seduta_url(html, numero_seduta, go_forward=True)
                    continue

            # Verifica se già processata
            if numero_seduta in sedute_processate:
                video_count_old = seduta_video_count.get(numero_seduta, 0)

                # Sempre aggiorna sedute recenti (ultimi 14 giorni)
                # perché l'ARS può cambiare gli ID video anche senza cambiare il count
                from datetime import date, timedelta
                is_recent = False
                if seduta_info.get('data_seduta'):
                    cutoff_date = (date.today() - timedelta(days=14)).isoformat()
                    is_recent = seduta_info['data_seduta'] >= cutoff_date

                # Se count video è uguale e NON è recente, skip
                if video_count_new == video_count_old and not is_recent:
                    print(f"  ⊙ Seduta {numero_seduta} già in anagrafica ({video_count_old} video), skip")
                    stats['sedute_skip'] += 1
                    current_url = scraper.get_next_seduta_url(html, numero_seduta, go_forward=True)
                    continue

                # Aggiorna se count diverso o se recente
                reason = f"{video_count_old} → {video_count_new} video" if video_count_new != video_count_old else "seduta recente"
                print(f"  ↻ Seduta {numero_seduta} aggiornata: {reason}")

                # Salva youtube_id esistenti prima di rimuovere
                existing_youtube_ids = get_existing_youtube_ids(anagrafica_file, numero_seduta)

                # Rimuovi video vecchi dall'anagrafica
                remove_seduta_from_anagrafica(anagrafica_file, numero_seduta)
                sedute_processate.remove(numero_seduta)
                stats['sedute_aggiornate'] += 1
                # Continua per salvare nuovi dati con youtube_id preservati
            else:
                # Nuova seduta, nessun youtube_id da preservare
                existing_youtube_ids = {}

            # Nuova seduta
            print(f"  ✓ Seduta {numero_seduta} del {seduta_info['data_seduta']}")
            print(f"    Video trovati: {len(seduta_info['videos'])}")

            if seduta_info.get('odg_url'):
                print(f"    OdG: presente")
            if seduta_info.get('resoconto_url'):
                print(f"    Resoconto: presente")

            # Salva in anagrafica preservando youtube_id esistenti
            video_count = save_seduta_to_anagrafica(anagrafica_file, seduta_info, existing_youtube_ids)

            if video_count > 0:
                print(f"    Salvati {video_count} video in anagrafica")
                stats['sedute_nuove'] += 1
                stats['video_totali'] += video_count
                sedute_processate.add(numero_seduta)

            # Cerca prossima seduta FUTURA (numero maggiore)
            current_url = scraper.get_next_seduta_url(html, numero_seduta, go_forward=True)

        except Exception as e:
            print(f"  ✗ Errore: {e}")
            stats['errori'] += 1
            # Continua con prossima seduta FUTURA
            try:
                if 'seduta_info' in locals() and seduta_info.get('numero_seduta'):
                    current_url = scraper.get_next_seduta_url(html, seduta_info['numero_seduta'], go_forward=True)
                else:
                    current_url = None
            except:
                current_url = None

    return stats


def main():
    """Main entry point."""
    print("ARS - Build Anagrafica Filmati\n")

    # Carica config
    try:
        config = load_config()
    except Exception as e:
        print(f"✗ Errore config: {e}")
        sys.exit(1)

    anagrafica_file = config['logging']['anagrafica_file']

    # Init anagrafica
    init_anagrafica_csv(anagrafica_file)

    # Carica anagrafica esistente
    print("Caricamento anagrafica esistente...")
    sedute_processate, ultima_seduta, seduta_video_count = load_existing_anagrafica(anagrafica_file)

    if sedute_processate:
        print(f"  Sedute già processate: {len(sedute_processate)}")
        if ultima_seduta:
            print(f"  Ultima seduta: {ultima_seduta}")
    else:
        print(f"  Anagrafica vuota, primo run")

    # Determina URL di partenza
    start_url = config['scraping']['start_url']

    print(f"\nURL partenza: {start_url}")

    # Crawl nuove sedute
    try:
        stats = crawl_nuove_sedute(config, sedute_processate, seduta_video_count, start_url)

        # Riepilogo
        print(f"\n{'='*70}")
        print(f"Riepilogo:")
        print(f"  Sedute nuove:        {stats['sedute_nuove']}")
        print(f"  Sedute aggiornate:   {stats['sedute_aggiornate']}")
        print(f"  Sedute già viste:    {stats['sedute_skip']}")
        print(f"  Video totali:        {stats['video_totali']}")
        print(f"  Errori:              {stats['errori']}")
        print(f"{'='*70}\n")

        print(f"✓ Anagrafica aggiornata: {anagrafica_file}\n")

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
