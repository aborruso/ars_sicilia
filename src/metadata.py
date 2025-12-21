"""Costruzione metadati YouTube."""

from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote

from .utils import format_date_italian, extract_year, extract_month_name


def build_title(seduta_info: dict, video_info: dict) -> str:
    """
    Costruisce titolo video YouTube.

    Formato: "Lavori d'aula: seduta n. 219/A del 10 Dicembre 2025 - 11:30"

    Args:
        seduta_info: Dict con info seduta
        video_info: Dict con info video

    Returns:
        Titolo formattato
    """
    data_seduta_formattata = format_date_italian(seduta_info['data_seduta'])
    data_video_formattata = format_date_italian(video_info['data_video'] or seduta_info['data_seduta'])
    numero = seduta_info['numero_seduta']
    ora = video_info['ora_video']

    return (
        f"Lavori d'aula: seduta n. {numero} ({data_seduta_formattata}), "
        f"{data_video_formattata} dalle ore {ora}"
    )


def build_seduta_token(seduta_info: dict) -> str | None:
    """
    Costruisce token univoco per seduta.

    Formato: ARS_SEDUTA_{numero}-{data} (es. ARS_SEDUTA_219-2025-12-10)
    """
    if not seduta_info.get('numero_seduta') or not seduta_info.get('data_seduta'):
        return None
    numero_token = seduta_info['numero_seduta'].replace('/', '-')
    return f"ARS_SEDUTA_{numero_token}-{seduta_info['data_seduta']}"


def build_description(seduta_info: dict, video_info: dict, config: dict = None) -> str:
    """
    Costruisce descrizione video YouTube.

    Args:
        seduta_info: Dict con info seduta
        video_info: Dict con info video
        config: Dict configurazione (opzionale, per channel_id)

    Returns:
        Descrizione formattata
    """
    data_seduta_formattata = format_date_italian(seduta_info['data_seduta'])
    numero = seduta_info['numero_seduta']
    ora = video_info['ora_video']

    token = build_seduta_token(seduta_info)

    description_parts = [
        f"Seduta n. {numero} del {data_seduta_formattata}",
        f"Video dalle ore {ora}",
        "",
        "Assemblea Regionale Siciliana - XVIII Legislatura",
        ""
    ]

    if token:
        description_parts.append(f"{token}")
        description_parts.append("")

    # Link ricerca tutti video seduta (ricerca globale con operatori)
    if token:
        search_query = f"\"{token}\" intitle:\"Lavori d'aula\""
        search_url = f"https://www.youtube.com/results?search_query={quote(search_query)}"
        description_parts.append(f"🔍 Tutti i video seduta {numero}: {search_url}")
        description_parts.append("")

    # Aggiungi documenti se disponibili
    if seduta_info.get('odg_url') or seduta_info.get('resoconto_url'):
        description_parts.append("📄 Documenti:")

        if seduta_info.get('odg_url'):
            description_parts.append(f"- OdG e Comunicazioni: {seduta_info['odg_url']}")

        if seduta_info.get('resoconto_url'):
            description_parts.append(f"- Resoconto provvisorio: {seduta_info['resoconto_url']}")

        description_parts.append("")

    # Aggiungi link pagina ARS
    if seduta_info.get('url_pagina'):
        description_parts.append(f"🔗 Link alla seduta: {seduta_info['url_pagina']}")

    return "\n".join(description_parts)


def build_recording_date(video_info: dict, timezone: str = "Europe/Rome") -> str:
    """
    Costruisce recordingDate in formato ISO 8601.

    Formato: "2025-12-10T11:30:00Z"

    Args:
        video_info: Dict con info video

    Returns:
        Data/ora in formato ISO 8601
    """
    data = video_info['data_video']
    ora = video_info['ora_video']

    if not data or not ora:
        return None

    try:
        dt = datetime.fromisoformat(f"{data}T{ora}:00")
        dt = dt.replace(tzinfo=ZoneInfo(timezone))
        return dt.isoformat(timespec="seconds")
    except Exception:
        return None


def build_tags(seduta_info: dict, config: dict) -> list:
    """
    Costruisce lista tags per YouTube ottimizzati per ricerca seduta.

    Args:
        seduta_info: Dict con info seduta
        config: Dict configurazione con tags base

    Returns:
        Lista tags
    """
    # Tags base da config
    tags = config.get('youtube', {}).get('tags', []).copy()

    # Tag specifici seduta per ricerca
    if seduta_info.get('numero_seduta'):
        numero = seduta_info['numero_seduta']
        numero_base = numero.split('/')[0]

        # Tag numero completo e base
        tags.append(f"Seduta n. {numero}")  # Es: "Seduta n. 220" o "Seduta n. 219/A"
        if '/' in numero:
            tags.append(f"Seduta {numero_base}")  # Es: "Seduta 219" (senza suffisso)

    # Tag anno e mese
    if seduta_info.get('data_seduta'):
        anno = extract_year(seduta_info['data_seduta'])
        if anno:
            tags.append(anno)

        mese = extract_month_name(seduta_info['data_seduta'])
        if mese:
            tags.append(f"{mese} {anno}")  # Es: "Dicembre 2025"

    return tags


def build_youtube_metadata(seduta_info: dict, video_info: dict, config: dict) -> dict:
    """
    Costruisce tutti i metadati per upload YouTube.

    Args:
        seduta_info: Dict con info seduta
        video_info: Dict con info video
        config: Dict configurazione

    Returns:
        Dict con tutti i metadati YouTube
    """
    return {
        'title': build_title(seduta_info, video_info),
        'description': build_description(seduta_info, video_info, config),
        'tags': build_tags(seduta_info, config),
        'category': config.get('youtube', {}).get('category_id', '25'),
        'privacy': config.get('youtube', {}).get('privacy', 'public'),
        'recordingDate': build_recording_date(
            video_info,
            timezone=config.get('youtube', {}).get('timezone', 'Europe/Rome')
        ),
        'defaultLanguage': config.get('youtube', {}).get('default_language', 'it')
    }
