"""Scraper per pagine sedute ARS."""

import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
from .utils import parse_italian_date, parse_time_from_text


def get_seduta_page(seduta_url: str, user_agent: str = "ARS-YouTube-Bot/1.0") -> BeautifulSoup:
    """
    Scarica HTML pagina seduta.

    Args:
        seduta_url: URL della pagina seduta
        user_agent: User agent per la richiesta HTTP

    Returns:
        BeautifulSoup object con HTML parsato

    Raises:
        requests.RequestException: Se download fallisce
    """
    headers = {'User-Agent': user_agent}
    response = requests.get(seduta_url, headers=headers, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')


def extract_seduta_number(html: BeautifulSoup) -> Optional[str]:
    """
    Estrae numero seduta dalla pagina.

    Args:
        html: BeautifulSoup object

    Returns:
        Numero seduta (es. "219/A") o None
    """
    # Cerca prima nel title (più affidabile)
    title = html.find('title')
    if title:
        title_text = title.get_text()
        match = re.search(r'Seduta numero\s+(\d+/?\w*)', title_text, re.IGNORECASE)
        if match:
            return match.group(1)

    # Fallback: cerca nel h1 o span principale
    main_heading = html.find('h1')
    if main_heading:
        match = re.search(r'Seduta\s+(?:numero|n\.)\s+(\d+/?\w*)', main_heading.get_text(), re.IGNORECASE)
        if match:
            return match.group(1)

    # Ultimo fallback: cerca in tutto il testo
    text = html.get_text()
    match = re.search(r'Seduta numero\s+(\d+/?\w*)', text, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def extract_seduta_date(html: BeautifulSoup) -> Optional[str]:
    """
    Estrae data seduta dalla pagina in formato YYYY-MM-DD.

    Args:
        html: BeautifulSoup object

    Returns:
        Data seduta (es. "2025-12-10") o None
    """
    # Cerca pattern "DEL 10 DICEMBRE 2025"
    text = html.get_text()
    match = re.search(r'DEL\s+(\d{1,2}\s+\w+\s+\d{4})', text, re.IGNORECASE)
    if match:
        italian_date = match.group(1)
        return parse_italian_date(italian_date)
    return None


def extract_document_urls(html: BeautifulSoup) -> dict:
    """
    Estrae URL documenti OdG e Resoconto.

    Args:
        html: BeautifulSoup object

    Returns:
        Dict con chiavi 'odg_url' e 'resoconto_url'
    """
    result = {
        'odg_url': None,
        'resoconto_url': None
    }

    # Trova tutti i link
    for link in html.find_all('a', href=True):
        href = link['href']

        # OdG e Comunicazioni
        if 'ODG_PDF' in href or 'ODG' in href:
            result['odg_url'] = href if href.startswith('http') else f"https://www.ars.sicilia.it{href}"

        # Resoconto
        if 'ResSteno' in href or 'Resoconto' in link.get_text():
            result['resoconto_url'] = href if href.startswith('http') else f"https://www.ars.sicilia.it{href}"

    return result


def find_video_elements(html: BeautifulSoup) -> list:
    """
    Trova tutti gli elementi video nella pagina.

    Args:
        html: BeautifulSoup object

    Returns:
        Lista di elementi video (tag BeautifulSoup)
    """
    # Cerca div con data-src e classe video_box
    return html.find_all('div', class_='video_box', attrs={'data-src': True})


def extract_video_metadata(video_element, current_date_heading: str = None) -> Optional[dict]:
    """
    Estrae metadati da un elemento video.

    Args:
        video_element: Tag BeautifulSoup dell'elemento video
        current_date_heading: Data corrente dal heading (fallback se title non disponibile)

    Returns:
        Dict con metadati video o None
    """
    try:
        # Estrai data-src (contiene URL pagina video)
        video_page_url = video_element.get('data-src')
        if not video_page_url:
            return None

        # Estrai ID video dall'URL (es. 2484769)
        match = re.search(r'/video/(\d+)', video_page_url)
        if not match:
            return None
        id_video = match.group(1)

        # Prova a estrarre data e ora dal title attribute (più affidabile)
        # Formato: "16 Dicembre 2025 - Video dalle 11:37"
        title_attr = video_element.get('title', '')
        data_video = None
        ora_video = None

        if title_attr:
            # Estrai data dal title
            date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', title_attr)
            if date_match:
                data_video = parse_italian_date(date_match.group(1))

            # Estrai ora dal title
            ora_video = parse_time_from_text(title_attr)

        # Fallback: usa heading corrente e testo elemento
        if not data_video and current_date_heading:
            data_video = parse_italian_date(current_date_heading)

        if not ora_video:
            text = video_element.get_text().strip()
            ora_video = parse_time_from_text(text)

        if not ora_video:
            return None

        # Stream URL (costruito da ID video)
        stream_url = build_video_stream_url(id_video, data_video, ora_video)

        return {
            'id_video': id_video,
            'ora_video': ora_video,
            'data_video': data_video,
            'stream_url': stream_url,
            'video_page_url': video_page_url if video_page_url.startswith('http') else f"https://www.ars.sicilia.it{video_page_url}"
        }
    except Exception as e:
        print(f"Errore estrazione video: {e}")
        return None


def build_video_stream_url(video_id: str, date_str: str = None, time_str: str = None) -> Optional[str]:
    """
    Costruisce URL stream HLS da ID video.

    URL pattern noto: https://www.ars.sicilia.it/stream/vodsed/__definst__/18/18.219.YYYYMMDD.HHMMSS.mp4/playlist.m3u8

    NOTA: Il pattern esatto potrebbe richiedere reverse engineering dal player video.
    Per ora ritorna None, da implementare dopo test.

    Args:
        video_id: ID video ARS
        date_str: Data in formato YYYY-MM-DD
        time_str: Ora in formato HH:MM

    Returns:
        URL stream m3u8 o None
    """
    # TODO: Implementare dopo reverse engineering del player
    # Per ora ritorniamo None e usiamo video_page_url per estrarre l'URL reale
    return None


def get_next_seduta_url(html: BeautifulSoup, current_number: str = None, go_forward: bool = False) -> Optional[str]:
    """
    Trova URL seduta successiva usando il div.next_link (se go_forward=True) o qualsiasi link.

    Args:
        html: BeautifulSoup object
        current_number: Numero seduta corrente (non usato, mantenuto per compatibilità)
        go_forward: Se True, cerca nel div.next_link (freccia destra), altrimenti primo link

    Returns:
        URL seduta successiva o None
    """
    # Se go_forward, cerca nel div.next_link (freccia destra verso seduta futura)
    if go_forward:
        next_div = html.find('div', class_='next_link')
        if next_div:
            link = next_div.find('a', href=True)
            if link:
                href = link['href']
                return href if href.startswith('http') else f"https://www.ars.sicilia.it{href}"
        return None  # Nessuna seduta futura

    # Logica originale: cerca qualsiasi seduta (cronologicamente precedente)
    for link in html.find_all('a', href=True):
        href = link['href']
        if 'seduta-numero-' in href:
            return href if href.startswith('http') else f"https://www.ars.sicilia.it{href}"

    return None


def extract_seduta_info(html: BeautifulSoup, seduta_url: str) -> dict:
    """
    Estrae tutte le informazioni da una pagina seduta.

    Args:
        html: BeautifulSoup object
        seduta_url: URL della pagina seduta

    Returns:
        Dict con tutte le informazioni seduta
    """
    seduta_number = extract_seduta_number(html)
    seduta_date = extract_seduta_date(html)
    documents = extract_document_urls(html)

    # Estrai video
    videos = []
    video_elements = find_video_elements(html)

    # Processa ogni elemento video trovando la data dall'h4 precedente
    for video_el in video_elements:
        # Trova l'heading h4 con data più vicino che precede questo video
        video_date = None
        previous_h4_list = video_el.find_all_previous('h4')

        # Cerca il primo h4 (più vicino) con pattern data italiana
        for h4 in previous_h4_list:
            h4_text = h4.get_text().strip()
            if re.match(r'\d{1,2}\s+\w+\s+\d{4}', h4_text):
                video_date = parse_italian_date(h4_text)
                break

        # Se non trovato, usa data seduta come fallback
        if not video_date:
            video_date = seduta_date

        video_data = extract_video_metadata(video_el, video_date)
        if video_data:
            video_data['numero_seduta'] = seduta_number
            video_data['data_seduta'] = seduta_date
            videos.append(video_data)

    return {
        'numero_seduta': seduta_number,
        'data_seduta': seduta_date,
        'url_pagina': seduta_url,
        'odg_url': documents['odg_url'],
        'resoconto_url': documents['resoconto_url'],
        'videos': videos
    }


def crawl_sedute(start_url: str, max_sedute: int = None) -> list:
    """
    Crawl sedute a partire da un URL.

    Args:
        start_url: URL prima seduta
        max_sedute: Numero massimo sedute da crawlare (None = infinite)

    Yields:
        Dict con info seduta
    """
    current_url = start_url
    count = 0

    while current_url and (max_sedute is None or count < max_sedute):
        try:
            print(f"Crawling: {current_url}")
            html = get_seduta_page(current_url)
            seduta_info = extract_seduta_info(html, current_url)

            yield seduta_info

            # Trova seduta successiva
            current_url = get_next_seduta_url(html)
            count += 1

        except Exception as e:
            print(f"Errore crawling {current_url}: {e}")
            break
