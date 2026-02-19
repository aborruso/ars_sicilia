
## Script Creation Guidelines

- Always resolve paths from repo root, not the current working directory.
- Use `REPO_ROOT = Path(__file__).resolve().parents[1]` (or `.parents[2]` for `scripts/archive`) and build config/data paths from it.
- Avoid hard-coded relative paths like `./config/config.yaml` or `data/playlists.json`.
- Nota operativa (CLI): per evitare espansioni indesiderate con caratteri speciali come `` ` ``, `$`, `(`, `)`, usare `gh issue comment --body-file` oppure un heredoc quotato con `<<'EOF'`.

## Utility Scripts

- `scripts/run_transcripts_and_digests.sh`: esegue in sequenza `git pull`, `scripts/download_transcripts.sh` e `scripts/generate_digests.sh` per aggiornare trascrizioni e digest con un solo comando.
