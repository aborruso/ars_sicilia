---
type: Pipeline
title: Acquisizione sedute e upload video
description: Crawler incrementale delle sedute ARS e caricamento dei video su YouTube.
tags: [pipeline, python, youtube]
timestamp: 2026-07-07T00:00:00Z
---

# Crawler sedute

`scripts/build_anagrafica.py` — crawler incrementale che popola
`data/anagrafica_video.csv` a partire dal sito ARS. Gira quotidianamente
via GitHub Actions (workflow "Daily ARS uploads").

# Upload YouTube

`scripts/upload_single.py` — carica i video su YouTube via OAuth. Fino a
~4 video/giorno nel workflow schedulato, per restare dentro le quote
dell'API YouTube. Privacy dei video impostata su "non in elenco"
(unlisted).

`scripts/auth_captions.py` / `scripts/get_auth_url.py` /
`scripts/complete_auth.py` — gestione del flusso OAuth (token in
`config/token.json`, secrets in `config/youtube_secrets.json` — non
committati).

# Trigger e commit

Il workflow schedulato committa `anagrafica_video.csv` aggiornato usando
un PAT (`WORKFLOW_PAT`) proprio perché un push a `data/**` deve poter
innescare a sua volta il deploy del sito (un `GITHUB_TOKEN` di default
non ritriggererebbe altri workflow).

# Vedi anche

* [Trascrizioni e digest](trascrizioni-digest.md) — il passo successivo per ogni video caricato
* [CI/CD](/wiki/ci-cd/index.md)
