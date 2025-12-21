"""Costruzione metadati YouTube."""

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
    data_formattata = format_date_italian(video_info['data_video'] or seduta_info['data_seduta'])
    numero = seduta_info['numero_seduta']
    ora = video_info['ora_video']

    return f"Lavori d'aula: seduta n. {numero} del {data_formattata} - {ora}"


def build_description(seduta_info: dict, video_info: dict) -> str:
    """
    Costruisce descrizione video YouTube.

    Args:
        seduta_info: Dict con info seduta
        video_info: Dict con info video

    Returns:
        Descrizione formattata
    """
    data_seduta_formattata = format_date_italian(seduta_info['data_seduta'])
    numero = seduta_info['numero_seduta']
    ora = video_info['ora_video']

    description_parts = [
        f"Seduta n. {numero} del {data_seduta_formattata}",
        f"Video dalle ore {ora}",
        "",
        "Assemblea Regionale Siciliana - XVIII Legislatura",
        ""
    ]

    # Aggiungi documenti se disponibili
    if seduta_info.get('odg_url') or seduta_info.get('resoconto_url'):
        description_parts.append("Documenti:")

        if seduta_info.get('odg_url'):
            description_parts.append(f"- OdG e Comunicazioni: {seduta_info['odg_url']}")

        if seduta_info.get('resoconto_url'):
            description_parts.append(f"- Resoconto provvisorio: {seduta_info['resoconto_url']}")

        description_parts.append("")

    # Aggiungi link pagina ARS
    if seduta_info.get('url_pagina'):
        description_parts.append(f"Link alla seduta: {seduta_info['url_pagina']}")

    return "\n".join(description_parts)


def build_recording_date(video_info: dict) -> str:
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

    return f"{data}T{ora}:00Z"


def build_tags(seduta_info: dict, config: dict) -> list:
    """
    Costruisce lista tags per YouTube.

    Args:
        seduta_info: Dict con info seduta
        config: Dict configurazione con tags base

    Returns:
        Lista tags
    """
    # Tags base da config
    tags = config.get('youtube', {}).get('tags', []).copy()

    # Tag numero seduta (solo numero, no suffisso)
    if seduta_info.get('numero_seduta'):
        numero_base = seduta_info['numero_seduta'].split('/')[0]
        tags.append(f"Seduta {numero_base}")

    # Tag anno
    if seduta_info.get('data_seduta'):
        anno = extract_year(seduta_info['data_seduta'])
        if anno:
            tags.append(anno)

        # Tag mese
        mese = extract_month_name(seduta_info['data_seduta'])
        if mese:
            tags.append(mese)

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
        'description': build_description(seduta_info, video_info),
        'tags': build_tags(seduta_info, config),
        'category': config.get('youtube', {}).get('category_id', '25'),
        'privacy': config.get('youtube', {}).get('privacy', 'public'),
        'recordingDate': build_recording_date(video_info),
        'defaultLanguage': config.get('youtube', {}).get('default_language', 'it')
    }
