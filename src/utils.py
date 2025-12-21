"""Utility functions per il progetto ARS YouTube uploader."""

from datetime import datetime
import re


def format_date_italian(date_str: str) -> str:
    """
    Converte data YYYY-MM-DD in formato italiano "DD Mese YYYY".

    Args:
        date_str: Data in formato YYYY-MM-DD

    Returns:
        Data in formato "10 Dicembre 2025"
    """
    months_it = {
        '01': 'Gennaio', '02': 'Febbraio', '03': 'Marzo', '04': 'Aprile',
        '05': 'Maggio', '06': 'Giugno', '07': 'Luglio', '08': 'Agosto',
        '09': 'Settembre', '10': 'Ottobre', '11': 'Novembre', '12': 'Dicembre'
    }

    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return date_str

        year, month, day = parts
        day = day.lstrip('0')  # Rimuovi zero iniziale
        month_name = months_it.get(month, month)

        return f"{day} {month_name} {year}"
    except Exception:
        return date_str


def parse_italian_date(italian_date: str) -> str:
    """
    Converte data italiana "10 Dicembre 2025" in formato YYYY-MM-DD.

    Args:
        italian_date: Data in formato "10 Dicembre 2025"

    Returns:
        Data in formato YYYY-MM-DD
    """
    months_it_reverse = {
        'gennaio': '01', 'febbraio': '02', 'marzo': '03', 'aprile': '04',
        'maggio': '05', 'giugno': '06', 'luglio': '07', 'agosto': '08',
        'settembre': '09', 'ottobre': '10', 'novembre': '11', 'dicembre': '12'
    }

    try:
        # Pattern: "10 Dicembre 2025" o "10 DICEMBRE 2025"
        match = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})', italian_date, re.IGNORECASE)
        if not match:
            return italian_date

        day, month_name, year = match.groups()
        month = months_it_reverse.get(month_name.lower())

        if not month:
            return italian_date

        day = day.zfill(2)  # Aggiungi zero iniziale se manca
        return f"{year}-{month}-{day}"
    except Exception:
        return italian_date


def extract_year(date_str: str) -> str:
    """
    Estrae l'anno da una data YYYY-MM-DD.

    Args:
        date_str: Data in formato YYYY-MM-DD

    Returns:
        Anno come stringa (es. "2025")
    """
    try:
        return date_str.split('-')[0]
    except Exception:
        return ""


def extract_month_name(date_str: str) -> str:
    """
    Estrae il nome del mese da una data YYYY-MM-DD.

    Args:
        date_str: Data in formato YYYY-MM-DD

    Returns:
        Nome mese in italiano (es. "Dicembre")
    """
    months_it = {
        '01': 'Gennaio', '02': 'Febbraio', '03': 'Marzo', '04': 'Aprile',
        '05': 'Maggio', '06': 'Giugno', '07': 'Luglio', '08': 'Agosto',
        '09': 'Settembre', '10': 'Ottobre', '11': 'Novembre', '12': 'Dicembre'
    }

    try:
        month = date_str.split('-')[1]
        return months_it.get(month, "")
    except Exception:
        return ""


def sanitize_filename(filename: str) -> str:
    """
    Rimuove caratteri non validi da un filename.

    Args:
        filename: Nome file originale

    Returns:
        Nome file sanitizzato
    """
    # Rimuovi caratteri non validi per filesystem
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    return filename


def parse_time_from_text(text: str) -> str | None:
    """
    Estrae orario da testo tipo "Video dalle 11:30".

    Args:
        text: Testo contenente orario

    Returns:
        Orario in formato HH:MM o None
    """
    match = re.search(r'(\d{1,2}):(\d{2})', text)
    if match:
        hour = match.group(1).zfill(2)
        minute = match.group(2)
        return f"{hour}:{minute}"
    return None
