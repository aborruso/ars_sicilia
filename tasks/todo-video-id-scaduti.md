# Task: download dei video con id pagina ARS scaduto

## Problema

L'id della pagina video ARS (`/agenda/seduta/aula/video/<id>`) cambia ogni giorno. Una pagina con id vecchio risponde 200 ma con `<source src="">`, e `yt-dlp` fallisce con "Unsupported URL".

- Seduta 271 in anagrafica: `2876870` (9/9), `2878715`, `2880560`, `2881790`, `2883635` (13/9 notte); sul sito il 13/9 alle 12 è `2884250`. Due richieste a pochi secondi di distanza danno lo stesso id.
- Il crawler notturno rinfresca gli id delle sedute recenti e `daily_upload` scarica subito dopo: per le sedute nuove funziona.
- Si rompe il download di un video il cui id è vecchio: recuperi, nuovi tentativi, arretrati oltre il limite di 4 al giorno. Caso concreto: seduta 244, id `2675426` fermo ad aprile.
- Con l'id attuale (`2884212`, dalla pagina della seduta) la 244 espone `18.244.20260415.150319.mp4/playlist.m3u8`: 1162 segmenti, 195 minuti, uguale a `duration_minutes`.

## Piano

### Fase 1 - Risolvere l'URL attuale della pagina video

- [ ] In `src/scraper.py`, funzione `resolve_current_video_page_url(url_pagina, ora_video, data_video)`: scarica la pagina della seduta con `get_seduta_page`, prende i video con `find_video_elements` + `extract_video_metadata` e restituisce il `video_page_url` con stessa `ora_video` (e `data_video`, se presente). `None` se non trova corrispondenza. Riusa il parsing esistente, nessuna logica nuova di scraping.
  → verify: sulle sedute 244 e 271 restituisce una pagina il cui `<source src>` non è vuoto; su un orario inesistente restituisce `None`.

### Fase 2 - Usarlo in `upload_single.py` prima del download

- [ ] Prima di `downloader.download_video`, chiamare la funzione e scaricare dall'URL risolto. Se la risoluzione fallisce, si usa `video_page_url` dell'anagrafica come oggi e si logga il fallback.
- [ ] L'anagrafica non cambia: `id_video` resta la chiave con cui `update_anagrafica_youtube_id` ritrova la riga.
  → verify: `yt-dlp --simulate` sull'URL risolto della 244 trova il formato HLS; `bash`/`python` senza errori di sintassi.

### Fase 3 - Ricaricare la seduta 244 via CI

- [ ] Svuotare `youtube_id` e `status` della 244 in anagrafica (solo quella riga, CRLF preservati) e toglierla da `video_not_found.txt`; push; `workflow_dispatch` di `daily_upload`.
  → verify: nel log download completato e YouTube ID nuovo; in anagrafica la riga ha il nuovo `youtube_id` con `status=success`; `videos.list` sul nuovo id restituisce il video.
- [ ] Se fallisce: ripristinare subito la riga (altrimenti la 244 `failed` viene scelta per prima ogni notte e ferma il ciclo di upload).

### Fase 4 - Chiusura

- [ ] Voce in `LOG.md`; sezione di review qui sotto.

## Domande aperte

- Nessuna bloccante. Da decidere dopo: la trascrizione e il digest della 244 arriveranno col run notturno di `transcripts_digests`, oppure li lanciamo a mano dopo l'upload?

## Review

