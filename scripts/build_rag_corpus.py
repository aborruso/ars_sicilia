#!/usr/bin/env python3
"""Genera il corpus Markdown per Cloudflare AI Search dalle trascrizioni SRT.

Per ogni video selezionato produce `{youtube_id}.md` con:
- header di metadati (seduta, data, youtube_id, URL pagina video);
- trascrizione in paragrafi aggregati (~PARAGRAPH_SECONDS) con marker [HH:MM:SS]
  usato dal frontend per il deep-link al secondo.

Uso:
  python3 scripts/build_rag_corpus.py                 # 10 video più recenti → data/rag_corpus/
  python3 scripts/build_rag_corpus.py --limit 0       # tutti i video con SRT
  python3 scripts/build_rag_corpus.py --output tmp/x --variant ownline --limit 3
"""

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANAGRAFICA = REPO_ROOT / "data" / "anagrafica_video.csv"
TRASCRIZIONI_DIR = REPO_ROOT / "data" / "trascrizioni"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "rag_corpus"

SITE_BASE = "https://aborruso.github.io/ars_sicilia"
PARAGRAPH_SECONDS = 60

MESI = [
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
]

TIMESTAMP_RE = re.compile(
    r"(\d{2}):(\d{2}):(\d{2}),\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}"
)


def parse_srt(path: Path):
    """Restituisce lista di cue (start_seconds, text)."""
    cues = []
    start = None
    text_lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        m = TIMESTAMP_RE.match(line)
        if m:
            start = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            text_lines = []
        elif not line:
            if start is not None and text_lines:
                cues.append((start, " ".join(text_lines)))
            start = None
            text_lines = []
        elif not line.isdigit() or start is not None:
            if start is not None:
                text_lines.append(line)
    if start is not None and text_lines:
        cues.append((start, " ".join(text_lines)))
    return cues


def to_hms(seconds: int) -> str:
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def build_paragraphs(cues, window=PARAGRAPH_SECONDS):
    """Aggrega i cue in paragrafi da ~window secondi: [(start, testo), ...]."""
    paragraphs = []
    current_start = None
    current_text = []
    for start, text in cues:
        if current_start is None:
            current_start = start
        if start - current_start >= window and current_text:
            paragraphs.append((current_start, " ".join(current_text)))
            current_start = start
            current_text = []
        current_text.append(text)
    if current_text:
        paragraphs.append((current_start, " ".join(current_text)))
    return paragraphs


def data_italiana(iso_date: str) -> str:
    y, m, d = iso_date.split("-")
    return f"{int(d)} {MESI[int(m) - 1]} {y}"


def video_page_url(row) -> str:
    y, m, d = row["data_seduta"].split("-")
    ora = row["ora_video"].replace(":", "")
    return f"{SITE_BASE}/sedute/{y}/{m}/{d}/seduta-{row['numero_seduta']}/video-{ora}/"


def render_markdown(row, paragraphs, variant: str) -> str:
    numero = row["numero_seduta"]
    data_it = data_italiana(row["data_seduta"])
    lines = [
        f"# Assemblea Regionale Siciliana — seduta n. {numero} del {data_it} (video delle ore {row['ora_video']})",
        "",
        f"- Seduta: {numero}",
        f"- Data: {row['data_seduta']}",
        f"- Video YouTube: {row['youtube_id']}",
        f"- Pagina video: {video_page_url(row)}",
        "- Fonte: trascrizione automatica dei sottotitoli YouTube",
        "",
        "## Trascrizione",
        "",
    ]
    for start, text in paragraphs:
        marker = f"[{to_hms(start)}]"
        if variant == "ownline":
            lines.append(marker)
            lines.append("")
            lines.append(text)
        else:
            lines.append(f"{marker} {text}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=10, help="quanti video (0 = tutti)")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--variant", choices=["inline", "ownline"], default="inline")
    args = ap.parse_args()

    with ANAGRAFICA.open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("youtube_id")]

    rows = [r for r in rows if (TRASCRIZIONI_DIR / f"{r['youtube_id']}.it.srt").exists()]
    rows.sort(key=lambda r: (r["data_seduta"], r["ora_video"]), reverse=True)
    if args.limit:
        rows = rows[: args.limit]

    if not rows:
        sys.exit("Nessun video con SRT trovato.")

    args.output.mkdir(parents=True, exist_ok=True)
    for row in rows:
        srt = TRASCRIZIONI_DIR / f"{row['youtube_id']}.it.srt"
        cues = parse_srt(srt)
        paragraphs = build_paragraphs(cues)
        md = render_markdown(row, paragraphs, args.variant)
        out = args.output.resolve() / f"{row['youtube_id']}.md"
        out.write_text(md, encoding="utf-8")
        print(f"✓ {out.name} — seduta {row['numero_seduta']} "
              f"{row['data_seduta']}, {len(paragraphs)} paragrafi")

    print(f"\n{len(rows)} file in {args.output}")


if __name__ == "__main__":
    main()
