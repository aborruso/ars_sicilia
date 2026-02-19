#!/usr/bin/env python3
"""Scarica sottotitoli YouTube via API ufficiali in formato SRT."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

REPO_ROOT = Path(__file__).resolve().parents[1]
TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def load_oauth_credentials() -> Credentials:
    secrets_file = REPO_ROOT / "config" / "youtube_secrets.json"
    token_file = REPO_ROOT / "config" / "token.json"

    if not secrets_file.exists():
        raise RuntimeError(f"Missing secrets file: {secrets_file}")
    if not token_file.exists():
        raise RuntimeError(f"Missing token file: {token_file}")

    with secrets_file.open("r", encoding="utf-8") as f:
        secrets = json.load(f)
    with token_file.open("r", encoding="utf-8") as f:
        token_data = json.load(f)

    client_info = secrets.get("installed") or secrets.get("web") or {}
    client_id = client_info.get("client_id")
    client_secret = client_info.get("client_secret")
    refresh_token = token_data.get("refresh_token")

    if not client_id or not client_secret or not refresh_token:
        raise RuntimeError("Incomplete OAuth credentials in secrets/token files")

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=refresh_token,
        token_uri=TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )

    if not creds.valid:
        creds.refresh(Request())
        token_file.write_text(creds.to_json(), encoding="utf-8")

    return creds


def select_caption_id(items: list[dict], language: str) -> str | None:
    lang_matches = [item for item in items if item.get("snippet", {}).get("language") == language]
    if not lang_matches:
        return None

    # Prefer manually curated captions over ASR when both are available.
    lang_matches.sort(key=lambda item: item.get("snippet", {}).get("trackKind") == "asr")
    return lang_matches[0].get("id")


def download_caption(youtube_id: str, output_file: Path, language: str) -> int:
    creds = load_oauth_credentials()
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    captions_resp = youtube.captions().list(part="id,snippet", videoId=youtube_id).execute()
    items = captions_resp.get("items", [])
    caption_id = select_caption_id(items, language)
    if not caption_id:
        return 2

    payload = youtube.captions().download(id=caption_id, tfmt="srt").execute()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, bytes):
        output_file.write_bytes(payload)
    else:
        output_file.write_text(str(payload), encoding="utf-8")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Download YouTube caption track as SRT")
    parser.add_argument("--youtube-id", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--lang", default="it")
    args = parser.parse_args()

    try:
        return download_caption(args.youtube_id, Path(args.output_file), args.lang)
    except HttpError as exc:
        print(f"ERROR: YouTube API HTTP {exc.resp.status}: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
