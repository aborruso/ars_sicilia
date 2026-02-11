<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## Script Creation Guidelines

- Always resolve paths from repo root, not the current working directory.
- Use `REPO_ROOT = Path(__file__).resolve().parents[1]` (or `.parents[2]` for `scripts/archive`) and build config/data paths from it.
- Avoid hard-coded relative paths like `./config/config.yaml` or `data/playlists.json`.

## Utility Scripts

- `scripts/run_transcripts_and_digests.sh`: esegue in sequenza `git pull`, `scripts/download_transcripts.sh` e `scripts/generate_digests.sh` per aggiornare trascrizioni e digest con un solo comando.
