## Implementation
- [x] 1.1 Introdurre un helper (Python) per scaricare caption via YouTube API dato `youtube_id`, con OAuth da `config/youtube_secrets.json` + `config/token.json`.
- [x] 1.2 Aggiornare `scripts/download_transcripts.sh` per usare l'helper API al posto di `yt-dlp`, mantenendo naming file e logica di skip esistente.
- [x] 1.3 Garantire output invariato: salvataggio `.it.srt` e derivazione `.it.txt` nello stesso formato attuale.
- [x] 1.4 Gestire assenza caption (o lingua italiana non disponibile) segnando il video in `data/trascrizioni/no_transcript.txt` senza interrompere il batch.
- [x] 1.5 Aggiornare la documentazione operativa (`README.md` e/o `scripts/README.md`) sui nuovi prerequisiti (OAuth YouTube API per trascrizioni).
- [x] 1.6 Validare con un test manuale su almeno un video con caption e uno senza caption, verificando output file e summary script.
