# Note di gestione problemi di deployment

## Errore: Pages deployment già in corso
**Sintomo**
- Nel log del job `actions/deploy-pages@v4` compare: `Deployment request failed ... due to in progress deployment. Please cancel <id> first or wait for it to complete.`

**Causa**
- GitHub Pages non accetta un nuovo deployment finché quello precedente è ancora `in progress`.

**Soluzione rapida (CLI)**
1) Annulla il deployment in corso (usa l'ID riportato nel log)
```
gh api -X POST repos/<OWNER>/<REPO>/pages/deployments/<ID>/cancel
```
2) Rilancia il workflow fallito
```
gh run rerun <RUN_ID> --failed
```

**Soluzione da UI**
1) Actions → apri il run in corso → annulla il job di deploy
2) Rilancia il run fallito

**Prevenzione**
- Aggiungere `concurrency` al workflow di deploy per evitare sovrapposizioni.

Esempio:
```yaml
concurrency:
  group: pages
  cancel-in-progress: true
```

## Comandi utili (gh)
- Elenco ultimi run
```
gh run list --limit 5
```
- Dettaglio ultimo run
```
gh run list --limit 1 --json databaseId,workflowName,displayTitle,conclusion,status,event
```
