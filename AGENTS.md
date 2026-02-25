
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
