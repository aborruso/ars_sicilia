#!/usr/bin/env python3
"""Rigenera il token OAuth del progetto captions con gli scope corretti.

Apre un server locale per il consenso nel browser e salva config/token.json
con un refresh_token valido. Da usare quando il refresh_token e' scaduto o
quando cambiano gli scope.

Scope: youtube.readonly + youtube.force-ssl (necessari per captions.download).
"""

from __future__ import annotations

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

REPO_ROOT = Path(__file__).resolve().parents[1]
SECRETS_FILE = REPO_ROOT / "config" / "youtube_secrets.json"
TOKEN_FILE = REPO_ROOT / "config" / "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def main() -> int:
    if not SECRETS_FILE.exists():
        raise SystemExit(f"Missing secrets file: {SECRETS_FILE}")

    flow = InstalledAppFlow.from_client_secrets_file(str(SECRETS_FILE), SCOPES)

    # access_type=offline + prompt=consent forzano il rilascio del refresh_token.
    creds = flow.run_local_server(
        port=8080,
        access_type="offline",
        prompt="consent",
        open_browser=True,
    )

    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    print(f"\nToken salvato in: {TOKEN_FILE}")
    print(f"refresh_token presente: {bool(creds.refresh_token)}")
    print(f"scopes: {creds.scopes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
