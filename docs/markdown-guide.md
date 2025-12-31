# Guida Markdown per le pagine statiche

Questa guida spiega come creare nuove pagine in Markdown per il sito Astro.

## Dove mettere i file

- Inserisci i file in `src/pages/`.
- Il percorso del file diventa la rotta del sito.
  - `src/pages/faq.md` → `/ars_sicilia/faq/`
  - `src/pages/privacy.md` → `/ars_sicilia/privacy/`

## Frontmatter richiesto

Ogni pagina deve avere un frontmatter con `title` e `description`:

```yaml
---
title: "Titolo della pagina"
description: "Breve descrizione per SEO e social"
---
```

## Template base

```markdown
---
title: "Titolo della pagina"
description: "Breve descrizione per SEO e social"
---

<article class="prose prose-gray max-w-none">

# Titolo della pagina

Testo introduttivo.

## Sezione

- Punto uno
- Punto due

</article>
```

## Sintassi Markdown utile

- **Grassetto**: `**testo**`
- *Corsivo*: `*testo*`
- Link: `[testo](https://esempio.it)`
- Liste ordinate:
  1. Primo
  2. Secondo

## Note

- Le pagine Markdown usano automaticamente il layout principale.
- Per link esterni con `target="_blank"`, usa HTML:

```html
<a href="https://esempio.it" target="_blank" rel="noopener noreferrer">Testo</a>
```
