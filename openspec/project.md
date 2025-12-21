# Project Context

## Purpose
Automate the collection and publication of Assemblea Regionale Siciliana (ARS) plenary videos: crawl seduta pages, catalog metadata, download streams, and upload to YouTube with searchable titles, descriptions, tags, and recording dates. Maintain a public CSV log to avoid duplicate uploads and enable auditing.

## Tech Stack
- Python 3.10+
- Virtual environment: `.venv` (managed via `python3 -m venv`)
- Core libraries: `requests`, `beautifulsoup4`, `yt-dlp`, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`, `pyyaml`
- Data/config: YAML config file (`config/config.yaml`), CSV logs/indices under `data/`
- Bash wrapper (`scripts/run_daily.sh`) for cron with lock handling
- GitHub Actions workflows for daily upload and RSS publish (`.github/workflows/*.yml`)
- Package dependencies: `yt-dlp>=2024.0.0`, `google-api-python-client>=2.0.0`, `google-auth-oauthlib>=1.0.0`, `google-auth-httplib2>=0.1.0`, `beautifulsoup4>=4.12.0`, `requests>=2.31.0`, `pyyaml>=6.0`

## Project Conventions

### Code Style
- PEP 8 with type hints; functions are snake_case and documented with concise Italian docstrings.
- Prefer `pathlib.Path` for filesystem paths; UTF-8 for file I/O.
- Print-based progress logging in CLI scripts; CSV logs for durable history (`data/logs/upload_log.csv`, `index.csv`).
- Keep secrets out of git (`config/youtube_secrets.json`, `config/token.json`, `.env` are ignored).
- Project documentation: `README.md` (user guide), `PRD.md` (requirements), `LOG.md` (change log), `docs/` (additional docs).

### Architecture Patterns
- Modular pipeline: `scraper` (HTML fetch/parse) → `metadata` (title/description/tags) → `downloader` (yt-dlp HLS) → `uploader` (YouTube Data API) → `logger` (CSV log/index).
- Script entrypoints live under `scripts/` (e.g., `scripts/main.py`, `scripts/build_anagrafica.py`, `scripts/run_daily.sh`).
- RSS feed generation via `scripts/generate_rss.py`, published by GitHub Actions.
- Configuration-driven behavior via `config/config.yaml`; defaults target seduta 219 (10/12/2025) onward.
- Idempotency: skip uploads already logged as `success`; incremental crawler (`build_anagrafica.py`) updates `data/anagrafica_video.csv` and stops when no future sedute.
- Shell automation (`run_daily.sh`) uses `set -euo pipefail` and lock file to prevent concurrent runs.

### Testing Strategy
- Manual smoke scripts: `scripts/test_youtube_auth.py` / `scripts/test_youtube_auth_manual.py` to validate OAuth tokens and quota.
- Single-upload smoke test: `scripts/upload_single.py` to validate the end-to-end flow on one video.
- OAuth helper scripts: `scripts/get_auth_url.py` / `scripts/complete_auth.py` for manual authentication flow.
- Functional verification by running `scripts/build_anagrafica.py` (catalog only) and `scripts/main.py [seduta_url]` for end-to-end upload.
- No automated CI/unit tests yet; rely on log outputs and quota checks for success/failure signals.
- GitHub Actions runs daily: uploads (up to 4 videos/day, based on `data/anagrafica_video.csv`) and RSS publish to `gh-pages`.

### Git Workflow
- No formal workflow documented; default to feature branches merged into `main` via PRs.
- Commit small, reviewable changes; keep operational scripts executable (`chmod +x run_daily.sh`).
- Never commit OAuth secrets or tokens; verify `.gitignore` before pushing.

## Domain Context
- Source site: https://www.ars.sicilia.it; seduta pages under `/agenda/sedute-aula/` with `video_box` entries containing `data-src` links to per-video pages.
- Seduta numbering includes suffixes (e.g., `219/A`); dates are Italian text (`10 Dicembre 2025`) parsed to `YYYY-MM-DD`.
- YouTube metadata pattern: title `Lavori d'aula: seduta n. {numero} del {data} - {ora}`; description includes OdG/Resoconto links and seduta URL; tags add base list + seduta number/year/month.
- Recording date uses video date/time (`YYYY-MM-DDTHH:MM:00Z`) when available; falls back to seduta date for titles/descriptions.

## Important Constraints
- YouTube Data API quota 10,000 units/day; upload costs ~1,600 units ⇒ max ~6 uploads/day unless quota increased.
- Daily automation further caps uploads at 4/day in the GitHub Actions workflow.
- Channel must be verified for videos >15 minutes; OAuth desktop credentials required locally.
- Network timeouts: scraping 30s, download up to 1h per video; retries configurable.
- Storage/bandwidth: ~1 GB per hour of 720p video; temp files cleaned post-upload when `cleanup_after_upload=true`.
- Privacy setting configurable (default `public`); ensure compliance with ARS content rights.

## External Dependencies
- ARS website (`ars.sicilia.it`) for HTML pages, OdG PDFs, resoconti, and video page links.
- YouTube Data API v3 for authentication, upload, and channel/quota info.
- Google OAuth 2.0 desktop client secrets (`config/youtube_secrets.json`) and token cache (`config/token.json`).
- `yt-dlp` binary for downloading HLS streams from ARS video pages.
- GitHub Pages for hosting the public RSS feed (`public/feed.xml`, published from `gh-pages`).
