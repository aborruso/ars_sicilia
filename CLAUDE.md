
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
