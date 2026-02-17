#!/usr/bin/env python3
"""
Scraper incrementale per "Studi e Pubblicazioni" ARS (sezioni correnti).

Esclude deliberatamente la sezione Archivio.
Output: JSONL append-only (solo record nuovi in base alla URL del documento).
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://www.ars.sicilia.it"
HOME_URL = f"{BASE_URL}/studi-e-pubblicazioni"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "studi_pubblicazioni.jsonl"

USER_AGENT = "ars-sicilia-studi-scraper/1.0 (+https://github.com/aborruso/ars_sicilia)"

DOWNLOAD_MONTH_RE = re.compile(r"/downloads/(\d{4})-(\d{2})/", re.IGNORECASE)
DDL_CONTEXT_RE = re.compile(
    r"(?is)\b(?:ddl|disegno\s+di\s+legge)\b(?:\s*(?:nn?|n)\.?)?\s*([^\n.;:()\"]{1,140})"
)
DDL_TOKEN_RE = re.compile(
    r"\b\d{1,4}(?:\s*/\s*[A-Za-z])?(?:\s*(?:bis|ter|quater|quinquies))?(?:\s*[A-Za-z])?\b",
    re.IGNORECASE,
)


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def get_soup(session: requests.Session, url: str, timeout: int) -> BeautifulSoup:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def extract_category_links(home_soup: BeautifulSoup) -> list[tuple[str, str]]:
    categories: list[tuple[str, str]] = []
    seen_urls: set[str] = set()

    for anchor in home_soup.select("ul.smenu_left a[href]"):
        label = normalize_space(anchor.get_text(" ", strip=True))
        if not label:
            continue

        href = urljoin(BASE_URL, anchor["href"])
        is_archive = "archivio" in label.lower() or href.rstrip("/").endswith(
            "/studi-e-pubblicazioni-archivio"
        )
        if is_archive:
            continue

        if href in seen_urls:
            continue

        seen_urls.add(href)
        categories.append((label, href))

    return categories


def infer_data_pubblicazione_from_url(document_url: str) -> str | None:
    match = DOWNLOAD_MONTH_RE.search(document_url)
    if not match:
        return None
    return f"{match.group(1)}-{match.group(2)}"


def extract_ddl_numbers(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    for context_match in DDL_CONTEXT_RE.finditer(text):
        context = normalize_space(context_match.group(1))
        for token in DDL_TOKEN_RE.findall(context):
            normalized = normalize_space(token).upper()
            normalized = re.sub(r"\s*/\s*", "/", normalized)
            normalized = re.sub(r"\s+", " ", normalized)
            normalized = re.sub(r"^(\d{1,4})\s+([A-Z])$", r"\1\2", normalized)

            base_match = re.match(r"^(\d{1,4})", normalized)
            if not base_match:
                continue
            base_number = int(base_match.group(1))

            # Riduce falsi positivi (date, codici interni, numerazioni non DDL).
            if base_number <= 9:
                continue
            if re.match(r"^\d+[A-Z]$", normalized) and normalized[-1] not in {"A", "B"}:
                continue
            if re.match(r"^\d+/[A-Z]$", normalized) and normalized[-1] not in {"A", "B"}:
                continue

            if normalized.isdigit():
                if 1900 <= base_number <= 2100:
                    continue

            if normalized and normalized not in seen:
                seen.add(normalized)
                found.append(normalized)

    return found


def extract_records_for_category(
    category_name: str,
    category_url: str,
    category_soup: BeautifulSoup,
    run_timestamp: str,
) -> list[dict]:
    records: list[dict] = []

    for item in category_soup.select("div.views-element-container div.pad-blocco-discorsi ul > li"):
        title_el = item.select_one("div.blocco-discorsi-2 p")
        link_el = item.select_one("div.blocco-discorsi-3 a[href]")
        if not title_el or not link_el:
            continue

        title = normalize_space(title_el.get_text(" ", strip=True))
        if not title:
            continue

        descriptor_el = item.select_one("div.blocco-discorsi-1 p")
        descriptor = (
            normalize_space(descriptor_el.get_text(" ", strip=True)) if descriptor_el else None
        )

        document_url = urljoin(BASE_URL, link_el["href"])
        ddl_numbers = extract_ddl_numbers(f"{descriptor or ''} {title}")

        record = {
            "titolo": title,
            "url": document_url,
            "data_pubblicazione": infer_data_pubblicazione_from_url(document_url),
            "numeri_ddl_estratti": ddl_numbers,
            "fonte": category_url,
            "sezione": category_name,
            "timestamp_raccolta_utc": run_timestamp,
        }
        if descriptor:
            record["descrittore_documento"] = descriptor

        records.append(record)

    return records


def merge_records_by_url(records: Iterable[dict]) -> list[dict]:
    by_url: dict[str, dict] = {}

    for record in records:
        key = record["url"]
        if key not in by_url:
            seed = dict(record)
            seed["sezioni"] = [record["sezione"]]
            by_url[key] = seed
            continue

        existing = by_url[key]
        if record["sezione"] not in existing["sezioni"]:
            existing["sezioni"].append(record["sezione"])

        for ddl in record.get("numeri_ddl_estratti", []):
            if ddl not in existing["numeri_ddl_estratti"]:
                existing["numeri_ddl_estratti"].append(ddl)

        if len(record["titolo"]) > len(existing["titolo"]):
            existing["titolo"] = record["titolo"]

    merged = list(by_url.values())
    for item in merged:
        item["sezioni"] = sorted(item["sezioni"])

    return merged


def load_existing_urls(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()

    seen_urls: set[str] = set()
    with output_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            url = payload.get("url")
            if isinstance(url, str) and url:
                seen_urls.add(url)
    return seen_urls


def write_jsonl(records: list[dict], output_path: Path, mode: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_mode = "w" if mode == "snapshot" else "a"
    with output_path.open(file_mode, encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape ARS Studi e Pubblicazioni (sezioni correnti, archivio escluso)."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Path output JSONL (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--mode",
        choices=("append", "snapshot"),
        default="append",
        help="append: aggiunge solo nuovi URL; snapshot: sovrascrive con lo stato corrente",
    )
    parser.add_argument("--timeout", type=int, default=30, help="Timeout HTTP in secondi")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    home_soup = get_soup(session, HOME_URL, args.timeout)
    categories = extract_category_links(home_soup)
    if not categories:
        print("Nessuna categoria trovata nella pagina Studi e Pubblicazioni.")
        return 1

    print(f"Categorie trovate (archivio escluso): {len(categories)}")

    all_records: list[dict] = []
    for category_name, category_url in categories:
        try:
            category_soup = get_soup(session, category_url, args.timeout)
            records = extract_records_for_category(category_name, category_url, category_soup, run_ts)
            print(f"- {category_name}: {len(records)} record")
            all_records.extend(records)
        except requests.RequestException as exc:
            print(f"- {category_name}: errore download ({exc})")
            continue

    merged_records = merge_records_by_url(all_records)
    print(f"Record totali estratti: {len(all_records)}")
    print(f"Record unici per URL: {len(merged_records)}")

    if args.mode == "snapshot":
        ordered = sorted(merged_records, key=lambda r: r["url"])
        write_jsonl(ordered, args.output, mode="snapshot")
        print(f"Snapshot scritto in {args.output} ({len(ordered)} record).")
        return 0

    existing_urls = load_existing_urls(args.output)
    new_records = [record for record in merged_records if record["url"] not in existing_urls]
    write_jsonl(new_records, args.output, mode="append")
    print(f"Record già presenti: {len(existing_urls)}")
    print(f"Nuovi record aggiunti: {len(new_records)}")
    print(f"Output aggiornato: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
