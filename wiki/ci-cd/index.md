---
type: Workflow CI
title: Workflow GitHub Actions
description: I workflow schedulati che orchestrano crawling, upload, trascrizioni, digest, corpus RAG e deploy.
tags: [ci-cd, github-actions]
timestamp: 2026-07-07T00:00:00Z
---

# Workflow attivi (`.github/workflows/`)

| Workflow | Trigger | Cosa fa |
|---|---|---|
| `daily_upload.yml` | Schedulato (01:37 UTC) | Crawla nuove sedute, carica fino a ~4 video/giorno su YouTube, committa `anagrafica_video.csv` |
| `extract_odg.yml` | Schedulato (03:47 UTC) | Estrae i disegni di legge dai PDF OdG → `disegni_legge.jsonl` |
| `transcripts_digests.yml` | Schedulato (04:30 UTC) | Scarica trascrizioni (API YouTube), genera digest AI, **rigenera e sincronizza il corpus RAG** su Cloudflare AI Search, committa tutto |
| `publish_rss.yml` | Schedulato (02:17 UTC) | Rigenera il feed RSS |
| `deploy-site.yml` | Push su `main` che tocca `data/**`, `src/**`, `build-data.mjs` o config | Build Astro + deploy su GitHub Pages |
| `sync_viewer.yml` | Push su `main` (branch specifico) | Sync di un viewer verso `gh-pages` |

Ordine di esecuzione notturno: crawler (01:37) → estrazione OdG (03:47) →
trascrizioni/digest/corpus RAG (04:30). Ogni push a `data/**` fatto da
questi workflow innesca a sua volta `deploy-site.yml`.

# Perché un PAT (`WORKFLOW_PAT`) invece del token di default

I workflow che committano su `data/` usano `secrets.WORKFLOW_PAT` in
checkout invece del `GITHUB_TOKEN` di default: un push fatto con il
token di default non ritriggererebbe altri workflow (limite di
sicurezza di GitHub Actions), mentre serve che il push inneschi il
deploy del sito.

# Secret richiesti

| Secret | Usato da | Scopo |
|---|---|---|
| `WORKFLOW_PAT` | tutti i workflow che committano | Push che ritriggera altri workflow |
| `YOUTUBE_CLIENT_ID` / `_SECRET` / `_REFRESH_TOKEN` | daily_upload, transcripts_digests | OAuth YouTube (upload, caption) |
| `GEMINI_API_KEY` | transcripts_digests | Generazione digest (`llm` + Gemini 2.5 Flash) |
| `CLOUDFLARE_API_TOKEN` | transcripts_digests | Upload su R2 (`wrangler r2 object put`) + trigger sync AI Search. Permessi: Workers Edit + R2 Edit + AI Search Edit/Run |
| `CLOUDFLARE_ACCOUNT_ID` | transcripts_digests | Endpoint API per il trigger di sync AI Search |

# Vedi anche

* [Pipeline di acquisizione](/wiki/pipeline/index.md)
* [Ricerca nelle trascrizioni](/wiki/ricerca-trascrizioni/architettura.md)
