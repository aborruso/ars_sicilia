# Project Context

## Purpose
Automate the collection and publication of Assemblea Regionale Siciliana (ARS) plenary videos: crawl seduta pages, catalog metadata, download streams, and upload to YouTube with searchable titles, descriptions, tags, and recording dates. Maintain a public CSV log to avoid duplicate uploads and enable auditing. Extract structured legislative bill data from agenda PDFs (OdG) for historical archiving and linkage to videos. Generate AI-powered video digests from transcripts and track video duration for analytics. Provide a public static website to browse, search, and navigate sedute videos with enhanced accessibility and user experience features.

## Tech Stack

### Backend Pipeline
- Python 3.10+
- Virtual environment: `.venv` (managed via `python3 -m venv`)
- Core libraries: `requests`, `beautifulsoup4`, `yt-dlp`, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`, `pyyaml`
- Data/config: YAML config file (`config/config.yaml`), CSV logs/indices under `data/`
- Bash wrapper (`scripts/run_daily.sh`) for cron with lock handling
- Package dependencies: `yt-dlp>=2024.0.0`, `google-api-python-client>=2.0.0`, `google-auth-oauthlib>=1.0.0`, `google-auth-httplib2>=0.1.0`, `beautifulsoup4>=4.12.0`, `requests>=2.31.0`, `pyyaml>=6.0`
- CLI tools: `markitdown` (PDF to text conversion), `llm` (LLM-based structured extraction), `mlr` (miller, JSONL/CSV processing), `qv` (yt-dlp wrapper for transcript download)

### Frontend Website
- Astro 5.0+ (static site generator)
- Tailwind CSS 3.4+ with Typography plugin for content styling
- TypeScript for type safety
- Build-time data processing: `scripts/build-data.mjs` converts CSV/JSONL/JSON to static JSON bundles
- Static hosting: GitHub Pages
- Integrations: `@astrojs/tailwind`, `@astrojs/sitemap`, `@astrojs/rss`
- GitHub Actions workflows for automated deployment

## Project Conventions

### Code Style
- PEP 8 with type hints; functions are snake_case and documented with concise Italian docstrings.
- Prefer `pathlib.Path` for filesystem paths; UTF-8 for file I/O.
- Print-based progress logging in CLI scripts; CSV logs for durable history (`data/logs/upload_log.csv`, `index.csv`).
- Keep secrets out of git (`config/youtube_secrets.json`, `config/token.json`, `.env` are ignored).
- Project documentation: `README.md` (user guide), `PRD.md` (requirements), `LOG.md` (change log), `docs/` (additional docs).

### Architecture Patterns

#### Backend Pipeline
- Modular pipeline: `scraper` (HTML fetch/parse) → `metadata` (title/description/tags) → `downloader` (yt-dlp HLS) → `uploader` (YouTube Data API) → `logger` (CSV log/index).
- Script entrypoints live under `scripts/` (e.g., `scripts/main.py`, `scripts/build_anagrafica.py`, `scripts/extract_odg_data.sh`, `scripts/generate_digests.sh`, `scripts/run_daily.sh`).
- Document extraction: scraper extracts 4 document types from seduta pages (OdG, resoconto provvisorio/stenografico, allegato) via pattern matching on HTML labels; maintains backward-compatible `resoconto_url` field (prefers stenographic over provisional).
- OdG extraction pipeline: `extract_odg_data.sh` uses `markitdown` (PDF→text) + `llm` (text→JSON) to extract legislative bills from agenda PDFs; outputs to `data/disegni_legge.jsonl` with deduplication.
- Video digest generation: `generate_digests.sh` downloads transcripts via `qv`, generates structured summaries using `llm` with JSON schema validation, and skips videos without spoken content (<100 bytes transcript) by marking them in anagrafica CSV.
- Duration tracking: video length extracted from yt-dlp metadata during download and stored in `duration_minutes` column; backfill script uses YouTube Data API for already-uploaded videos.
- Maintenance tools: `scripts/update_descriptions.py` for bulk YouTube metadata updates; supports dry-run mode.
- RSS feed generation via `scripts/generate_rss.py`, published by GitHub Actions.
- Configuration-driven behavior via `config/config.yaml`; defaults target seduta 219 (10/12/2025) onward.
- Idempotency: skip uploads already logged as `success`; incremental crawler (`build_anagrafica.py`) updates `data/anagrafica_video.csv` and stops when no future sedute; OdG extraction tracks processed PDFs; digest generation skips existing JSONs and videos marked `no_transcript=true`.
- Shell automation (`run_daily.sh`) uses `set -euo pipefail` and lock file to prevent concurrent runs.

#### Frontend Website
- Static site architecture: Astro generates HTML at build time from data files; no runtime server required.
- File-based routing: pages under `src/pages/` map to URLs (e.g., `src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].astro` → `/sedute/2025/12/16/seduta-220/video-1137/`).
- Data flow: `scripts/build-data.mjs` (prebuild step) aggregates CSV/JSONL/digest JSON into consolidated `src/data/processed/*.json` files; Astro pages import these at build time via `data-loader.ts`.
- Component structure: reusable Astro components in `src/components/` (layout, sedute, UI); layouts in `src/layouts/` (BaseLayout, PageLayout).
- Video page navigation: prev/next buttons allow sequential navigation between videos of same seduta without returning to seduta overview; buttons disabled (grayed) at boundaries; chronological order based on `dataVideo` + `oraVideo`.
- SEO: sitemap.xml auto-generated, RSS feed for latest sedute, Schema.org VideoObject structured data on video pages, OpenGraph tags.
- Accessibility: skip links, semantic HTML, ARIA labels, keyboard navigation support.
- Styling: Tailwind utility classes; Tailwind Typography for digest content rendering.

### Testing Strategy
- Manual smoke scripts: `scripts/tests/test_youtube_auth.py` / `scripts/tests/test_youtube_auth_manual.py` to validate OAuth tokens and quota.
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
- Seduta documents: 4 types extracted (OdG e Comunicazioni, Resoconto provvisorio, Resoconto stenografico, Allegato alla seduta); HTML pattern `<h3>Label<a href>` uniform across all types.
- YouTube metadata pattern: title `Lavori d'aula: seduta n. {numero} del {data} - {ora}`; description includes all available documents (OdG, resoconto provvisorio/stenografico, allegato) with emoji indicators and seduta URL; tags add base list + seduta number/year/month.
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
- GitHub Pages for hosting the public RSS feed (`feed.xml`, published from `gh-pages`).
