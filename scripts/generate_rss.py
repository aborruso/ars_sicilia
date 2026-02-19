#!/usr/bin/env python3
"""Generate RSS feed for latest uploaded videos."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import csv
import json
from datetime import datetime
from email.utils import format_datetime
from zoneinfo import ZoneInfo
from xml.etree.ElementTree import Element, SubElement, ElementTree

import yaml

from src.metadata import build_title

REPO_ROOT = Path(__file__).resolve().parents[1]

def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def parse_datetime(date_str: str | None, time_str: str | None, tz_name: str) -> datetime | None:
    if not date_str:
        return None
    time_part = time_str or '00:00'
    try:
        dt = datetime.fromisoformat(f"{date_str}T{time_part}:00")
        return dt.replace(tzinfo=ZoneInfo(tz_name))
    except Exception:
        return None


def has_valid_digest(youtube_id: str | None, digest_dir: Path) -> bool:
    if not youtube_id:
        return False
    digest_file = digest_dir / f"{youtube_id}.json"
    if not digest_file.exists():
        return False
    try:
        with digest_file.open('r', encoding='utf-8') as f:
            payload = json.load(f)
        digest_text = payload.get('digest')
        return isinstance(digest_text, str) and len(digest_text.strip()) > 0
    except Exception:
        return False


def build_rss(base_url: str, rows: list[dict], tz_name: str, limit: int, digest_dir: Path) -> Element:
    rss = Element('rss', version='2.0')
    channel = SubElement(rss, 'channel')

    SubElement(channel, 'title').text = 'ARS Sicilia - Ultimi video'
    SubElement(channel, 'link').text = f"{base_url}/feed.xml"
    SubElement(channel, 'description').text = 'Ultimi video caricati delle sedute ARS.'
    SubElement(channel, 'language').text = 'it-it'

    items = []
    for row in rows:
        youtube_id = row.get('youtube_id')
        if not youtube_id or not has_valid_digest(youtube_id, digest_dir):
            continue
        dt = parse_datetime(row.get('data_video'), row.get('ora_video'), tz_name)
        items.append((dt, row))

    items = [item for item in items if item[0] is not None]
    items.sort(key=lambda x: x[0], reverse=True)

    for dt, row in items[:limit]:
        seduta_info = {
            'numero_seduta': row.get('numero_seduta'),
            'data_seduta': row.get('data_seduta'),
            'url_pagina': row.get('url_pagina'),
            'odg_url': row.get('odg_url'),
            'resoconto_url': row.get('resoconto_url')
        }
        video_info = {
            'id_video': row.get('id_video'),
            'ora_video': row.get('ora_video'),
            'data_video': row.get('data_video'),
            'video_page_url': row.get('video_page_url')
        }

        title = build_title(seduta_info, video_info)
        youtube_id = row.get('youtube_id')
        link = f"https://www.youtube.com/watch?v={youtube_id}"

        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = title
        SubElement(item, 'link').text = link
        SubElement(item, 'guid').text = youtube_id
        SubElement(item, 'pubDate').text = format_datetime(dt)
        SubElement(item, 'description').text = f"Seduta n. {seduta_info['numero_seduta']} del {seduta_info['data_seduta']}"

    return rss


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate RSS feed for latest videos')
    parser.add_argument('--config', default=str(REPO_ROOT / 'config' / 'config.yaml'))
    parser.add_argument('--anagrafica', default=str(REPO_ROOT / 'data' / 'anagrafica_video.csv'))
    parser.add_argument('--digest-dir', default=str(REPO_ROOT / 'data' / 'digest'))
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--output', default='feed.xml')
    args = parser.parse_args()

    config = load_config(args.config)
    tz_name = config.get('youtube', {}).get('timezone', 'Europe/Rome')

    rows = []
    with open(args.anagrafica, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    rss = build_rss(args.base_url, rows, tz_name, args.limit, Path(args.digest_dir))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree = ElementTree(rss)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
