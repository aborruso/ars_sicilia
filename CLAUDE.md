# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Civic-tech platform that makes the sessions of the Sicilian Regional Assembly (ARS) consultable. It crawls session metadata, uploads session videos to YouTube, generates AI digests from transcripts, extracts draft laws (disegni di legge) from agenda PDFs, and publishes a static Astro site to GitHub Pages.

The system has three layers that meet through the `data/` directory:

- **Backend (Python, `scripts/`)** — acquisition/publication pipeline. Writes datasets into `data/`.
- **Data layer (`data/`)** — public open datasets, the contract between backend and frontend.
- **Frontend (Astro, `src/`)** — static site generated at build time from `data/`.

## Architecture

The build is **data-driven**: `scripts/build-data.mjs` runs as Astro's `prebuild` hook. It reads the raw datasets and emits aggregated JSON into `src/data/processed/`, which the Astro pages consume. Editing `data/` is not enough to see changes locally — `prebuild` must regenerate the processed JSON.

Data flow:

1. `data/anagrafica_video.csv` — session/video metadata (one row per video; sessions aggregate rows by `numero_seduta` + `data_seduta`).
2. `data/disegni_legge.jsonl` — draft laws extracted from agenda (OdG) PDFs.
3. `data/digest/{youtube_id}.json` — per-video AI digests (digests with body ≤10 chars are dropped as empty).
4. `build-data.mjs` joins these → `src/data/processed/{sedute,videos,ddls,categories}.json`.
5. Astro renders pages from the processed JSON; `src/lib/data-loader.ts` is the typed loader.

Astro config (`astro.config.mjs`): static output, `site: https://aborruso.github.io`, `base: /ars_sicilia` — all internal links must respect the base path. Markdown pages in `src/pages/` get a default layout via the `remark-default-layout.mjs` remark plugin.

`ars_sicilia_api/` is a standalone Python client for the ARS legislative search API — independent of the site build, with its own README and OpenSpec.

## Common Commands

Frontend (run from repo root):

```bash
npm install            # install deps
npm run dev            # prebuild (build-data.mjs) + astro dev → http://localhost:4321
npm run build          # prebuild + astro build → dist/
npm run preview        # preview built site
node scripts/build-data.mjs   # regenerate src/data/processed/ only
```

Backend pipeline (Python; use `.venv`):

```bash
python3 -m venv .venv && source .venv/bin/activate && pip3 install -r requirements.txt
python3 scripts/build_anagrafica.py     # incremental crawler → anagrafica_video.csv
python3 scripts/upload_single.py --dry-run   # YouTube upload (OAuth)
./scripts/extract_odg_data.sh           # draft laws from OdG PDFs → disegni_legge.jsonl
./scripts/run_transcripts_and_digests.sh   # git pull + download transcripts + generate digests
```

The digest pipeline (`generate_digests.sh`) requires external CLIs: `qv` (transcripts), `llm` (Gemini 2.5 Flash), `mlr`. Transcript download + digest generation run **manually/locally** (OAuth not available in CI). See `scripts/README.md` for the full script catalog.

Backend tests live in `scripts/tests/` (YouTube auth smoke tests) — run a single one with `python3 scripts/tests/test_youtube_auth.py`.

## CI / Deploy

GitHub Actions run nightly and on push:

- `deploy-site.yml` — on push to `main` touching `data/**`, `src/**`, `build-data.mjs`, or config → builds and deploys to GitHub Pages.
- `daily_upload.yml` — crawls sessions, uploads up to ~4 videos/day, commits `anagrafica_video.csv` (triggers deploy via `WORKFLOW_PAT`).
- `extract_odg.yml` — extracts draft laws nightly.
- `publish_rss.yml` — regenerates the RSS feed.

A push to `data/` triggers the deploy, so committing new digests/transcripts is enough to publish.

## Working with OpenSpec

### Quick Start: Creating a Change Proposal

1. **Create change directory** and scaffold files:
   ```bash
   mkdir -p openspec/changes/my-change-id
   ```

2. **Create 3 essential files**:
   - `proposal.md` — What & why (REQUIRED)
   - `specs/my-capability/spec.md` — Technical requirements (REQUIRED)
   - `tasks.md` — Work breakdown (REQUIRED)

3. **Proposal Format** (`proposal.md`):
   ```markdown
   # Change: my-change-id

   ## Why
   [1-2 sentences on problem/opportunity]

   ## What Changes
   - [Bullet list of changes]
   - [Mark breaking changes with **BREAKING**]

   ## Impact
   - Affected specs: [list capabilities]
   - Affected code: [key files/systems]
   ```

4. **Spec Format** (`specs/capability-name/spec.md`):
   - Header with purpose (one line)
   - Sections: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`
   - Each requirement:
     - Header: `### Requirement: unique-id`
     - Body: **MUST contain `SHALL` or `MUST`** (RFC 2119 keywords)
     - Scenarios: `#### Scenario: description` (at least one per requirement)

5. **Validate**:
   ```bash
   openspec validate my-change-id --strict
   ```

### Minimal Valid Spec Structure

```markdown
# Spec: my-capability

Brief purpose statement.

## ADDED Requirements

### Requirement: my-requirement

The system MUST do [requirement]. (Note: must include SHALL or MUST)

#### Scenario: description of specific case

Concrete user story showing the requirement in action.
```

### Common Commands

- `openspec list` — List all active changes
- `openspec show my-change-id` — Inspect change details
- `openspec validate my-change-id --strict` — Validate (must pass before proposing)
- `openspec apply my-change-id` — Apply approved change to specs/

### Key Rules

1. **Every requirement MUST include SHALL or MUST** (validation requirement)
2. **Every requirement MUST have at least one Scenario** (concrete example)
3. **Use `### Requirement:` header** for requirement definitions (not `####`)
4. **Use `#### Scenario:` header** for scenario examples (under requirement)
5. **Cross-reference related specs** at end of spec file
6. **Keep tasks small and verifiable** — one task = one user-visible change

## Script Creation Guidelines

- Always resolve paths from repo root, not the current working directory.
- Use `REPO_ROOT = Path(__file__).resolve().parents[1]` (or `.parents[2]` for `scripts/archive`) and build config/data paths from it.
- Avoid hard-coded relative paths like `./config/config.yaml` or `data/playlists.json`.
- Nota operativa (CLI): per evitare espansioni indesiderate con caratteri speciali come `` ` ``, `$`, `(`, `)`, usare `gh issue comment --body-file` oppure un heredoc quotato con `<<'EOF'`.
- Per preservare i ritorni a capo in Markdown, non passare testo multilinea direttamente a `--body "..."`
  con `\n`: si rischia di avere `\n` letterali.
- Flusso consigliato: scrivere il contenuto in un file (o heredoc quotato) e poi usare `--body-file`.
  Esempio:
  ```bash
  cat > /tmp/comment.md <<'EOF'
  Riga 1
  
  - bullet con `codice`
  - altra riga
  EOF
  gh issue comment 123 --body-file /tmp/comment.md
  ```

## Utility Scripts

- `scripts/run_transcripts_and_digests.sh`: esegue in sequenza `git pull`, `scripts/download_transcripts.sh` e `scripts/generate_digests.sh` per aggiornare trascrizioni e digest con un solo comando.
