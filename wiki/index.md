---
okf_version: "0.1"
---

# ARS Sicilia — Wiki di progetto

Documentazione tecnica del progetto, organizzata per concetti secondo la
convenzione OKF (Open Knowledge Format, mirrorata in
`/home/aborruso/git/ai-specs/specs/okf/`) — un file markdown per concetto,
con frontmatter minimale, pensata per essere letta sia da persone che da
agenti IA. Non contiene credenziali, token o URL riservati: per quelli,
vedi la configurazione locale (`wrangler.toml`, secrets di GitHub Actions,
`config/`).

Scopo: mantenere un quadro sempre aggiornato di come il progetto è fatto,
perché certe scelte sono state prese, e come farlo evolvere.

# Sezioni

* [Architettura](architettura/) - i tre livelli del sistema (backend, dati, frontend) e il contratto dati che li collega
* [Pipeline di acquisizione](pipeline/) - come nascono i dati: crawler sedute, upload YouTube, trascrizioni, digest AI, disegni di legge
* [Frontend](frontend/) - il sito Astro: routing, layout, data loader
* [Ricerca nelle trascrizioni](ricerca-trascrizioni/) - la feature sperimentale di ricerca semantica basata su Cloudflare AI Search
* [CI/CD](ci-cd/) - i workflow GitHub Actions che orchestrano tutto
* [Decisioni](decisioni/) - scelte architetturali rilevanti e il perché

# Come mantenerlo

* Un concetto nuovo → un nuovo file `.md` con frontmatter `type`, `title`, `description`.
* Una scelta architetturale rilevante → una voce in [decisioni/](decisioni/).
* Un cambiamento di rilievo → una riga in [log.md](log.md).
* Nessun segreto qui dentro: se un dato serve ma è sensibile, descrivi *dove* si trova, non il suo valore.
